# AGM/LPAC Attendance - PostgreSQL移行完了 ✅

## 変更サマリー

agm_lpac_attendanceをSQLiteからPostgreSQL方式に完全移行しました。

### 主な変更点

#### 1. データベース対応 🗄️
- ✅ PostgreSQL対応（Render対応）
- ✅ DATABASE_URL環境変数サポート
- ✅ SQLiteフォールバック（ローカル開発用）
- ✅ 起動時の自動テーブル作成

#### 2. モデル更新 📊
- ✅ `password_hash`: VARCHAR(150) → VARCHAR(255)
- ✅ Werkzeugの新しいscryptハッシュ対応
- ✅ AGMとLPACのステータス管理

#### 3. 管理スクリプト 🛠️
以下のスクリプトを追加:
- `create_user.py` - ユーザー作成
- `list_users.py` - ユーザー一覧表示
- `delete_user.py` - ユーザー削除
- `reset_password.py` - パスワードリセット
- `debug_login.py` - ログイン問題デバッグ
- `init_db.py` - データベース初期化
- `simple_recreate.py` - テーブル再作成
- `update_schema.py` - スキーマ更新

#### 4. ドキュメント 📚
- ✅ README.md - 包括的な説明
- ✅ DEPLOYMENT_GUIDE.md - Renderデプロイ手順

#### 5. CSVインポート/エクスポート機能 📥📤
- ✅ 参加者CSVエクスポート機能
- ✅ 参加者CSVインポート機能（一括登録/更新）
- ✅ ユーザーCSVインポート機能（一括ユーザー作成）
- ✅ テンプレートファイル提供
- ✅ UTF-8 BOM対応（Excel互換）

## ファイル一覧

### コアファイル
- `app.py` - メインアプリケーション（PostgreSQL対応）
- `models.py` - データモデル（password_hash 255文字）
- `requirements.txt` - 依存パッケージ（psycopg2-binary追加）

### 管理スクリプト
- `create_user.py` - ユーザー作成
- `list_users.py` - ユーザー一覧
- `delete_user.py` - ユーザー削除
- `reset_password.py` - パスワードリセット
- `debug_login.py` - デバッグツール
- `init_db.py` - DB初期化
- `simple_recreate.py` - テーブル再作成
- `update_schema.py` - スキーマ更新

### テンプレート
- `templates/login.html` - ログインページ
- `templates/index.html` - ホームページ
- `templates/admin_dashboard.html` - 管理者ダッシュボード（CSVインポートボタン付き）
- `templates/import_csv.html` - 参加者CSVインポート画面
- `templates/import_users.html` - ユーザーCSVインポート画面
- (その他のテンプレートは既存のものを使用)

### CSVテンプレート
- `users_template.csv` - ユーザーインポート用テンプレート
- `participants_template.csv` - 参加者インポート用テンプレート

### ドキュメント
- `README.md` - システム概要（CSVインポート機能説明付き）
- `DEPLOYMENT_GUIDE.md` - デプロイ手順
- `UPGRADE_SUMMARY.md` - このファイル

## 次のステップ

### 1. Renderへのデプロイ

```bash
# 1. PostgreSQLデータベース作成
# Renderダッシュボードで: agm-lpac-attendance-db

# 2. Web Service作成
# GitHubリポジトリを接続

# 3. 環境変数設定
DATABASE_URL = [Internal Database URL]
SECRET_KEY = [ランダムな文字列]

# 4. デプロイ
# 自動的にデプロイされます
```

### 2. 初期ユーザー作成

```bash
# Render Shellで実行
python create_user.py admin adminpass123 --role admin
python create_user.py user1 pass123 --role user1
python create_user.py user2 pass456 --role user2
```

### 3. 動作確認

```bash
# ユーザー一覧確認
python list_users.py

# ログインテスト
# ブラウザでアクセスしてログイン
```

## 重要な注意事項 ⚠️

1. **Internal Database URL使用**
   - External URLではなくInternal URLを使用
   - Render内部ネットワークで高速・安定

2. **SECRET_KEY設定必須**
   - デフォルト値は使用しない
   - ランダムな長い文字列を生成

3. **password_hash 255文字**
   - 新しいWerkzeugのscryptハッシュ対応
   - 既存DBの場合は`simple_recreate.py`で再作成

4. **データの永続化**
   - PostgreSQL使用でデータが消えない
   - SQLiteは使用しない（Renderでは非推奨）

## トラブルシューティング

### ログインできない
```bash
python debug_login.py admin
python reset_password.py admin newpassword
```

### テーブルが作成されない
```bash
python simple_recreate.py
```

### データベース接続エラー
- DATABASE_URLを確認
- Internal URLを使用しているか確認
- PostgreSQLが起動しているか確認

## 技術仕様

### 環境
- Python 3.8+
- Flask 2.0+
- PostgreSQL 12+
- Gunicorn (本番環境)

### 依存パッケージ
```
Flask>=2.0
Flask-Login>=0.6
flask_sqlalchemy>=3.0
SQLAlchemy>=1.4,<2.0
psycopg2-binary>=2.9.0
gunicorn
```

### データベーススキーマ

**user テーブル:**
- id: SERIAL PRIMARY KEY
- username: VARCHAR(150) UNIQUE
- password_hash: VARCHAR(255)
- role: VARCHAR(50)

**participant テーブル:**
- id: SERIAL PRIMARY KEY
- name: VARCHAR(150)
- email: VARCHAR(150)
- position: VARCHAR(150)
- questions: TEXT
- agm_status: VARCHAR(50)
- lpac_status: VARCHAR(50)
- user_id: INTEGER (FK to user)

## 完了チェックリスト ✅

- ✅ PostgreSQL対応完了
- ✅ password_hash 255文字対応
- ✅ 管理スクリプト一式作成
- ✅ ドキュメント作成
- ✅ テンプレート更新
- ✅ requirements.txt更新
- ✅ エラーハンドリング強化
- ✅ ログ出力改善

## 移行前との比較

### Before (SQLite版)
- ❌ Renderでデータが消える
- ❌ password_hash 150文字（不足）
- ❌ 管理ツールなし
- ❌ ドキュメント不足

### After (PostgreSQL版)
- ✅ データ永続化
- ✅ password_hash 255文字
- ✅ 豊富な管理ツール
- ✅ 詳細なドキュメント
- ✅ トラブルシューティング対応

## サポート

問題が発生した場合:
1. README.mdを確認
2. DEPLOYMENT_GUIDE.mdを確認
3. `debug_login.py`でデバッグ
4. Renderのログを確認

---

**移行完了日**: 2025年11月25日
**バージョン**: PostgreSQL Edition v1.0
**ステータス**: ✅ Production Ready
