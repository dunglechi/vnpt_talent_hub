"""
Cleanup script to remove old files after restructuring
Run this only after verifying the new structure works correctly
"""

import os
import shutil

# Root directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Old files to remove (now replaced by files in app/ and scripts/)
old_files = [
    "database.py",         # → app/core/database.py
    "models.py",           # → app/models/competency.py, job.py, employee.py
    "create_database.py",  # → scripts/create_database.py
    "create_tables.py",    # → scripts/create_tables.py
    "import_data.py",      # → scripts/import_data.py
    "ssh_tunnel.py"        # → scripts/ssh_tunnel.py
]

def cleanup():
    """Remove old files after verifying new structure works"""
    print("=" * 60)
    print("VNPT Talent Hub - Cleanup Script")
    print("=" * 60)
    print("\n⚠️  WARNING: This will delete old files that have been")
    print("   moved to the new structure (app/ and scripts/).")
    print("\nFiles to be deleted:")
    
    for file in old_files:
        filepath = os.path.join(ROOT_DIR, file)
        if os.path.exists(filepath):
            print(f"  - {file}")
    
    print("\n" + "=" * 60)
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("✗ Cleanup cancelled.")
        return
    
    print("\n" + "=" * 60)
    print("Starting cleanup...")
    print("=" * 60)
    
    deleted_count = 0
    for file in old_files:
        filepath = os.path.join(ROOT_DIR, file)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"✓ Deleted: {file}")
                deleted_count += 1
            except Exception as e:
                print(f"✗ Error deleting {file}: {e}")
        else:
            print(f"⊘ Not found: {file}")
    
    print("\n" + "=" * 60)
    print(f"✓ Cleanup completed! Deleted {deleted_count} files.")
    print("=" * 60)
    
    # Clean __pycache__
    print("\nCleaning __pycache__ directories...")
    for root, dirs, files in os.walk(ROOT_DIR):
        if '__pycache__' in dirs:
            pycache_dir = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_dir)
                print(f"✓ Removed: {pycache_dir}")
            except Exception as e:
                print(f"✗ Error removing {pycache_dir}: {e}")
    
    print("\n✓ All cleanup operations completed!")

if __name__ == "__main__":
    # Verify new structure exists first
    required_dirs = ["app", "app/core", "app/models", "scripts", "docs"]
    missing_dirs = []
    
    for dir_name in required_dirs:
        if not os.path.exists(os.path.join(ROOT_DIR, dir_name)):
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print("✗ ERROR: New structure incomplete!")
        print("Missing directories:")
        for dir_name in missing_dirs:
            print(f"  - {dir_name}")
        print("\nPlease complete the restructuring first.")
    else:
        cleanup()
