from datetime import datetime, time
import os
import json

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, send_from_directory, jsonify
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.utils import secure_filename

from astro_utils import (
    compute_target_window,
    build_default_plan_json,
)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

# --- Database config (SQLite by default, override with DATABASE_URL) ---------
db_url = os.environ.get("DATABASE_URL") or \
         "sqlite:///" + os.path.join(BASE_DIR, "astroplanner.db")
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# --- Uploads config ---------------------------------------------------------
UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER") or os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB


# ---------------------------------------------------------------------------
# MODELS
# ---------------------------------------------------------------------------

class Target(db.Model):
    __tablename__ = "targets"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    catalog_id = db.Column(db.String(64))
    target_type = db.Column(db.String(64))  # emission, reflection, galaxy, etc.

    # RA in decimal hours, Dec in decimal degrees
    ra_hours = db.Column(db.Float, nullable=False)
    dec_deg = db.Column(db.Float, nullable=False)

    notes = db.Column(db.Text)
    pixinsight_workflow = db.Column(db.Text)

    preferred_palette = db.Column(db.String(64), default="SHO")
    packup_time_local = db.Column(db.String(5), default="01:00")  # "HH:MM"

    final_image_filename = db.Column(db.String(255))

    plans = relationship("TargetPlan", back_populates="target",
                         cascade="all, delete-orphan")
    sessions = relationship("ImagingSession", back_populates="target",
                            cascade="all, delete-orphan")


class TargetPlan(db.Model):
    __tablename__ = "target_plans"

    id = db.Column(db.Integer, primary_key=True)
    target_id = db.Column(db.Integer, db.ForeignKey("targets.id"), nullable=False)
    palette_name = db.Column(db.String(64), nullable=False)

    # JSON string:
    # {
    #   "channels": [
    #       {"name": "H", "label": "Ha", "weight": 0.5,
    #        "weight_fraction": 0.5, "planned_minutes": 180},
    #       ...
    #   ],
    #   "dominant_channel": "H",
    #   "total_planned_minutes": 360,
    #   "palette": "SHO"
    # }
    plan_json = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    target = relationship("Target", back_populates="plans")


class ImagingSession(db.Model):
    __tablename__ = "imaging_sessions"

    id = db.Column(db.Integer, primary_key=True)
    target_id = db.Column(db.Integer, db.ForeignKey("targets.id"), nullable=False)

    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    channel = db.Column(db.String(16), nullable=False)  # H, O, S, L, R, G, B
    sub_exposure_seconds = db.Column(db.Integer, nullable=False)
    sub_count = db.Column(db.Integer, nullable=False)

    notes = db.Column(db.Text)

    target = relationship("Target", back_populates="sessions")


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def parse_time_str(tstr, default="01:00") -> time:
    """Parse 'HH:MM' into a time object; fall back if invalid."""
    try:
        h, m = map(int, tstr.split(":"))
        return time(hour=h, minute=m)
    except Exception:
        dh, dm = map(int, default.split(":"))
        return time(hour=dh, minute=dm)


