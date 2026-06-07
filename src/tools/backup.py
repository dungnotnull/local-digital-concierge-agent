'
import os
import shutil
import time
from datetime import datetime
from pathlib import Path

def backup_database(db_path: str = "data/concierge.db", backup_dir: str = "data/backups", max_backups: int = 7):
    """
    Create a backup of the SQLite database.
    Keeps only the most recent `max_backups` backups.
    """
    # Ensure backup directory exists
    Path(backup_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp for backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"concierge_{timestamp}.db"
    backup_path = Path(backup_dir) / backup_filename
    
    # Copy the database file
    if os.path.exists(db_path):
        shutil.copy2(db_path, backup_path)
        print(f"Backup created: {backup_path}")
    else:
        print(f"Warning: Database file not found at {db_path}")
        return
    
    # Clean up old backups
    backups = sorted(Path(backup_dir).glob("concierge_*.db"))
    if len(backups) > max_backups:
        for old_backup in backups[:-max_backups]:
            try:
                os.remove(old_backup)
                print(f"Removed old backup: {old_backup}")
            except OSError as e:
                print(f"Error removing backup {old_backup}: {e}")

if __name__ == "__main__":
    # For testing
    backup_database()
'
