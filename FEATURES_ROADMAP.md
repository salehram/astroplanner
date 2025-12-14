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

## ✅ 6. Palette Management System (Completed)
### Summary  
Database-driven palette management system allowing custom palettes beyond the hardcoded SHO/HOO/LRGB/LRGBNB options.

### Completed
- **Database Model**: Created `Palette` table with full palette definitions in JSON format
- **Database Schema Updates**: 
  - Added `palette_id` foreign key to `Target` and `TargetPlan` models
  - Maintained backward compatibility with existing `preferred_palette` and `palette_name` string fields
- **Default Palettes**: Automatically initialized system palettes (SHO, HOO, LRGB, LRGBNB) with detailed filter configurations
- **Palette Management UI**:
  - List view showing all available palettes (system and custom)
  - Create new custom palettes with dynamic filter channel configuration
  - Edit existing custom palettes (system palettes are read-only)
  - Delete custom palettes (with safety checks for usage)
  - Navigation integration in main navbar
- **Integration**: Updated target creation and editing forms to use database palettes instead of hardcoded options
- **Filter Configuration**: Each palette stores detailed filter information including:
  - Filter names, labels, and descriptions
  - RGB channel mappings
  - Default exposure times and weights
  - Custom channel configurations

### Technical Implementation
- Palettes stored as JSON in database for maximum flexibility
- Backward compatibility maintained during transition
- System palettes protected from modification/deletion
- Usage validation prevents deletion of palettes in use by targets

### Status  
**✅ Fully implemented and working.**

---

## ✅ 7. Plan & Palette Enhancements
### 7.1 Show Planned & Completed Times in H:M:S
- Planned time currently shown only in minutes.
- Completed exposure totals also shown only in minutes.
- Need:
  - H:M:S formatting ✅
  - Ability to enter total planned time in either:
    - Minutes ✅
    - HH:MM:SS format ✅

### 7.2 Make Frames & Time Inputs Bidirectional
- Changing planned minutes should update # of required subs. ✅
- Changing # of subs should update planned minutes. ✅

### Completed  
- **H:M:S Time Formatting**: Created `time_utils.py` with functions for H:M:S conversion
- **Template Updates**: Updated index.html and target_detail.html to display times in both minutes and H:M:S format
- **Bidirectional Inputs**: 
  - Total planned time can be entered in minutes or H:M:S format with real-time bidirectional conversion
  - Channel-level time inputs also support bidirectional minute ↔ H:M:S conversion
  - Frame count inputs automatically update time fields and vice versa
  - All inputs sync in real-time as users type
- **JavaScript Enhancements**: Added parseHMS(), minutesToHMS(), and enhanced recalcFrames() for full bidirectional functionality

### Status  
**✅ Fully implemented and working.**

---

## ✅ 8. Altitude Chart Enhancements
### Required
- Draw a horizontal line at the altitude threshold (e.g., 30°). ✅
- Shade the region corresponding to the valid imaging window:
  - Inside window: highlighted ✅
  - Outside window: dimmed ✅

### Completed
- **Threshold Line**: Added dashed red line showing minimum altitude threshold with legend
- **Window Shading**: 
  - Green shaded area highlights valid imaging window
  - Gray shading for times outside the imaging window
  - Dashed vertical lines mark window boundaries
- **Enhanced Interactivity**:
  - Improved legend showing both altitude curve and threshold line
  - Enhanced tooltips indicating whether time is within imaging window
  - Grid line coloring to reinforce window visualization
- **Visual Improvements**:
  - Better color scheme with blue altitude curve and red threshold
  - Responsive design with improved hover interactions
  - Custom Chart.js plugin for background shading

### Status  
**✅ Fully implemented and working.**

---

## 🟡 9. Session Recommendation Engine with AI-Driven Logic (Pending)
### Summary
Implement an intelligent session recommendation engine that uses AI/ML to optimize imaging sessions based on multiple factors and user preferences.

### Required Features
- **Weather Integration**: Real-time weather data and forecasting
- **Target Priority Scoring**: AI-driven ranking based on:
  - Current target visibility and altitude
  - Weather conditions and forecast
  - Moon phase and illumination impact
  - Historical completion data
  - User preferences and imaging history
- **Session Planning**: Automatically suggest:
  - Best targets for tonight/upcoming nights
  - Optimal imaging order within a session
  - Filter switching recommendations to minimize equipment changes
  - Adaptive scheduling based on changing conditions
- **Machine Learning Components**:
  - Learn from user behavior and preferences
  - Improve recommendations based on session outcomes
  - Adapt to local weather patterns and seeing conditions
- **Integration Features**:
  - Export recommended session plans to NINA
  - Real-time session adjustments based on conditions
  - Historical analysis and recommendation accuracy tracking

### Technical Considerations
- Weather API integration (OpenWeatherMap, Clear Outside, etc.)
- ML framework integration (scikit-learn, TensorFlow Lite, etc.)
- Background scheduling and recommendation updates
- User feedback collection for model training

### Status  
**Feature concept added to roadmap - not yet started.**

---

## 🟡 10. Automatic Recompute Pipeline (Pending)
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
| Palette management | ✅ Done | Database-driven with custom palette support |
| Plan & Palette Enhancements | ✅ Done | H:M:S formatting and bidirectional frame/time inputs |
| Altitude chart enhancements | ✅ Done | Threshold lines, window shading, enhanced interactivity |
| Session recommendation engine | 🟡 Pending | AI-driven session optimization |
| Automatic recomputation | 🟡 Pending | After changes to settings |

---

# Next Recommended Focus
**9. Session Recommendation Engine** - AI-driven session optimization  
Now that the core planning features are complete (time formatting, palette management, altitude visualization), the next major enhancement is implementing an intelligent session recommendation engine. This ambitious feature includes:
- Weather integration and forecasting
- AI-driven target priority scoring based on multiple factors
- Automatic session planning and filter switching recommendations
- Machine learning to adapt to user behavior and local conditions

Alternative smaller enhancements:
- **10. Automatic Recomputation** - Dynamic updates when settings change
- **Additional Export Formats** - More observatory software integrations
- **Mobile Responsiveness** - Enhanced mobile interface optimizations

---

# End of Roadmap
