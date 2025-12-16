# FMQE Quick Reference Card

## One-Line Commands

```powershell
# Setup (first time)
.\setup_environment.ps1

# Verify installation
py -3.12 test_setup.py

# Start notebook
py -3.12 -m jupyter notebook fmqe_import.ipynb
```

## Notebook Cell Order

| Cell | Run | Description |
|------|-----|-------------|
| 2 | Always first | JVM + imports |
| 4 | Always | Configuration |
| 6-7 | Always | PostgreSQL |
| 9 | Always | Schemas |
| 11-13 | Always | FileMaker |
| 15 | Always | Table definitions |
| 17-18 | Always | Import functions |
| **20** | First time | **FULL IMPORT** |
| **22** | Daily | **INCREMENTAL** |

## Key Paths

```
JAVA_HOME = C:\projects\duft\java\jdk-21.0.4+7
JVM_PATH  = C:\projects\duft\java\jdk-21.0.4+7\bin\server\jvm.dll
JDBC_JAR  = C:\projects\duft\fmqe\fmjdbc.jar
```

## Connections

| System | Host | Port | User |
|--------|------|------|------|
| PostgreSQL | 127.0.0.1 | 5432 | postgres |
| FileMaker | localhost | 2399 | Administrator |

## Common Fixes

| Problem | Solution |
|---------|----------|
| JVM not found | Restart kernel, check JAVA_HOME |
| Connection refused | Start FileMaker, enable JDBC |
| Column not found | Check table schema, update query |
| Class not found | Restart kernel, check JDBC_JAR |

## Tables Imported

`pat` → `cd` → `fup` → `tsfr` → `meas` → `rgm` → `ti` → `tbt` → `lab`

## PostgreSQL Access

```sql
-- View imported data
SELECT * FROM fm_staging.pat LIMIT 10;

-- Check import history
SELECT * FROM fm_staging.import_history ORDER BY id DESC;

-- Count records
SELECT 'pat' as tbl, COUNT(*) FROM fm_staging.pat
UNION ALL SELECT 'cd', COUNT(*) FROM fm_staging.cd
UNION ALL SELECT 'fup', COUNT(*) FROM fm_staging.fup;
```

---
*Full docs: DOCUMENTATION.md*
