# DUFT Project Setup Guide

## Current Status

### ✅ Completed Steps
1. **Git submodules initialized** - All 6 repositories cloned successfully
   - duft-server (Django backend)
   - duft-ui (React frontend)
   - duft-config (Configuration)
   - duft-config-wakanda (Wakanda-specific config)
   - duft-docs (Documentation)
   - flowbite-react (UI components)

2. **Node.js & Yarn installed**
   - Node.js v22.16.0 ✓
   - Yarn v1.22.x ✓

### ⚠️ Required Manual Actions

You need to install **2 things** before we can continue:

## 1. Install Python 3.12

**Why:** Python 3.13 is too new - many required packages don't have pre-built wheels yet.

**Download:** https://www.python.org/downloads/release/python-31210/
- Scroll down to "Files"
- Download: **Windows installer (64-bit)**

**Installation Steps:**
1. Run the installer
2. ✅ **IMPORTANT:** Check "Add Python 3.12 to PATH"
3. ✅ Check "Install for all users" (optional but recommended)
4. Click "Install Now"
5. After installation, verify by opening new Command Prompt:
   ```cmd
   python --version
   ```
   Should show: `Python 3.12.10` (or similar)

## 2. Install PostgreSQL 15

**Why:** Required database for the Django backend.

**Download:** https://www.postgresql.org/download/windows/
- Click "Download the installer"
- Choose **PostgreSQL 15.x** for Windows x86-64
- From EnterpriseDB: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads

**Installation Steps:**
1. Run the installer
2. Components: Install all (PostgreSQL Server, pgAdmin, Command Line Tools)
3. **Password for postgres user:** Set to `postgres`
   - (This matches the project's default config)
   - Write it down if you use a different password
4. **Port:** `5432` (default)
5. **Locale:** Default
6. Complete the installation

**After Installation:**
PostgreSQL will run automatically as a Windows service.

---

## What Happens After You Install

Once you've installed **Python 3.12** and **PostgreSQL 15**, let me know and I'll automatically:

1. ✅ Recreate the Python virtual environment with Python 3.12
2. ✅ Install all Django dependencies (Django, DRF, Channels, etc.)
3. ✅ Create the `qe_data` database in PostgreSQL
4. ✅ Run database migrations
5. ✅ Create a superuser account for you
6. ✅ Install frontend dependencies (React, Vite, Tailwind)
7. ✅ Start both backend and frontend servers
8. ✅ Open the application in your browser

---

## Installation Downloads Quick Reference

| Software | Version | Download Link |
|----------|---------|---------------|
| Python | 3.12.10 | https://www.python.org/downloads/release/python-31210/ |
| PostgreSQL | 15.x | https://www.enterprisedb.com/downloads/postgres-postgresql-downloads |

---

## Verification Commands

After installing, verify in a **new Command Prompt**:

```cmd
# Check Python 3.12
python --version
# Should show: Python 3.12.x

# Check PostgreSQL
psql --version
# Should show: psql (PostgreSQL) 15.x
```

---

## Project Information

**Database Configuration (from .env):**
- Host: `127.0.0.1` (localhost)
- Port: `5432`
- Database: `qe_data`
- Username: `postgres`
- Password: `postgres`

**Application Ports:**
- Backend (Django): `http://localhost:8000`
- Frontend (React): `http://localhost:3031`

**Features Enabled:**
- ✓ Data Tasks
- ✓ User Authentication
- ✓ Server Uploads
- ✓ AI Engine
- ✗ Task Scheduler (disabled)

---

## Troubleshooting

**If Python 3.12 installation fails:**
- Try downloading the installer again
- Run as Administrator
- Uninstall Python 3.13 first if needed

**If PostgreSQL installation fails:**
- Ensure no other PostgreSQL instances are running
- Check that port 5432 is available
- Run installer as Administrator

**If you prefer Docker instead:**
- Install Docker Desktop: https://www.docker.com/products/docker-desktop/
- I can use the included `docker-compose.yml` for PostgreSQL

---

## Ready to Continue?

After installing both Python 3.12 and PostgreSQL 15:
1. Open a **new** Command Prompt or Terminal
2. Navigate to: `C:\projects\duft`
3. Let me know you're ready, and I'll complete the automated setup!
