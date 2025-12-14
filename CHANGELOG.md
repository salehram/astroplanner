# Changelog

All notable changes to AstroPlanner will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-14

### 🎉 Initial Stable Release

**AstroPlanner v1.0.0** represents the first stable release of a comprehensive astrophotography session planning tool with all core features complete and thoroughly tested.

### ✅ Core Features Included

#### Target Management
- **Project-based Organization**: Each target treated as its own imaging project
- **Creation Tracking**: Automatic timestamp tracking with local timezone support  
- **Target Settings**: Per-target overrides for pack-up time and minimum altitude
- **Priority Scoring**: Intelligent priority calculation based on completion, remaining time, and tonight's window

#### Session Planning  
- **Tonight's Recommendation**: AI-driven target recommendations for optimal session planning
- **Window Calculations**: Automatic calculation of imaging windows based on sunset, darkness, altitude constraints
- **Progress Tracking**: Comprehensive tracking of completed vs. planned exposures
- **Status Indicators**: Visual badges showing completion status and tonight's potential

#### Palette Management
- **Custom Palettes**: Create and manage custom filter palettes for different targets
- **Database-driven**: Full CRUD operations for palette management with system and custom palette support
- **Filter Recommendations**: Smart filter recommendations based on target type

#### Time Management & Planning
- **H:M:S Time Formatting**: Flexible time input and display in both minutes and H:M:S format
- **Bidirectional Frame/Time Inputs**: Change frame counts to update exposure times and vice versa
- **Real-time Calculations**: Dynamic updates as you modify exposure plans
- **Multi-format Display**: Times shown in both minutes and H:M:S throughout the interface

#### Visual Planning Tools
- **Enhanced Altitude Charts**: Professional charts with threshold lines and window shading
- **Window Visualization**: Green shading for valid imaging times, gray for invalid periods
- **Interactive Elements**: Tooltips showing window status and enhanced hover interactions
- **Threshold Indicators**: Visual markers for minimum altitude requirements

#### Observatory Integration
- **N.I.N.A. Export**: Direct export to N.I.N.A. Advanced Sequencer format
- **Template System**: Customizable sequence templates with dynamic block generation
- **Automated Sequences**: Automatic generation including cooling, filtering, and parking

#### Configuration Management
- **Global Settings**: Observer location (lat/lon/elevation), timezone, default pack-up time, min altitude
- **Per-target Overrides**: Ability to override global settings for individual targets
- **Database Initialization**: Automated setup with sensible defaults
- **Windows Compatibility**: Robust timezone handling for Windows systems

### 🛠️ Technical Features

#### Architecture
- **Flask 3.0.3**: Modern Python web framework
- **SQLAlchemy 2.0.32**: Advanced database ORM with relationship management
- **SQLite Database**: Lightweight, file-based database with full migration support
- **Responsive UI**: Bootstrap-based interface optimized for desktop planning workflows

#### Astronomical Computing
- **Astropy Integration**: Professional-grade astronomical calculations
- **Astroplan Integration**: Advanced observation planning capabilities
- **Timezone Support**: Robust local timezone handling with Windows compatibility
- **Coordinate Systems**: Support for various astronomical coordinate formats

#### Data Management
- **Database Models**: GlobalConfig, TargetType, Palette, Target, TargetPlan, ImagingSession, ObjectMapping
- **Migration Support**: CLI commands for database initialization and updates
- **Data Integrity**: Foreign key relationships and validation
- **Backup Friendly**: Human-readable SQLite format

### 🎯 User Experience

#### Interface Design
- **Dark Theme**: Optimized for nighttime use with astronomy-friendly color scheme
- **Intuitive Navigation**: Clear workflow from target creation to session planning
- **Real-time Feedback**: Immediate updates as settings and plans are modified
- **Professional Appearance**: Charts and visualizations suitable for serious astrophotography

#### Workflow Optimization
- **Streamlined Target Creation**: Quick setup with intelligent defaults
- **Efficient Session Planning**: Prioritized recommendations with visual planning aids
- **Progress Tracking**: Clear indicators of completion status and remaining work
- **Export Integration**: Seamless transition from planning to observatory execution

### 📊 Statistics
- **8 Major Features** implemented and completed
- **1,400+ lines** of Python application code
- **680+ lines** of HTML template code with advanced JavaScript functionality  
- **270+ lines** of comprehensive roadmap documentation
- **240+ lines** of professional README documentation
- **Extensive testing** on Windows Python 3.14 environment

### 🔧 Dependencies
- Python 3.14+ (tested on 3.14.2)
- Flask 3.0.3 web framework
- SQLAlchemy 2.0.32 database ORM
- Astropy ≥7.2.0 for astronomical calculations
- Astroplan ≥0.10.1 for observation planning
- NumPy ≥2.3.5 for numerical computations
- Chart.js for interactive altitude visualization

### 📝 Documentation
- Comprehensive README with installation and usage instructions
- Detailed feature roadmap with implementation status
- Professional project structure and development guidelines
- Docker support for containerized deployment
- License and contribution guidelines

---

**Release Notes**: This stable release provides a complete astrophotography planning solution suitable for serious amateur astronomers and astrophotographers. All core features are implemented, tested, and ready for production use.

**Next Release Focus**: Future versions will focus on advanced features like AI-driven session recommendation engines, weather integration, and enhanced mobile responsiveness.