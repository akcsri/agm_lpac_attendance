# メール通知機能設定ガイド

## 概要

agm_lpac_attendanceは、ユーザーのアクション（ログイン、ログアウト、参加者の追加・更新・削除、CSVインポート）を管理者にメールで通知します。

## 必要な環境変数

### メールサーバー設定

```bash
MAIL_SERVER=smtp.gmail.com          # SMTPサーバーアドレス
MAIL_PORT=587                         # SMTPポート（通常587）
MAIL_USE_TLS=True                     # TLS使用（True/False）
MAIL_USERNAME=your_email@gmail.com    # 送信元メールアドレス
MAIL_PASSWORD=your_app_password       # アプリパスワード
MAIL_DEFAULT_SENDER=your_email@gmail.com  # 送信者名（省略可）
```

### 通知先メールアドレス（複数指定可能）

```bash
# 単一アドレス
NOTIFICATION_EMAILS=admin@example.com

# 複数アドレス（カンマ区切り）
NOTIFICATION_EMAILS=admin1@example.com,admin2@example.com,admin3@example.com
```

## Renderでの設定方法

### ステップ1: Gmailアプリパスワードの取得

1. **Googleアカウント**にログイン
2. **セキュリティ** → **2段階認証プロセス**を有効化
3. **アプリパスワード**を作成
   - アプリ: メール
   - デバイス: その他（カスタム名）
4. 生成された16文字のパスワードをコピー

### ステップ2: Renderで環境変数を設定

Web Serviceの**Environment**タブで以下を追加：

```
MAIL_SERVER = smtp.gmail.com
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = your_email@gmail.com
MAIL_PASSWORD = [Gmailアプリパスワード]
NOTIFICATION_EMAILS = admin1@example.com,admin2@example.com
```

### ステップ3: デプロイ

環境変数を保存すると、自動的に再デプロイされます。

## Gmail以外のメールサービス

### SendGrid

```bash
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=[SendGrid APIキー]
NOTIFICATION_EMAILS=admin@example.com
```

### Outlook/Office 365

```bash
MAIL_SERVER=smtp.office365.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@outlook.com
MAIL_PASSWORD=[パスワード]
NOTIFICATION_EMAILS=admin@example.com
```

### カスタムSMTPサーバー

```bash
MAIL_SERVER=smtp.your-domain.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=noreply@your-domain.com
MAIL_PASSWORD=[パスワード]
NOTIFICATION_EMAILS=admin@your-domain.com
```

## 通知されるアクション

### 1. ユーザーログイン

```
件名: [AGM/LPAC Attendance] ユーザーログイン
内容:
  ユーザー: yamada
  時刻: 2025-11-25 12:34:56
  ロール: user1
```

### 2. ユーザーログアウト

```
件名: [AGM/LPAC Attendance] ユーザーログアウト
内容:
  ユーザー: yamada
  時刻: 2025-11-25 13:45:12
```

### 3. 参加者追加

```
件名: [AGM/LPAC Attendance] 参加者追加
内容:
  操作: 参加者追加
  ユーザー: yamada
  時刻: 2025-11-25 14:00:00
  
  役職: 部長
  氏名: 山田太郎
  メール: yamada@example.com
  AGMステータス: 出席（対面）
  LPACステータス: 出席（オンライン）
  質問: 駐車場について
```

### 4. 参加者情報更新

```
件名: [AGM/LPAC Attendance] 参加者情報更新
内容:
  操作: 参加者情報更新
  ユーザー: yamada
  時刻: 2025-11-25 15:30:00
  
  【変更前】
  部長 - 山田太郎 - yamada@example.com - AGM:出席（対面） LPAC:欠席
  
  【変更後】
  部長 - 山田太郎 - yamada@example.com
  AGM: 出席（オンライン）, LPAC: 出席（対面）
  質問: （なし）
```

### 5. 参加者ステータス更新

```
件名: [AGM/LPAC Attendance] 参加者ステータス更新
内容:
  操作: ステータス更新
  ユーザー: yamada
  時刻: 2025-11-25 16:00:00
  
  参加者: 部長 - 山田太郎
  変更内容:
  AGM: 出席（対面） → 出席（オンライン）
```

