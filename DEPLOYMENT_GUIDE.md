# AGM/LPAC Attendance - Renderデプロイメントガイド

## 前提条件

- GitHubアカウント
- Renderアカウント
- コードがGitHubリポジトリにプッシュされている

## ステップ1: PostgreSQLデータベースの作成

1. **Renderダッシュボード**にログイン: https://dashboard.render.com/

2. **New PostgreSQL**をクリック

3. データベース設定:
   - **Name**: `agm-lpac-attendance-db`
   - **Database**: `agm_lpac_db` (自動生成でOK)
   - **User**: `agm_lpac_user` (自動生成でOK)
   - **Region**: お好みのリージョン (Tokyo推奨)
   - **PostgreSQL Version**: 15以上
   - **Plan**: Free (または必要に応じて有料プラン)

4. **Create Database**をクリック

5. データベース作成後、**Info**タブで以下を確認:
   - ✅ **Internal Database URL**をコピー (これを使用)
   - ❌ External Database URLはRenderアプリでは使用しない

   ```
   Internal Database URL:
   postgresql://user:pass@dpg-xxxxx/dbname
   ```

## ステップ2: Web Serviceの作成

1. Renderダッシュボードで**New Web Service**をクリック

2. **Connect GitHub**でリポジトリを選択
   - リポジトリ: `agm_lpac_attendance`

3. Web Service設定:
   
   **Basic Information:**
   - **Name**: `agm-lpac-attendance`
   - **Region**: データベースと同じリージョン
   - **Branch**: `main` (またはデプロイしたいブランチ)
   - **Root Directory**: 空欄 (ルートディレクトリの場合)

   **Build Settings:**
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```
     gunicorn app:app
     ```

   **Plan:**
   - Free (または必要に応じて有料プラン)

4. **Create Web Service**をクリック

## ステップ3: 環境変数の設定

Web Serviceが作成されたら、**Environment**タブで環境変数を追加:

1. **DATABASE_URL**
   ```
   Key: DATABASE_URL
   Value: [ステップ1でコピーしたInternal Database URL]
   ```
   
   ⚠️ 重要: **Internal Database URL**を使用すること！

2. **SECRET_KEY**
   ```
   Key: SECRET_KEY
   Value: [ランダムな長い文字列]
   ```
   
   例: `mysecretkey123456789abcdefghijk`
   
   より強力なキーを生成するには:
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```

3. **Save Changes**をクリック

環境変数を保存すると、アプリが自動的に再デプロイされます。

## ステップ4: デプロイの確認

1. **Logs**タブで以下の出力を確認:
   ```
   📊 DATABASE_URL detected: postgresql://...
   ✓ Render PostgreSQL detected
   ✅ Database tables created/verified successfully.
   ✅ Using PostgreSQL database
   ```

2. エラーがないことを確認

3. URLをクリックしてアプリにアクセス
   - URL例: `https://agm-lpac-attendance.onrender.com`

## ステップ5: 初期ユーザーの作成

デプロイ成功後、**Shell**タブを開いて初期ユーザーを作成:

### 1. データベース初期化の確認

```bash
python list_users.py
```

ユーザーが0人と表示されれば正常です。

### 2. 管理者ユーザーの作成

```bash
python create_user.py admin YourSecurePassword123 --role admin
```

出力例:
```
✅ ユーザー 'admin' を作成しました。
   ログイン情報:
   - ユーザー名: admin
   - パスワード: YourSecurePassword123
   - ロール: admin
```

### 3. 一般ユーザーの作成

```bash
# User1 (AGMのみ)
python create_user.py user1 Pass123 --role user1

# User2 (AGM + LPAC)
python create_user.py user2 Pass456 --role user2
```

### 4. ユーザー一覧の確認

```bash
python list_users.py
```

## ステップ6: ログインテスト

1. ブラウザでアプリのURLを開く

