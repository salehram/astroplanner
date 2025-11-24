from __future__ import annotations

import json
import math
import os
import datetime
from zoneinfo import ZoneInfo

try:
    from astropy.coordinates import SkyCoord, EarthLocation, AltAz, get_sun
    from astropy.time import Time
    import astropy.units as u
    from astroplan import Observer
    ASTRO_DEPS_AVAILABLE = True
except Exception:
    ASTRO_DEPS_AVAILABLE = False


def _fallback_window(note: str):
    return {
        "deps_available": False,
        "note": note,
        "sunset": None,
        "dark_start": None,
        "dark_end": None,
        "meridian_time": None,
        "start_time": None,
        "end_time": None,
        "total_minutes": None,
        "min_altitude_deg": None,
    }


def compute_target_window(
    ra_hours: float,
    dec_deg: float,
    latitude_deg: float,
    longitude_deg: float,
    elevation_m: float,
    packup_time_local: datetime.time | None,
    min_altitude_deg: float = 30.0,
):
    """
    Compute basic observing window info for tonight for the given target.

    Returns a dict with:
      deps_available: bool
      note: str (if deps not available)
      sunset_utc, sunset_local: str
      dark_start_utc, dark_start_local: str
      dark_end_utc, dark_end_local: str
      meridian_utc, meridian_local: str
      start_time_utc, start_time_local: str
      end_time_utc, end_time_local: str
      total_minutes: int | None
      min_altitude_deg: float
    """
    try:
        import astropy.units as u
        from astropy.time import Time
        from astropy.coordinates import SkyCoord, EarthLocation, AltAz, get_sun
        from astroplan import Observer
    except ImportError:
        return {
            "deps_available": False,
            "note": "Astropy/astroplan not installed in this environment.",
            "total_minutes": None,
        }

    # Local timezone from env or default to Riyadh
    tz_name = os.environ.get("OBSERVER_TZ", "Asia/Riyadh")
    try:
        local_tz = ZoneInfo(tz_name)
    except Exception:
        local_tz = datetime.timezone.utc
        tz_name = "UTC"

    # Observer location
    location = EarthLocation(
        lat=latitude_deg * u.deg,
        lon=longitude_deg * u.deg,
        height=elevation_m * u.m,
    )

    # "Now" in UTC for tonight’s calculations
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    t_now = Time(now_utc)

    # Astroplan observer (timezone can be string or tzinfo)
    observer = Observer(location=location, name="LocalObserver", timezone=tz_name)

    # Target coordinates
    coord = SkyCoord(ra=ra_hours * u.hourangle, dec=dec_deg * u.deg)

    # Helper to make UTC/local datetime pairs from astropy Time
    def time_pair(t: Time | None):
        if t is None:
            return None, None
        dt_utc = t.to_datetime(timezone=datetime.timezone.utc)
        dt_local = dt_utc.astimezone(local_tz)
        return dt_utc, dt_local

    # Compute sunset & nautical twilight for "tonight"
    try:
        sunset = observer.sun_set_time(t_now, which="nearest")
        dark_start = observer.twilight_evening_nautical(t_now, which="nearest")
        dark_end = observer.twilight_morning_nautical(t_now, which="next")
    except Exception:
        return {
            "deps_available": False,
            "note": "Could not compute sun/twilight times for this location/date.",
            "total_minutes": None,
        }

    # Target meridian transit time
    try:
        meridian_time = observer.target_meridian_transit_time(t_now, coord, which="nearest")
    except Exception:
        meridian_time = None

    sunset_utc, sunset_local = time_pair(sunset)
    dark_start_utc, dark_start_local = time_pair(dark_start)
    dark_end_utc, dark_end_local = time_pair(dark_end)
    meridian_utc, meridian_local = time_pair(meridian_time) if meridian_time is not None else (None, None)

    # If anything is missing, bail out gracefully
    if not (sunset_local and dark_start_local and dark_end_local):
        return {
            "deps_available": False,
            "note": "Insufficient data to compute night window.",
            "total_minutes": None,
        }

    # Determine local packup time as a datetime
    # We base "packup date" on the dark_start_local date and roll to next day if needed
    if packup_time_local:
        packup_dt_local = datetime.datetime.combine(
            dark_start_local.date(), packup_time_local, tzinfo=local_tz
        )
        # If packup time is earlier or equal to dark start (e.g. 01:00 after midnight),
        # move it to the next day.
        if packup_dt_local <= dark_start_local:
            packup_dt_local += datetime.timedelta(days=1)
    else:
        packup_dt_local = dark_end_local

    # Usable window start/end in LOCAL time (simple version: from dark start to min(dark_end, packup))
    start_local = dark_start_local
    end_local = min(dark_end_local, packup_dt_local)

    if end_local <= start_local:
        total_minutes = 0
    else:
        total_minutes = int(round((end_local - start_local).total_seconds() / 60.0))

    # Rough altitude at the midpoint of the window
    if end_local > start_local:
        mid_local = start_local + (end_local - start_local) / 2
        mid_utc = mid_local.astimezone(datetime.timezone.utc)
        t_mid = Time(mid_utc)
        altaz_mid = coord.transform_to(AltAz(obstime=t_mid, location=location))
        min_altitude_val = float(altaz_mid.alt.deg)
    else:
        min_altitude_val = float("nan")

    # Build UTC versions of start/end from local
    start_utc = start_local.astimezone(datetime.timezone.utc)
    end_utc = end_local.astimezone(datetime.timezone.utc)

    def fmt(dt: datetime.datetime | None):
        if not dt:
            return "N/A"
        # Full date+time, 24h
        return dt.strftime("%Y-%m-%d %H:%M")

    return {
        "deps_available": True,
        "note": "",
        "sunset_local": fmt(sunset_local),
        "sunset_utc": fmt(sunset_utc),
        "dark_start_local": fmt(dark_start_local),
        "dark_start_utc": fmt(dark_start_utc),
        "dark_end_local": fmt(dark_end_local),
        "dark_end_utc": fmt(dark_end_utc),
        "meridian_local": fmt(meridian_local),
        "meridian_utc": fmt(meridian_utc),
        "start_time_local": fmt(start_local),
        "start_time_utc": fmt(start_utc),
        "end_time_local": fmt(end_local),
        "end_time_utc": fmt(end_utc),
        "total_minutes": total_minutes,
        "min_altitude_deg": round(min_altitude_val, 1) if min_altitude_val == min_altitude_val else None,
    }


