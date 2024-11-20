import os
import shutil
import subprocess
import sys

# Paths
VENV_DIR = ".venv"
REQUIREMENTS_FILE = "duft-server/requirements.txt"
BACKUP_DIR = f"{VENV_DIR}_backup"


def backup_venv():
    """Backs up the current virtual environment."""
    if os.path.exists(BACKUP_DIR):
        print(f"Backup already exists: {BACKUP_DIR}")
    else:
        shutil.copytree(VENV_DIR, BACKUP_DIR)
        print(f"Backup created at {BACKUP_DIR}")


def restore_venv():
    """Restores the backup virtual environment."""
    if os.path.exists(BACKUP_DIR):
        if os.path.exists(VENV_DIR):
            shutil.rmtree(VENV_DIR)
        shutil.move(BACKUP_DIR, VENV_DIR)
        print(f"Backup restored to {VENV_DIR}")
    else:
        print(f"No backup found at {BACKUP_DIR}")


def update_packages():
    """Updates all packages in the virtual environment."""
    print("Backing up the current virtual environment...")
    backup_venv()

    print("Updating packages...")
    # Activate virtual environment and upgrade packages
    subprocess.run(
        f"{VENV_DIR}/bin/pip freeze > {REQUIREMENTS_FILE}", shell=True, check=True
    )
    subprocess.run(
        f"{VENV_DIR}/bin/pip list --outdated --format=freeze | cut -d '=' -f 1 | xargs -n1 {VENV_DIR}/bin/pip install -U",
        shell=True,
        check=True,
    )
    print("Packages updated successfully.")

    # Export updated requirements
    subprocess.run(
        f"{VENV_DIR}/bin/pip freeze > {REQUIREMENTS_FILE}", shell=True, check=True
    )
    print(f"Updated requirements saved to {REQUIREMENTS_FILE}")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "-reverse":
        print("Reversing to backup...")
        restore_venv()
    else:
        print("Starting update process...")
        update_packages()


if __name__ == "__main__":
    main()
