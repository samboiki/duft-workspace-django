# FMQE - FileMaker to PostgreSQL Query Engine

**Version 1.0.0** | **December 2025**

A Python-based ETL solution for importing patient health data from FileMaker databases to PostgreSQL.

---

## Quick Start

### 1. Run Setup Script
```powershell
cd C:\projects\duft\fmqe
.\setup_environment.ps1
```

### 2. Verify Installation
```powershell
py -3.12 test_setup.py
```

### 3. Run Imports
```powershell
py -3.12 -m jupyter notebook fmqe_import.ipynb
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [DOCUMENTATION.md](DOCUMENTATION.md) | **Comprehensive guide** - Full background, architecture, installation, troubleshooting |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | **Cheat sheet** - Commands, paths, common fixes |
| [SETUP_REPORT.md](SETUP_REPORT.md) | **Technical report** - What was configured, issues resolved |

---

## What It Does

```
FileMaker Database  ──────►  FMQE  ──────►  PostgreSQL
   (Source)                (Python)          (Analytics)
```

- **Full Import**: Initial load of all historical data
- **Incremental Import**: Daily sync of changed records only
- **9 Tables**: pat, cd, fup, tsfr, meas, rgm, ti, tbt, lab
- **Audit Trail**: Complete import history tracking

---

## Requirements

| Software | Version |
|----------|---------|
| Python | 3.12+ |
| Java (OpenJDK) | 21+ |
| PostgreSQL | 18+ |
| FileMaker Server | 19+ (with JDBC enabled) |

---

## Files

```
fmqe/
├── fmqe_import.ipynb      # Main notebook
├── fmjdbc.jar             # FileMaker JDBC driver
├── test_setup.py          # Verification script
├── setup_environment.ps1  # Setup script (PowerShell)
├── setup_environment.bat  # Setup script (Batch)
├── DOCUMENTATION.md       # Full documentation
├── QUICK_REFERENCE.md     # Quick reference card
├── SETUP_REPORT.md        # Setup report
└── README.md              # This file
```

---

## Support

See [DOCUMENTATION.md](DOCUMENTATION.md) for troubleshooting guide.

---

*UCSF IGHS / MoHSS NDW Data Engineering*