2. 作成したユーザーでログイン:
   - ユーザー名: `admin`
   - パスワード: `YourSecurePassword123`

3. ログイン成功を確認

## トラブルシューティング

### デプロイが失敗する

**症状**: Build failedまたはDeploy failed

**原因と解決策**:

1. **requirements.txtの問題**
   - ファイルが存在するか確認
   - 正しいパッケージが記載されているか確認

2. **Pythonバージョン**
   - Environment が `Python 3` になっているか確認

3. **Build Command**
   ```
   pip install -r requirements.txt
   ```

4. **Start Command**
   ```
   gunicorn app:app
   ```

### データベース接続エラー

**症状**: ログに `DATABASE_URL` エラー

**解決策**:

1. **Internal Database URL** を使用しているか確認
   - ❌ External URL: `postgres://...@oregon-postgres.render.com:5432/...`
   - ✅ Internal URL: `postgres://...@dpg-xxxxx/...`

2. DATABASE_URLが正しく設定されているか確認
   ```bash
   echo $DATABASE_URL
   ```

3. データベースが起動しているか確認

### テーブルが作成されない

**症状**: ログに "no such table" エラー

**解決策**:

```bash
# Shellで実行
python simple_recreate.py
```

### ログインできない

**症状**: "ログイン失敗" メッセージ

**解決策**:

1. **パスワードを確認**
   ```bash
   python debug_login.py admin
   ```

2. **パスワードをリセット**
   ```bash
   python reset_password.py admin NewPassword123
   ```

3. **ユーザーが存在するか確認**
   ```bash
   python list_users.py
   ```

### Password hash too long エラー

**症状**: `password_hash` が150文字を超える

**解決策**:

1. models.pyで `password_hash = db.Column(db.String(255), ...)` になっているか確認

2. テーブル再作成:
   ```bash
   python simple_recreate.py
   python create_user.py admin password123 --role admin
   ```

## 更新とメンテナンス

### コードの更新

1. GitHubにプッシュ
2. Renderが自動的に再デプロイ
3. データは保持される（PostgreSQLのため）

### データベースのバックアップ

Renderの「Backups」タブでバックアップを作成できます。

### ログの確認

**Logs**タブでリアルタイムログを確認:
- アプリケーションのエラー
- データベース接続状態
- ユーザーのログイン状況

## セキュリティチェックリスト

- ✅ SECRET_KEYが強力なランダム文字列
- ✅ DATABASE_URLがInternal URL
- ✅ 管理者パスワードが強力
- ✅ 本番環境でDEBUG=False
- ✅ 不要なユーザーが削除されている

## よくある質問

### Q: SQLiteとPostgreSQLの違いは？

A: Renderでは:
- SQLite: デプロイ時にデータが消える ❌
- PostgreSQL: データが永続化される ✅

### Q: Internal URLとExternal URLの違いは？

A: 
- Internal URL: Render内部ネットワーク（高速・無料）✅
- External URL: 外部からのアクセス（遅い・制限あり）❌

### Q: 無料プランの制限は？

A:
- PostgreSQL: 90日間の非アクティブで削除
- Web Service: スリープあり（アクセスで起動）
- データベース容量: 1GB

### Q: ユーザーのロールの違いは？

A:
- **admin**: 全参加者の閲覧、CSV出力
- **user1**: AGM出席管理のみ
- **user2**: AGM + LPAC出席管理

## サポート

問題が解決しない場合:

1. Renderのログを確認
2. `debug_login.py`を実行
3. DATABASE_URLとSECRET_KEYを再確認
4. テーブルを再作成

## まとめ

これで agm_lpac_attendance アプリケーションがRenderにデプロイされました！

主なポイント:
- ✅ PostgreSQLデータベース作成
- ✅ Web Service作成
- ✅ 環境変数設定（DATABASE_URL, SECRET_KEY）
- ✅ 初期ユーザー作成
- ✅ ログインテスト

お疲れ様でした！
