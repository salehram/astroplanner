# AstroPlanner

A comprehensive web-based tool for planning astrophotography sessions and managing imaging targets. Built with Flask and designed to help astrophotographers optimize their imaging time and track their progress.

![Version](https://img.shields.io/badge/version-1.0.0-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.14+-green.svg)
![Flask](https://img.shields.io/badge/flask-3.0.3-red.svg)
![Status](https://img.shields.io/badge/status-stable-success.svg)

## 🌟 Features

### 📊 Target Management
- **Project-based Organization**: Each target is treated as its own imaging project
- **Creation Tracking**: Automatic timestamp tracking with local timezone support
- **Target Settings**: Per-target overrides for pack-up time and minimum altitude
- **Priority Scoring**: Intelligent priority calculation based on completion percentage, remaining time, and tonight's window

### 🎯 Session Planning
- **Tonight's Recommendation**: AI-driven target recommendations for optimal session planning
- **Window Calculations**: Automatic calculation of imaging windows based on:
  - Sunset and astronomical darkness times
  - Target altitude constraints
  - Observer location and timezone
- **Progress Tracking**: Comprehensive tracking of completed vs. planned exposures
- **Time Management**: Flexible time input with H:M:S formatting and bidirectional conversions

### 🎨 Palette Management
- **Custom Palettes**: Create and manage custom filter palettes for different targets
- **Database-driven**: Full CRUD operations for palette management
- **Filter Recommendations**: Smart filter recommendations based on target type

### 📈 Advanced Planning
- **Bidirectional Frame/Time Inputs**: Change frame counts to update exposure times and vice versa
- **Real-time Calculations**: Dynamic updates as you modify exposure plans
- **Status Indicators**: Visual badges showing completion status and tonight's potential
- **Multi-format Time Display**: Times shown in both minutes and H:M:S format

### 🔧 NINA Integration
- **Export Compatibility**: Direct export to N.I.N.A. (Nighttime Imaging 'N' Astronomy) Advanced Sequencer
- **Template System**: Customizable sequence templates
- **Dynamic Block Generation**: Automatic sequence generation with cooling, filtering, and parking

### 🌍 Global Configuration
- **Observer Location**: Configurable latitude, longitude, and elevation
- **Timezone Support**: Robust timezone handling with Windows compatibility
- **Default Settings**: Global defaults for pack-up time and minimum altitude
- **Per-target Overrides**: Ability to override global settings per target

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
