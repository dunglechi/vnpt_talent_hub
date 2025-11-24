"""
Utility script to create SSH tunnel to remote database server
Keep this running while working with the database
"""

import subprocess
import time
import sys

# Thông tin SSH
ssh_host = "one.vnptacademy.com.vn"
ssh_port = "2222"
ssh_user = "admin"
ssh_password = "Cntt@2025"

print("=" * 60)
print("SSH Tunnel Setup - VNPT Talent Hub")
print("=" * 60)
print(f"\nKết nối: {ssh_user}@{ssh_host}:{ssh_port}")
print("Port forwarding: 5432:localhost:5432")
print("\n⚠️  Vui lòng nhập password khi được hỏi: Cntt@2025")
print("\n✓ Giữ cửa sổ này mở. Nhấn Ctrl+C để dừng tunnel.\n")
print("=" * 60)

try:
    # Tạo SSH tunnel
    process = subprocess.Popen(
        ["ssh", "-L", "5432:localhost:5432", 
         f"{ssh_user}@{ssh_host}", "-p", ssh_port, "-N"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print("✓ SSH tunnel đang chạy...")
    print("\nBây giờ bạn có thể chạy:")
    print("  - python scripts/create_database.py")
    print("  - python scripts/create_tables.py")
    print("  - python scripts/import_data.py")
    
    # Giữ script chạy
    process.wait()
    
except KeyboardInterrupt:
    print("\n\nĐang đóng SSH tunnel...")
    process.terminate()
    print("✓ SSH tunnel đã đóng.")
    sys.exit(0)