# ---------------------------------------------------------------------------
# ROUTES
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    from collections import defaultdict

    targets = Target.query.order_by(Target.name).all()

    # Observer location from env (defaults to Riyadh)
    lat = float(os.environ.get("OBSERVER_LAT", "24.7136"))
    lon = float(os.environ.get("OBSERVER_LON", "46.6753"))
    elev = float(os.environ.get("OBSERVER_ELEV_M", "600"))

    summaries = []

    for t in targets:
        # Latest plan for current preferred palette
        plan = (
            TargetPlan.query
            .filter_by(target_id=t.id, palette_name=t.preferred_palette)
            .order_by(TargetPlan.created_at.desc())
            .first()
        )

        if plan:
            plan_data = json.loads(plan.plan_json)
            planned_total = float(plan_data.get("total_planned_minutes", 0) or 0)
            channels = plan_data.get("channels", [])
        else:
            plan_data = None
            planned_total = 0.0
            channels = []

        # Progress: accumulate per-channel & total
        total_seconds = 0.0
        per_channel_seconds = defaultdict(float)

        for s in t.sessions:
            secs = s.sub_exposure_seconds * s.sub_count
            total_seconds += secs
            per_channel_seconds[s.channel] += secs

        done_minutes = total_seconds / 60.0
        remaining_minutes = max(planned_total - done_minutes, 0.0)

        # Suggested channel = one with largest remaining seconds
        suggested_channel = None
        suggested_label = None
        max_remaining_ch_sec = -1.0

        for ch in channels:
            name = ch.get("name")
            label = ch.get("label", name)
            ch_planned_min = float(ch.get("planned_minutes", 0) or 0)
            planned_sec = ch_planned_min * 60.0
            done_sec = per_channel_seconds.get(name, 0.0)
            rem_sec = max(planned_sec - done_sec, 0.0)
            if rem_sec > max_remaining_ch_sec:
                max_remaining_ch_sec = rem_sec
                suggested_channel = name
                suggested_label = label

        # Tonight's window for this target
        packup_time = parse_time_str(t.packup_time_local)
        window_info = compute_target_window(
            ra_hours=t.ra_hours,
            dec_deg=t.dec_deg,
            latitude_deg=lat,
            longitude_deg=lon,
            elevation_m=elev,
            packup_time_local=packup_time,
        )

        if window_info.get("deps_available"):
            window_minutes = float(window_info.get("total_minutes") or 0.0)
        else:
            window_minutes = 0.0

        # Best you can realistically do tonight for this target
        best_tonight_minutes = min(window_minutes, remaining_minutes) if remaining_minutes > 0 else 0.0

        # Basic ratios (we'll normalize later too)
        if planned_total > 0:
            completion_ratio = done_minutes / planned_total
            remaining_ratio = remaining_minutes / planned_total
        else:
            completion_ratio = 0.0
            remaining_ratio = 0.0

        # Window fit: how much of remaining can tonight cover (capped at 1.0)
        if remaining_minutes > 0:
            window_fit_ratio = min(1.0, window_minutes / remaining_minutes)
            tonight_completion_fraction = best_tonight_minutes / remaining_minutes
        else:
            window_fit_ratio = 0.0
            tonight_completion_fraction = 0.0

        summaries.append({
            "target": t,
            "plan_data": plan_data,
            "planned_total": round(planned_total, 1),
            "done_total": round(done_minutes, 1),
            "remaining_total": round(remaining_minutes, 1),
            "window_minutes": round(window_minutes, 1),
            "best_tonight_minutes": round(best_tonight_minutes, 1),
            "suggested_channel": suggested_channel,
            "suggested_channel_label": suggested_label,
            "completion_ratio_raw": completion_ratio,
            "remaining_ratio_raw": remaining_ratio,
            "window_fit_ratio_raw": window_fit_ratio,
            "tonight_completion_fraction_raw": tonight_completion_fraction,
        })

    # Second pass: normalize across all targets & compute a priority score
    # Only consider targets that have a plan and some remaining time.
    active = [s for s in summaries if s["planned_total"] > 0 and s["remaining_total"] > 0]

    if active:
        max_remaining = max(s["remaining_total"] for s in active) or 1.0

        for s in active:
            remaining_total = s["remaining_total"]

            # 1 - remaining/ max_remaining  ->  high if this target has less remaining than others
            remaining_rel = 1.0 - (remaining_total / max_remaining)

            completion_ratio = s["completion_ratio_raw"]
            window_fit_ratio = s["window_fit_ratio_raw"]
            tonight_completion_fraction = s["tonight_completion_fraction_raw"]

            # Priority score (0–1-ish): favor almost-finished & finishable tonight
            priority_score = (
                0.35 * completion_ratio +
                0.25 * window_fit_ratio +
                0.20 * remaining_rel +
                0.20 * tonight_completion_fraction
            )

            s["priority_score"] = round(priority_score, 3)
            s["completion_pct"] = round(completion_ratio * 100, 1)
        # Non-active targets: set score to 0
        for s in summaries:
            if s not in active:
                s["priority_score"] = 0.0
                s["completion_pct"] = 0.0
    else:
        for s in summaries:
            s["priority_score"] = 0.0
            s["completion_pct"] = 0.0

    # Tonight's pick = highest priority_score among active
    tonight_pick = None
    if active:
        tonight_pick = max(active, key=lambda s: s["priority_score"])

    return render_template(
        "index.html",
        target_summaries=summaries,
        tonight_pick=tonight_pick,
    )


