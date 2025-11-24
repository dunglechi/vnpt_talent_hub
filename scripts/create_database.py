"""
Script to create the vnpt_talent_hub database
Run this once before creating tables
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Parse DATABASE_URL from .env
# Format: postgresql://postgres:Cntt%402025@localhost:1234/vnpt_talent_hub
database_url = os.getenv("DATABASE_URL")
# Extract connection details
import re
match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', database_url)
if match:
    user, password, host, port, dbname = match.groups()
    # Unescape password
    password = password.replace('%40', '@')
else:
    # Fallback to defaults
    host = "localhost"
    port = "1234"
    user = "postgres"
    password = "Cntt@2025"

# Kết nối đến PostgreSQL (kết nối tới database postgres - database mặc định)
conn = psycopg2.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    database="postgres"  # Kết nối tới database mặc định
)

# Đặt autocommit để có thể tạo database
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor()

# Kiểm tra xem database đã tồn tại chưa
cursor.execute("SELECT 1 FROM pg_database WHERE datname='vnpt_talent_hub'")
exists = cursor.fetchone()

if not exists:
    cursor.execute("CREATE DATABASE vnpt_talent_hub")
    print("✓ Đã tạo database 'vnpt_talent_hub' thành công!")
else:
    print("✓ Database 'vnpt_talent_hub' đã tồn tại.")

cursor.close()
conn.close()

print("\nBây giờ chạy: python scripts/create_tables.py")
