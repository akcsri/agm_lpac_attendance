# AGM/LPAC Attendance Management System

AGMとLPACの出席管理システム（PostgreSQL対応版）

## 概要

このアプリケーションは、AGM（Annual General Meeting）とLPACミーティングの参加者情報を管理するシステムです。

### 主な機能

- **User1**: AGMの出席管理のみ
- **User2**: AGMとLPACの両方の出席管理
- **Admin**: 全参加者の閲覧とCSVエクスポート

## システム要件

- Python 3.8+
- PostgreSQL 12+ (Render等のクラウド環境推奨)
- Flask 2.0+

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

Renderの環境変数で以下を設定:

```
DATABASE_URL=postgresql://...  # PostgreSQLのINTERNAL URL
SECRET_KEY=ランダムな長い文字列
```

### 3. データベース初期化

```bash
# 方法1: 初期化スクリプト
python init_db.py

# 方法2: テーブル再作成（既存データ削除）
python simple_recreate.py
```

### 4. ユーザー作成

```bash
# 管理者ユーザー
python create_user.py admin admin123 --role admin

# User1 (AGMのみ)
python create_user.py yamada pass123 --role user1

# User2 (AGM + LPAC)
python create_user.py tanaka pass456 --role user2
```

## Renderへのデプロイ

### 1. PostgreSQLデータベース作成

1. Renderダッシュボードで「New PostgreSQL」
2. データベース名: `agm-lpac-attendance-db`
3. リージョン: お好みの場所
4. 作成後、**Internal Database URL**をコピー

### 2. Web Serviceの作成

1. Renderダッシュボードで「New Web Service」
2. GitHubリポジトリを接続
3. 設定:
   - **Name**: agm-lpac-attendance
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

### 3. 環境変数の設定

Web Serviceの「Environment」タブで:

```
DATABASE_URL = [PostgreSQLのInternal Database URL]
SECRET_KEY = [ランダムな長い文字列]
```

### 4. デプロイ後の初期設定

Renderの「Shell」タブで:

```bash
# データベース初期化
python init_db.py

# ユーザー作成
python create_user.py admin adminpass123 --role admin
python create_user.py user1 pass123 --role user1
python create_user.py user2 pass456 --role user2

# 確認
python list_users.py
```

## 管理スクリプト

### ユーザー管理

```bash
# ユーザー一覧表示
python list_users.py

# ユーザー作成
python create_user.py ユーザー名 パスワード --role [admin|user1|user2]

# パスワードリセット
python reset_password.py ユーザー名 新しいパスワード

# ユーザー削除
python delete_user.py ユーザー名
```

### トラブルシューティング

```bash
# ログイン問題のデバッグ
python debug_login.py [ユーザー名]

# テーブル再作成（データ削除注意）
python simple_recreate.py
```

## アップグレード手順（SQLite → PostgreSQL）

既存のSQLite版からPostgreSQLへ移行する場合:

1. PostgreSQLデータベースを作成
2. `DATABASE_URL`環境変数を設定
3. `simple_recreate.py`でテーブル作成
4. ユーザーを再作成
5. 必要に応じて参加者データを手動でインポート

## ディレクトリ構成

```
agm_lpac_attendance/
├── app.py              # メインアプリケーション
├── models.py           # データベースモデル
├── requirements.txt    # 依存パッケージ
├── templates/          # HTMLテンプレート
│   ├── login.html
│   ├── index.html
│   ├── user1_dashboard.html
│   ├── user2_dashboard.html
│   └── admin_dashboard.html
├── static/             # 静的ファイル
│   └── logo.png
└── [管理スクリプト]
    ├── init_db.py
    ├── create_user.py
    ├── list_users.py
    ├── reset_password.py
    ├── delete_user.py
    ├── debug_login.py
    └── simple_recreate.py
```

## トラブルシューティング

### ログインできない

```bash
# デバッグツールを実行
python debug_login.py admin

# パスワードをリセット
python reset_password.py admin newpassword
```

### データベース接続エラー

1. `DATABASE_URL`が正しく設定されているか確認
2. **Internal Database URL**を使用しているか確認
3. PostgreSQLデータベースが起動しているか確認

### テーブルが作成されない

```bash
# 手動でテーブル作成
python simple_recreate.py
```

### パスワードハッシュのエラー

- models.pyで`password_hash`が`VARCHAR(255)`になっているか確認
- 必要に応じて`simple_recreate.py`でテーブル再作成

## 重要な注意事項

1. **SQLiteは使用しない**: Renderではデータが消えるため必ずPostgreSQLを使用
2. **Internal Database URL**: External URLではなくInternal URLを使用
3. **SECRET_KEY**: 本番環境では必ず強力なランダム文字列を設定
4. **password_hash**: VARCHAR(255)が必須（新しいWerkzeugのscryptハッシュ対応）

## サポート

問題が発生した場合は、以下を確認してください:

1. Renderのログを確認
2. `debug_login.py`でデバッグ情報を取得
3. `list_users.py`でユーザー情報を確認
4. DATABASE_URLとSECRET_KEYの設定を確認

## ライセンス

Private/Internal Use
