from alembic.config import Config
from alembic import command
import os

def run_migrations():
    """
    Programmatically runs Alembic migrations to upgrade the database to the 'head' revision.
    
    This script is a workaround for environments where direct `alembic` command execution
    is restricted. It locates the `alembic.ini` file in the project root and invokes
    the upgrade command using the Alembic library's programmatic API.
    """
    try:
        # The script is in /scripts, so the project root is one level up.
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Construct the full path to alembic.ini
        alembic_ini_path = os.path.join(project_root, 'alembic.ini')
        
        if not os.path.exists(alembic_ini_path):
            print(f"Error: alembic.ini not found at {alembic_ini_path}")
            return

        print(f"Using Alembic config: {alembic_ini_path}")
        
        # Create an AlembicConfig object
        alembic_cfg = Config(alembic_ini_path)
        
        # Ensure the script location is correctly set relative to the project root
        alembic_cfg.set_main_option("script_location", os.path.join(project_root, "alembic"))
        
        print("Running Alembic upgrade to 'head'...")
        # Run the 'upgrade' command
        command.upgrade(alembic_cfg, "head")
        
        print("Database migration completed successfully.")

    except Exception as e:
        print(f"An error occurred during migration: {e}")
        # Re-raise the exception to ensure the script exits with a non-zero status code
        raise

if __name__ == "__main__":
    run_migrations()