@app.route("/target/new", methods=["GET", "POST"])
def new_target():
    if request.method == "POST":
        name = request.form.get("name")
        catalog_id = request.form.get("catalog_id") or None
        target_type = request.form.get("target_type") or None
        ra_hours = float(request.form.get("ra_hours"))
        dec_deg = float(request.form.get("dec_deg"))
        preferred_palette = request.form.get("preferred_palette") or "SHO"
        packup_time_local = request.form.get("packup_time_local") or "01:00"

        target = Target(
            name=name,
            catalog_id=catalog_id,
            target_type=target_type,
            ra_hours=ra_hours,
            dec_deg=dec_deg,
            preferred_palette=preferred_palette,
            packup_time_local=packup_time_local,
        )
        db.session.add(target)
        db.session.commit()

        # Initial plan guess
        plan_json = build_default_plan_json(
            target_type=target_type,
            palette=preferred_palette,
            bortle=9,
        )
        plan = TargetPlan(
            target_id=target.id,
            palette_name=preferred_palette,
            plan_json=plan_json,
        )
        db.session.add(plan)
        db.session.commit()

        flash("Target created.", "success")
        return redirect(url_for("target_detail", target_id=target.id))

    return render_template("target_form.html", target=None)


@app.route("/target/<int:target_id>")
def target_detail(target_id):
    target = Target.query.get_or_404(target_id)

    # Latest plan for current preferred palette
    plan = (
        TargetPlan.query
        .filter_by(target_id=target.id, palette_name=target.preferred_palette)
        .order_by(TargetPlan.created_at.desc())
        .first()
    )
    plan_data = json.loads(plan.plan_json) if plan else None

    # Observer location from env (defaults to Riyadh)
    lat = float(os.environ.get("OBSERVER_LAT", "24.7136"))
    lon = float(os.environ.get("OBSERVER_LON", "46.6753"))
    elev = float(os.environ.get("OBSERVER_ELEV_M", "600"))
    packup_time = parse_time_str(target.packup_time_local)

    window_info = compute_target_window(
        ra_hours=target.ra_hours,
        dec_deg=target.dec_deg,
        latitude_deg=lat,
        longitude_deg=lon,
        elevation_m=elev,
        packup_time_local=packup_time,
    )

    # Progress: accumulate minutes and seconds per channel
    from collections import defaultdict
    progress_minutes = defaultdict(float)
    progress_seconds = defaultdict(float)

    for s in target.sessions:
        total_seconds = s.sub_exposure_seconds * s.sub_count
        progress_seconds[s.channel] += total_seconds
        progress_minutes[s.channel] += total_seconds / 60.0

    return render_template(
        "target_detail.html",
        target=target,
        plan=plan,
        plan_data=plan_data,
        window_info=window_info,
        progress_minutes=progress_minutes,
        progress_seconds=progress_seconds,
    )


