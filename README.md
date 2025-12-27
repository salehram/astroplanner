# AstroPlanner

A comprehensive web-based tool for planning astrophotography sessions and managing imaging targets. Built with Flask and designed to help astrophotographers optimize their imaging time and track their progress.

![Version](https://img.shields.io/badge/version-1.0.0-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.14+-green.svg)
![Flask](https://img.shields.io/badge/flask-3.0.3-red.svg)
![Status](https://img.shields.io/badge/status-stable-success.svg)

## � Version 1.0.0 - Complete Feature Set

AstroPlanner v1.0.0 represents a mature, feature-complete astrophotography planning platform with comprehensive target management, session tracking, and telescope integration capabilities.

## 🌟 Features

### 📊 Target Management & Planning
- **Project-based Organization**: Each target is treated as its own imaging project with dedicated tracking
- **Creation Tracking**: Automatic timestamp tracking with local timezone support
- **Target Settings**: Per-target overrides for pack-up time and minimum altitude constraints
- **Priority Scoring**: Intelligent priority calculation based on completion percentage, remaining time, and tonight's window
- **Advanced Filter System**: Custom filter addition with real-time bidirectional calculations (minutes ↔ frames ↔ exposure time)
- **NINA Filter Mapping**: Custom filters map to standard telescope filter wheel names for hardware compatibility

### 🎯 Session Planning & Execution
- **Tonight's Recommendation**: AI-driven target recommendations for optimal session planning
- **Window Calculations**: Automatic calculation of imaging windows based on:
  - Sunset and astronomical darkness times
  - Target altitude constraints with visual chart indicators
  - Observer location and timezone with global configuration
- **Progress Tracking**: Comprehensive tracking with edit/delete functionality for session records
- **Time Management**: Flexible time input with H:M:S formatting and bidirectional conversions
- **Imaging Logs**: Complete session history with statistics, analytics, and backdating support

### 🎨 Palette & Filter Management
- **Custom Palettes**: Create and manage custom filter palettes with JSON-based storage
- **Database-driven CRUD**: Full palette management with system vs. custom palette protection
- **Filter Recommendations**: Smart filter recommendations based on target type and palette selection
- **Auto-populated Dropdowns**: Filter selection automatically populates from active target plans

### 📈 Advanced Planning & Calculations
- **Bidirectional Frame/Time Inputs**: Change frame counts to update exposure times and vice versa with decimal precision
- **Real-time Calculations**: Dynamic updates as you modify exposure plans with JavaScript validation
- **Status Indicators**: Visual badges showing completion status and tonight's imaging potential
- **Multi-format Time Display**: Times shown in both minutes and H:M:S format throughout the interface
- **Custom Filter Addition**: On-the-fly custom filter addition with auto-save and NINA compatibility

### 🔧 NINA Integration & Export
- **Export Compatibility**: Direct export to N.I.N.A. (Nighttime Imaging 'N' Astronomy) Advanced Sequencer
- **Template System**: Customizable sequence templates with dynamic block generation
- **Filter Wheel Integration**: Custom filter mapping ensures proper telescope hardware operation
- **Remaining Frames Export**: Intelligent export of only remaining frames for efficient session continuation

### 🌍 Global Configuration & Settings
- **Observer Location**: Configurable latitude, longitude, and elevation with global defaults
- **Timezone Support**: Robust timezone handling with Windows compatibility and UTC conversion
- **Default Settings**: Global defaults for pack-up time and minimum altitude with per-target overrides
- **Settings Management**: Dedicated configuration interface for both global and per-target settings

### 📊 Data Management & Analytics
- **Session Edit/Delete**: Complete CRUD operations for imaging session management with confirmation dialogs
- **Comprehensive Logs**: Imaging session tracking with date grouping, statistics, and monthly summaries
- **Progress Analytics**: Daily, monthly, and overall imaging statistics with visual indicators
- **Data Integrity**: Form validation, error handling, and database consistency maintenance

## 🚀 Quick Start

### Prerequisites

- Python 3.14+ (tested on 3.14.2)
- Git (for cloning the repository)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/astroplanner.git
   cd astroplanner
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv dev
   dev\Scripts\activate

   # Linux/macOS
   python -m venv dev
   source dev/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python -c "from app import app, init_db; app.app_context().push(); init_db()"
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   Navigate to `http://127.0.0.1:5000`

## 📋 Usage

### First-Time Setup

1. **Configure Global Settings**
   - Navigate to Settings (gear icon in navbar)
   - Set your observer location (latitude, longitude, elevation)
   - Configure default pack-up time and minimum altitude
   - Set your timezone

2. **Create Your First Target**
   - Click "+ New Target" on the home page
   - Enter target details (name, catalog ID, coordinates)
   - Set target type (Galaxy, Nebula, Star Cluster, etc.)
   - Choose or create a custom palette

3. **Plan Your Session**
   - Open the target detail page
   - Set total planned exposure time (in minutes or H:M:S format)
   - Configure channel-specific exposure plans
   - Use bidirectional frame/time inputs for precise planning

### Daily Workflow

1. **Check Tonight's Recommendation**
   - View the prioritized target recommendation on the home page
   - Review tonight's imaging window and suggested focus channel

2. **Update Progress**
   - Record completed exposures in the target detail page
   - Track progress with visual status indicators
   - Monitor remaining work and completion percentages

3. **Export to NINA**
   - Generate Advanced Sequencer files for remaining exposures
   - Automatic integration with your existing NINA templates

## 🗂️ Project Structure

```
astroplanner/
├── app.py                 # Main Flask application
├── astro_utils.py         # Astronomical calculations
├── nina_integration.py    # N.I.N.A. export functionality
├── time_utils.py         # Time formatting and parsing utilities
├── requirements.txt      # Python dependencies
├── FEATURES_ROADMAP.md   # Feature development roadmap
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── target_detail.html
│   ├── target_form.html
│   ├── settings.html
│   └── palette_list.html
├── dev/                  # Virtual environment
├── uploads/              # File uploads directory
└── astroplanner.db       # SQLite database
```

## ⚙️ Configuration

### Environment Variables

- `SECRET_KEY`: Flask secret key (defaults to 'dev-secret-key')
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `UPLOAD_FOLDER`: File upload directory (defaults to ./uploads)
- `OBSERVER_TZ`: Observer timezone (defaults to UTC+3)

### Database Models

The application uses SQLite with SQLAlchemy ORM:

- **GlobalConfig**: Observer location, default settings, timezone
- **TargetType**: Target classification system
- **Palette**: Custom filter palette definitions
- **Target**: Individual imaging targets
- **TargetPlan**: Exposure plans and channel definitions
- **ImagingSession**: Session tracking and progress data
- **ObjectMapping**: Catalog cross-references

## 🐳 Docker Support

The project includes Docker configuration for containerized deployment:

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 🛠️ Development

### Dependencies

- **Flask 3.0.3**: Web framework
- **SQLAlchemy 2.0.32**: Database ORM
- **Astropy ≥7.2.0**: Astronomical calculations
- **Astroplan ≥0.10.1**: Observation planning
- **NumPy ≥2.3.5**: Numerical computations

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📊 Current Status

### ✅ Completed Features

- Target-as-project design with creation timestamps
- Local timezone support with Windows compatibility
- Database rebuild support with CLI commands
- NINA export functionality for remaining exposures
- Global and per-target configuration management
- Palette management system with CRUD operations
- Plan & Palette Enhancements with H:M:S formatting
- Bidirectional frame/time input functionality

### 🚧 Roadmap

- **Altitude Chart Enhancements**: Visual improvements with threshold lines and shading
- **Session Recommendation Engine**: AI-driven session optimization
- **Automatic Recomputation**: Dynamic updates after configuration changes
- **Advanced Export Options**: Additional template formats and customization

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with the assistance of AI for rapid development
- Astropy and Astroplan communities for excellent astronomical libraries
- N.I.N.A. project for advanced sequencer integration
- Flask and SQLAlchemy communities for robust web framework foundation

## 📞 Support

For questions, issues, or feature requests:

1. Check the [FEATURES_ROADMAP.md](FEATURES_ROADMAP.md) for planned development
2. Open an issue on GitHub
3. Review existing documentation and code comments

---

**Happy Imaging! 🌌✨**