# ---------------------------------------------------------------------------
# Palette & exposure logic
# ---------------------------------------------------------------------------

# crude defaults you can tune later, in minutes of total integration
DEFAULT_TOTAL_MINUTES_BY_TYPE = {
    "emission": 600,   # 10h
    "diffuse": 480,
    "reflection": 420,
    "galaxy": 360,
    "cluster": 240,
}


def suggest_palette_and_exposures(target_type: str, palette: str, bortle: int = 9):
    """
    Heuristic exposure planner.

    Returns dict:
      {
        "channels": [
            {
              "name": "H", "label": "Ha",
              "weight": 0.5,
              "weight_fraction": 0.5,
              "planned_minutes": 180,
              "sub_exposure_seconds": 300
            },
            ...
        ],
        "dominant_channel": "H",
        "total_planned_minutes": 360,
        "per_channel_minutes": {"H": 180, "O": 110, ...},
        "palette": "SHO"
      }
    """
    ttype = (target_type or "").lower()
    base_total = DEFAULT_TOTAL_MINUTES_BY_TYPE.get(ttype, 420)

    # Bortle penalty – push longer total under bad skies
    if bortle >= 8:
        base_total *= 1.3
    elif bortle >= 6:
        base_total *= 1.1

    palette = (palette or "SHO").upper()

    if palette == "SHO":
        # Emission nebula – Ha usually king
        channels = [
            {"name": "H", "label": "Ha",   "weight": 0.5},
            {"name": "O", "label": "OIII", "weight": 0.3},
            {"name": "S", "label": "SII",  "weight": 0.2},
        ]
        dominant = "H"
    elif palette == "HOO":
        channels = [
            {"name": "H", "label": "Ha",   "weight": 0.6},
            {"name": "O", "label": "OIII", "weight": 0.4},
        ]
        dominant = "H"
    elif palette == "LRGB":
        channels = [
            {"name": "L", "label": "Luminance", "weight": 0.5},
            {"name": "R", "label": "Red",       "weight": 0.17},
            {"name": "G", "label": "Green",     "weight": 0.17},
            {"name": "B", "label": "Blue",      "weight": 0.16},
        ]
        dominant = "L"
    elif palette == "LRGBNB":
        # LRGB + a bit of Ha/OIII
        channels = [
            {"name": "L", "label": "Luminance", "weight": 0.4},
            {"name": "R", "label": "Red",       "weight": 0.12},
            {"name": "G", "label": "Green",     "weight": 0.12},
            {"name": "B", "label": "Blue",      "weight": 0.11},
            {"name": "H", "label": "Ha",        "weight": 0.15},
            {"name": "O", "label": "OIII",      "weight": 0.10},
        ]
        dominant = "L"
    else:
        # fallback – single luminance
        channels = [
            {"name": "L", "label": "Luminance", "weight": 1.0},
        ]
        dominant = "L"

    # Set default sub-exposures per channel (tuned for Bortle 9-ish)
    # Narrowband: 300s, LRGB: 180s (you can tweak later)
    for c in channels:
        n = c["name"]
        if n in ("H", "O", "S"):
            c["sub_exposure_seconds"] = 300
        elif n == "L":
            c["sub_exposure_seconds"] = 180
        else:  # R, G, B or others
            c["sub_exposure_seconds"] = 180

    total_minutes = round(base_total)
    weight_sum = sum(c["weight"] for c in channels)

    per_channel_minutes = {}
    for c in channels:
        c["weight_fraction"] = c["weight"] / weight_sum
        c["planned_minutes"] = round(total_minutes * c["weight_fraction"])
        per_channel_minutes[c["name"]] = c["planned_minutes"]

    return {
        "channels": channels,
        "dominant_channel": dominant,
        "total_planned_minutes": total_minutes,
        "per_channel_minutes": per_channel_minutes,
        "palette": palette,
    }



def build_default_plan_json(target_type: str, palette: str, bortle: int = 9) -> str:
    plan = suggest_palette_and_exposures(target_type, palette, bortle)
    return json.dumps(plan, indent=2)


def resolve_target_name(name: str):
    """
    Resolve an object name like 'NGC 6992', 'M31', 'IC 1805' using
    CDS name resolver via astropy.

    Returns:
      (ra_hours, dec_deg) as floats.

    Raises RuntimeError with a friendly message on failure.
    """
    if not ASTRO_DEPS_AVAILABLE:
        raise RuntimeError("Astropy/astroplan not installed; resolver unavailable.")

    name = (name or "").strip()
    if not name:
        raise RuntimeError("Empty name provided.")

    try:
        # Uses remote CDS service under the hood
        coord = SkyCoord.from_name(name)
    except Exception as exc:
        raise RuntimeError(f"Could not resolve '{name}': {exc}") from exc

    ra_hours = float(coord.ra.hour)
    dec_deg = float(coord.dec.degree)
    return ra_hours, dec_deg