@app.route("/target/<int:target_id>/delete", methods=["POST"])
def delete_target(target_id):
    target = Target.query.get_or_404(target_id)

    # Delete final image file if present
    if target.final_image_filename:
        upload_folder = app.config.get("UPLOAD_FOLDER", "uploads")
        img_path = os.path.join(upload_folder, target.final_image_filename)
        try:
            if os.path.exists(img_path):
                os.remove(img_path)
        except OSError:
            # Not fatal if we can't remove the file
            pass

    # Delete imaging sessions
    for s in list(target.sessions):
        db.session.delete(s)

    # Delete plans
    plans = TargetPlan.query.filter_by(target_id=target.id).all()
    for p in plans:
        db.session.delete(p)

    # Delete target itself
    db.session.delete(target)
    db.session.commit()

    flash(f"Target '{target.name}' and all associated data were deleted.", "success")
    return redirect(url_for("index"))


@app.route("/target/<int:target_id>/edit", methods=["GET", "POST"])
def edit_target(target_id):
    target = Target.query.get_or_404(target_id)

    if request.method == "POST":
        target.name = request.form.get("name")
        target.catalog_id = request.form.get("catalog_id") or None
        target.target_type = request.form.get("target_type") or None
        target.ra_hours = float(request.form.get("ra_hours"))
        target.dec_deg = float(request.form.get("dec_deg"))
        target.preferred_palette = request.form.get("preferred_palette") or target.preferred_palette
        target.packup_time_local = request.form.get("packup_time_local") or target.packup_time_local
        target.notes = request.form.get("notes")
        target.pixinsight_workflow = request.form.get("pixinsight_workflow")

        db.session.commit()
        flash("Target updated.", "success")
        return redirect(url_for("target_detail", target_id=target.id))

    return render_template("target_form.html", target=target)


@app.route("/target/<int:target_id>/plan/new", methods=["POST"])
def new_plan(target_id):
    target = Target.query.get_or_404(target_id)
    palette = request.form.get("palette") or target.preferred_palette

    target.preferred_palette = palette
    plan_json = build_default_plan_json(
        target_type=target.target_type,
        palette=palette,
        bortle=9,
    )
    plan = TargetPlan(
        target_id=target.id,
        palette_name=palette,
        plan_json=plan_json,
    )
    db.session.add(plan)
    db.session.commit()

    flash(f"New plan created for palette {palette}.", "success")
    return redirect(url_for("target_detail", target_id=target.id))


@app.route("/target/<int:target_id>/plan/update", methods=["POST"])
def update_plan(target_id):
    target = Target.query.get_or_404(target_id)

    # Get current plan for the preferred palette
    plan = (
        TargetPlan.query
        .filter_by(target_id=target.id, palette_name=target.preferred_palette)
        .order_by(TargetPlan.created_at.desc())
        .first()
    )
    if not plan:
        flash("No plan found to update.", "danger")
        return redirect(url_for("target_detail", target_id=target.id))

    data = json.loads(plan.plan_json)
    channels = data.get("channels", [])
    if not channels:
        flash("Plan JSON is missing channels.", "danger")
        return redirect(url_for("target_detail", target_id=target.id))

    # Original total (from plan or sum of channels)
    orig_total = data.get("total_planned_minutes")
    if not orig_total:
        orig_total = sum(float(c.get("planned_minutes", 0) or 0) for c in channels)

    # Ensure numeric planned_minutes and sub_exposure_seconds fields exist
    for c in channels:
        c["planned_minutes"] = float(c.get("planned_minutes", 0) or 0)
        if "sub_exposure_seconds" not in c or not c["sub_exposure_seconds"]:
            # Sensible default if missing, consistent with astro_utils
            n = c.get("name")
            if n in ("H", "O", "S"):
                c["sub_exposure_seconds"] = 300
            elif n == "L":
                c["sub_exposure_seconds"] = 180
            else:
                c["sub_exposure_seconds"] = 180

    # User-specified total
    form_total_raw = request.form.get("total_planned_minutes")
    new_total = None
    if form_total_raw:
        try:
            new_total = float(form_total_raw)
        except ValueError:
            new_total = None

    # If user provided a new total, rescale channels proportionally first
    if new_total and new_total > 0 and orig_total and orig_total > 0:
        scale = new_total / orig_total
        for c in channels:
            c["planned_minutes"] = round(c["planned_minutes"] * scale)

    # Then apply per-channel overrides from the form
    for c in channels:
        name = c.get("name")
        # Per-channel minutes override
        field_name = f"ch_{name}_minutes"
        field_val = request.form.get(field_name)
        if field_val is not None and field_val != "":
            try:
                mins = float(field_val)
                if mins >= 0:
                    c["planned_minutes"] = round(mins)
            except ValueError:
                pass  # ignore bad values, keep previous

        # Per-channel sub-exposure override
        sub_field = f"ch_{name}_subexp"
        sub_val = request.form.get(sub_field)
        if sub_val is not None and sub_val != "":
            try:
                sec = int(float(sub_val))
                if sec > 0:
                    c["sub_exposure_seconds"] = sec
            except ValueError:
                pass

    # Final total is sum of updated channels
    final_total = sum(c["planned_minutes"] for c in channels)

    # Recompute weights / fractions
    if final_total > 0:
        for c in channels:
            frac = c["planned_minutes"] / final_total
            c["weight_fraction"] = frac
            c["weight"] = frac
    else:
        for c in channels:
            c["weight_fraction"] = 0.0
            c["weight"] = 0.0

    data["channels"] = channels
    data["total_planned_minutes"] = round(final_total)

    # Dominant channel = one with max planned minutes
    if channels:
        dom = max(channels, key=lambda c: c.get("planned_minutes", 0))
        data["dominant_channel"] = dom.get("name", data.get("dominant_channel", ""))

    # Save back to plan
    plan.plan_json = json.dumps(data, indent=2)
    db.session.commit()

    flash("Plan updated.", "success")
    return redirect(url_for("target_detail", target_id=target.id))