### 6. 参加者削除

```
件名: [AGM/LPAC Attendance] 参加者削除
内容:
  操作: 参加者削除
  ユーザー: yamada
  時刻: 2025-11-25 17:00:00
  
  削除された参加者: 部長 - 山田太郎 - yamada@example.com
```

### 7. CSVインポート

```
件名: [AGM/LPAC Attendance] CSVインポート実行
内容:
  操作: CSVインポート
  実行ユーザー: admin
  時刻: 2025-11-25 18:00:00
  
  インポート成功: 15件
  エラー: 2件
  
  エラー詳細:
  行3: ユーザー 'user99' が見つかりません
  行7: 必須項目が不足しています
```

### 8. ユーザーCSVインポート

```
件名: [AGM/LPAC Attendance] ユーザーCSVインポート実行
内容:
  操作: ユーザーインポート
  実行ユーザー: admin
  時刻: 2025-11-25 19:00:00
  
  インポート成功: 10件
  エラー: 0件
```

## トラブルシューティング

### メールが送信されない

**症状**: ログに「⚠️ NOTIFICATION_EMAILS not configured」

**解決策**:
```bash
# NOTIFICATION_EMAILSが設定されているか確認
echo $NOTIFICATION_EMAILS

# 設定されていない場合、環境変数を追加
NOTIFICATION_EMAILS=admin@example.com
```

### メール認証エラー

**症状**: ログに「❌ Email sending failed: Authentication failed」

**解決策**:
1. Gmailアプリパスワードを再生成
2. MAIL_USERNAMEとMAIL_PASSWORDを確認
3. 2段階認証が有効か確認

### 一部のアドレスにのみ送信される

**症状**: 複数指定したが1件のみ届く

**原因**: カンマの前後にスペースがある

**解決策**:
```bash
# ❌ 間違い
NOTIFICATION_EMAILS=admin1@example.com, admin2@example.com

# ✅ 正しい
NOTIFICATION_EMAILS=admin1@example.com,admin2@example.com
```

### GmailでブロックされるGmail

**症状**: ログに「❌ Email sending failed: SMTP authentication error」

**解決策**:
1. 「安全性の低いアプリのアクセス」を有効化（非推奨）
2. **推奨**: アプリパスワードを使用

### メールが迷惑メールフォルダに入る

**解決策**:
1. 送信者を連絡先に追加
2. メールフィルターを設定
3. SPF/DKIM設定（カスタムドメインの場合）

## テスト方法

### 1. 環境変数の確認

```bash
# Render Shellで実行
python << 'PYTHON'
import os
print("MAIL_SERVER:", os.environ.get('MAIL_SERVER'))
print("MAIL_USERNAME:", os.environ.get('MAIL_USERNAME'))
print("NOTIFICATION_EMAILS:", os.environ.get('NOTIFICATION_EMAILS'))
PYTHON
```

### 2. テストログイン

1. アプリケーションにログイン
2. 通知メールが届くことを確認
3. 件名とログイン情報を確認

### 3. テスト参加者追加

1. 参加者を1件追加
2. 通知メールが届くことを確認
3. 参加者情報が正しいか確認

## セキュリティのベストプラクティス

### 1. アプリパスワードを使用

- 通常のパスワードを使用しない
- Gmailアプリパスワードを生成
- 定期的に更新

### 2. 環境変数で管理

- パスワードをコードに埋め込まない
- 環境変数で管理
- Gitにコミットしない

### 3. TLSを有効化

```bash
MAIL_USE_TLS=True  # 必ず有効化
```

### 4. 通知先の制限

- 必要最小限のアドレスのみ
- 社内メールアドレスを使用
- 個人メールアドレスは避ける

## まとめ

メール通知機能により：
- ✅ リアルタイムで活動を監視
- ✅ 不正アクセスを検知
- ✅ データ変更を追跡
- ✅ 複数の管理者に同時通知
- ✅ 監査ログとして活用

管理者の状況把握が大幅に向上します！

## サポート

問題が発生した場合:
1. 環境変数の設定を確認
2. Renderのログを確認
3. アプリパスワードを再生成
4. テストメールを送信
