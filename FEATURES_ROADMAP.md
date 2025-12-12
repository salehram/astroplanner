# AstroPlanner – Feature Roadmap  
*Status: Updated to 2025-12-12*

This document tracks the major features of the AstroPlanner project, what has been completed, and what remains.  
It is intended to be version-controlled in Git for transparency, planning, and future development.

---

## ✅ 1. Treat Each Target as a Project
### Summary  
Originally there was an option to either:
- Treat a target as a top-level object with multiple plans, or  
- Treat every target as its own project.

### Final Decision  
**Each target = one project.**

### Completed
- Added `created_at` to the `Target` model.
- Displayed creation date/time (converted to local timezone).
- Shown on both:
  - Target detail page  
  - Index page  
- Improved visibility using `text-light` + highlighted timestamp.

### Remaining  
Nothing. Feature fully implemented.

---

## ✅ 2. Local Time Zone Handling
### Completed
- Introduced `get_local_tz()` with robust Windows-friendly fallback.
- All timestamps (including created time) now correctly convert:
  - From UTC → Local (UTC+3 by default).
- Eliminated reliance on `tzdata` on systems where it's absent.
- Improved visibility styling.

### Remaining
- Optional: explicitly label sunset/dark/meridian times as “Local Time”.

---

## ✅ 3. Database Rebuild Support
### Completed
- Schema updated with new `created_at` field.
- Provided CLI command `flask --app app.py init-db`.
- Database recreated and validated.

### Remaining  
None.

---

## ✅ 4. NINA Export – Option A (Remaining Subs)
### Completed
- NINA JSON template parsed successfully.
- Dynamic block generation for:
  - Cooling camera  
  - Filter changes  
  - Wait instructions  
  - Exposure sequences  
  - Parking telescope  
- Correct mapping of filter names → wheel positions.
- Export now produces a fully functional NINA Advanced Sequencer JSON.

### Remaining (optional future enhancements)
- Export full plan (not only remaining subs).
- Allow template customization in-app.
- Store multiple export templates.

---

## ✅ 5. Global & Per-Target Configuration (Completed)
### Required
- Global defaults for:
  - Pack-up time
  - Minimum altitude
  - Observer location (lat/lon/elevation)
  - Timezone (fallback to UTC+3)
- Per-target overrides.
- Recompute all dependent information when changed:
  - Window start/end  
  - Midpoint altitude  
  - Chart  
  - NINA export  
  - Status badges  

### Completed
- Added `GlobalConfig` database model with observer location, default settings, and timezone.
- Added `override_packup_time` and `override_min_altitude` fields to `Target` model.
- Created global settings UI at `/settings` with configuration management.
- Created per-target settings UI at `/target/<id>/settings` for overrides.
- Implemented configuration resolution logic with helper functions.
- Updated all window calculations to use configurable parameters instead of hardcoded values.
- Added navigation links in navbar and target detail pages.
- Database initialization automatically creates default global configuration.
- All existing features (window calculations, charts, NINA export) now use configured settings.

### Status  
**✅ Fully implemented and working.**

---

## 🟡 6. Palette Management System (Pending)
### Required
- Create a `Palette` table in the database.
- UI for:
  - Add / edit / delete palettes
  - Edit filter weights
  - Rename channels
  - Add creative blends (e.g., Foraxx, dynamic SHO variants)
- Tie palette to each target.
- Recompute plans when palette changes.

### Status  
Not started.

---

## 🟡 7. Plan & Palette Enhancements (Pending)
### 7.1 Show Planned & Completed Times in H:M:S
- Planned time currently shown only in minutes.
- Completed exposure totals also shown only in minutes.
- Need:
  - H:M:S formatting
  - Ability to enter total planned time in either:
    - Minutes
    - HH:MM:SS format

### 7.2 Make Frames & Time Inputs Bidirectional
- Changing planned minutes should update # of required subs.
- Changing # of subs should update planned minutes.

### Status  
Partially implemented, needs full bidirectional logic.

---

## 🟡 8. Altitude Chart Enhancements (Pending)
### Required
- Draw a horizontal line at the altitude threshold (e.g., 30°).
- Shade the region corresponding to the valid imaging window:
  - Inside window: highlighted
  - Outside window: dimmed

### Status  
Not implemented yet.

---

## 🟡 9. Automatic Recompute Pipeline (Pending)
Any of the following should automatically trigger a full recomputation:
- Changing pack-up time  
- Changing altitude threshold  
- Changing observer location  
- Changing palette  
- Editing planned time or subs  

Affected subsystems:
- Window calculation
- Altitude chart
- Dominant channel
- Total planned exposure
- Remaining subs & time
- NINA export

### Status  
Not started.

---

# Summary Table

| Feature | Status | Notes |
|--------|--------|-------|
| Target-as-project design | ✅ Done | Creation timestamp integrated |
| Local timezone support | ✅ Done | Full conversion to UTC+3 |
| Database rebuild support | ✅ Done | CLI command available |
| NINA export (remaining subs) | ✅ Done | Fully functional |
| Global/per-target configuration | ✅ Done | Observer location, pack-up time, min altitude |
| Palette management | 🟡 Pending | Requires DB + UI |
| Planned/completed H:M:S | 🟡 Pending | Add formatting + editable logic |
| Altitude chart enhancements | 🟡 Pending | Draw threshold + shading |
| Automatic recomputation | 🟡 Pending | After changes to settings |

---

# Next Recommended Focus
**6. Palette Management System**  
Now that global configuration is complete, the next logical step is implementing a database-driven palette management system. This will allow:
- Creating custom palettes beyond the hardcoded SHO/HOO/LRGB/LRGBNB options
- Editing filter weights and channel configurations
- Dynamic palette creation for creative blends

Alternative focus areas:
- **7. Plan & Palette Enhancements** - H:M:S formatting and bidirectional frame/time inputs
- **8. Altitude Chart Enhancements** - Threshold lines and window shading visualization

---

# End of Roadmap