@app.route("/target/<int:target_id>/progress/add", methods=["POST"])
def add_progress(target_id):
    target = Target.query.get_or_404(target_id)
    channel = request.form.get("channel").strip().upper()
    sub_exposure_seconds = int(request.form.get("sub_exposure_seconds"))
    sub_count = int(request.form.get("sub_count"))
    notes = request.form.get("notes")

    session = ImagingSession(
        target_id=target.id,
        channel=channel,
        sub_exposure_seconds=sub_exposure_seconds,
        sub_count=sub_count,
        notes=notes,
    )
    db.session.add(session)
    db.session.commit()

    flash("Progress added.", "success")
    return redirect(url_for("target_detail", target_id=target.id))


@app.route("/target/<int:target_id>/upload-final", methods=["POST"])
def upload_final_image(target_id):
    target = Target.query.get_or_404(target_id)
    file = request.files.get("final_image")
    if not file:
        flash("No file uploaded.", "danger")
        return redirect(url_for("target_detail", target_id=target.id))

    filename = secure_filename(file.filename)
    if not filename:
        flash("Invalid filename.", "danger")
        return redirect(url_for("target_detail", target_id=target.id))

    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)

    target.final_image_filename = filename
    db.session.commit()

    flash("Final image uploaded.", "success")
    return redirect(url_for("target_detail", target_id=target.id))


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/api/resolve", methods=["GET"])
def api_resolve():
    """Resolve an object name to RA/Dec via astro_utils.resolve_target_name."""
    name = (request.args.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Missing 'name' query parameter."}), 400

    from astro_utils import resolve_target_name

    try:
        ra_hours, dec_deg = resolve_target_name(name)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Unexpected errors
        return jsonify({"error": f"Resolution failed: {e}"}), 500

    return jsonify({
        "name": name,
        "ra_hours": ra_hours,
        "dec_deg": dec_deg,
    })



# ---------------------------------------------------------------------------
# CLI helper
# ---------------------------------------------------------------------------

@app.cli.command("init-db")
def init_db():
    """Initialize the database tables."""
    db.create_all()
    print("Database initialized.")


if __name__ == "__main__":
    # For local dev. In Docker/K8s use gunicorn or `flask run`.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
