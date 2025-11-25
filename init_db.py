#!/usr/bin/env python3
"""
データベース初期化スクリプト

使い方:
  python init_db.py
"""

from app import app
from models import db

with app.app_context():
    db.create_all()
    print("=" * 60)
    print("✅ Database initialized.")
    print("=" * 60)
    print()
    print("テーブルが作成されました:")
    print("  - user (password_hash: VARCHAR(255))")
    print("  - participant (agm_status, lpac_status)")
    print()
    print("次のステップ:")
    print("  python create_user.py admin admin123 --role admin")
    print("  python create_user.py user1 pass123 --role user1")
    print("  python create_user.py user2 pass456 --role user2")
    print()
