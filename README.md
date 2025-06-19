## 【完全版】ストアカ日程追加・削除 自動化スクリプト 導入マニュアル

このマニュアルは、面倒なストアカの講座日程の追加・削除作業をPythonスクリプトで自動化するための手順書です。

### 全体の流れ

1.  **【事前準備】必要なツールをインストールする**
    *   お使いのMacに開発ツールやPythonがインストールされているかを確認し、なければインストールします。
2.  **【初回のみ】認証情報ファイルを作成する**
    *   スクリプトがあなたの代わりにログインするための「鍵」となるファイルを作成します。
3.  **【設定】スクリプトを自分の講座用に設定する**
    *   あなたの講座情報に合わせて、日程追加スクリプトの一部を書き換えます。
4.  **【実行】自動化スクリプトを動かす**
    *   コマンド一つで、日程の追加または削除を行います。

---

### ステップ1：【事前準備】必要なツールのインストール

お使いのMacに、Pythonと自動化ライブラリをインストールします。

#### 1-1. Homebrewのインストール確認と実行
Mac用のパッケージ管理ツール「Homebrew」を準備します。

まず、ターミナルを開き、以下のコマンドでHomebrewがインストール済みか確認します。
```bash
command -v brew
```
*   `/opt/homebrew/bin/brew` のようなパスが表示されれば、**インストール済み**です。次の「1-2. Pythonのインストール確認」に進んでください。
*   何も表示されなければ、**未インストール**です。以下のコマンドを貼り付けて実行し、Homebrewをインストールしてください。
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```

#### 1-2. Pythonのインストール確認と実行
次に、Homebrewを使ってPythonをインストールします。

まず、ターミナルでPythonがインストール済みか確認します。
```bash
python3 --version
```
*   `Python 3.x.x` のようにバージョンが表示されれば、**インストール済み**です。次の「1-3. プロジェクトフォルダの準備」に進んでください。
*   `command not found` のようなエラーが出れば、**未インストール**です。以下のコマンドでPythonをインストールしてください。
    ```bash
    brew install python3
    ```
    完了したら、ターミナルを一度完全に終了し、再起動してください。

#### 1-3. プロジェクトフォルダの準備
作業用のフォルダを作成し、そこに移動します。
```bash
# 例: デスクトップにフォルダを作成
mkdir stoc-aca-automation
cd stoc-aca-automation
```

#### 1-4. 仮想環境の作成と有効化
プロジェクト専用のクリーンな環境を作ります。
```bash
# 仮想環境を作成 (フォルダ内で初回のみ)
python3 -m venv .venv

# 仮想環境を有効化 (このフォルダで作業する際は毎回実行)
source .venv/bin/activate
```
ターミナルの行頭に `(.venv)` と表示されれば、仮想環境が有効化された状態です。

#### 1-5. Playwrightのインストール
仮想環境が有効な状態で、自動化に必要なライブラリとブラウザをインストールします。
```bash
# ライブラリのインストール
pip install playwright

# 自動操作用のブラウザをインストール
playwright install
```

---

### ステップ2：【初回のみ】認証情報ファイルを作成する

スクリプトにログイン操作を代行させるための「認証情報ファイル」を作成します。この作業は**一番最初に一度だけ**行います。

#### 2-1. 認証スクリプトの作成
`stoc-aca-automation`フォルダ内に、`save_auth.py` という名前でファイルを作成し、以下の内容を貼り付けます。

**`save_auth.py`**
```python
from playwright.sync_api import sync_playwright, expect

AUTH_FILE_PATH = 'playwright_auth.json'
# ストアカのログインページURL
LOGIN_PAGE_URL = "https://www.street-academy.com/d/users/sign_in"
# ログイン成功後に遷移する先生用ダッシュボードのURL
LOGIN_SUCCESS_URL = "https://www.street-academy.com/dashboard/steachers" 

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    print(f"ストアカのログインページを開きます: {LOGIN_PAGE_URL}")
    page.goto(LOGIN_PAGE_URL)
    
    print("\nブラウザ上で手動でログインしてください。")
    print(f"ログイン後、'{LOGIN_SUCCESS_URL}' に遷移すると自動的に終了します。")
    
    try:
        expect(page).to_have_url(LOGIN_SUCCESS_URL, timeout=300000) # 5分待機
        print("\nログインを検知しました。")
    except Exception as e:
        print(f"\nログインがタイムアウトまたは検知できませんでした: {e}")
        browser.close()
        exit()

    context.storage_state(path=AUTH_FILE_PATH)
    print(f"認証情報を {AUTH_FILE_PATH} に保存しました。")
    browser.close()
```

#### 2-2. 認証スクリプトの実行
ターミナルで以下のコマンドを実行します。
```bash
# 仮想環境が有効なことを確認 (.venv が表示されているか)
python save_auth.py
```
するとブラウザが起動するので、**手動でストアカにログイン**してください。ログインが完了すると、プログラムは自動で終了し、フォルダ内に`playwright_auth.json`ファイルが作成されます。

---

### ステップ3：【設定】スクリプトの準備と設定

自動化で使う2つのスクリプト（追加用と削除用）を作成・設定します。

#### 3-1. 日程「追加」スクリプトの作成
`stoc-aca-automation`フォルダ内に、`main.py` という名前でファイルを作成し、以下の内容を貼り付けます。

**`main.py`**
```python
import sys
import time
from datetime import date, timedelta
from playwright.sync_api import sync_playwright, expect

# --- ★★★★★ ここから設定項目 ★★★★★ ---
# 認証情報ファイルのパス (このままでOK)
AUTH_FILE_PATH = 'playwright_auth.json'

# ①：あなたの日程追加ページのURLに書き換えてください
# 例: 'https://www.street-academy.com/session_details/new_multi_session?classdetailid=123456'
TARGET_URL = 'https://www.street-academy.com/session_details/new_multi_session?classdetailid=123456'

# ②：あなたの緊急連絡先(電話番号)に書き換えてください
EMERGENCY_CONTACT = '090-1234-5678' 

# ③：追加したい時間帯 (9時〜22時でよければ変更不要)
HOURS_TO_ADD = list(range(9, 23)) 
# --- ★★★★★ 設定項目はここまで ★★★★★ ---


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

def add_schedule_for_day(page, target_date):
    print(f"\n--- {target_date.strftime('%Y-%m-%d')} の日程を追加します ---")
    first_block = page.locator('div[data-repeater-item]').first
    
    print("最初の日付を設定中...")
    first_block.locator('select[name*="[session_startdate_year]"]').select_option(str(target_date.year))
    first_block.locator('select[name*="[session_startdate_month]"]').select_option(str(target_date.month))
    first_block.locator('select[name*="[session_startdate_day]"]').select_option(str(target_date.day))
    
    start_hour = HOURS_TO_ADD[0]
    end_hour = start_hour + 1
    first_block.locator('select.js_start_time_hour').select_option(str(start_hour))
    first_block.locator('select.js_end_time_hour').select_option(str(end_hour))
    print(f"{start_hour}:00 - {end_hour}:00 の日程を設定しました。")
    time.sleep(0.5)

    for hour in HOURS_TO_ADD[1:]:
        print(f"{hour}時の日程を追加します...")
        page.get_by_role("button", name="日程を複製する").click()
        last_block = page.locator('div[data-repeater-item]').last
        expect(last_block).to_be_visible()
        
        start_hour = hour
        end_hour = start_hour + 1 if start_hour < 23 else 23
        last_block.locator('select.js_start_time_hour').select_option(str(start_hour))
        last_block.locator('select.js_end_time_hour').select_option(str(end_hour))
        print(f"{start_hour}:00 - {end_hour}:00 の日程を設定しました。")

def run(start_date_str, end_date_str):
    try:
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
    except ValueError:
        print("エラー: 日付の形式が正しくありません。YYYY-MM-DD形式で指定してください。")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=AUTH_FILE_PATH)
        page = context.new_page()

        for single_date in daterange(start_date, end_date):
            print(f"ページにアクセスします: {TARGET_URL}")
            page.goto(TARGET_URL)
            print("ページが読み込まれるのを待っています...")
            expect(page.get_by_role("button", name="日程を複製する")).to_be_visible(timeout=30000)
            print("ページの読み込みが完了しました。")
            
            add_schedule_for_day(page, single_date)

            print("\n緊急連絡先を入力します...")
            page.locator("#session_detail_multi_form_emergency_contact").fill(EMERGENCY_CONTACT)
            
            print("プレビュー画面へ進みます...")
            page.get_by_role("button", name="プレビュー画面で確認").click()
            
            print("内容を確定します...")
            confirm_button = page.get_by_role("button", name="確定")
            expect(confirm_button).to_be_visible(timeout=15000)
            confirm_button.click()

            print("完了メッセージを待っています...")
            expect(page.get_by_text("講座の予約受付が開始されました！")).to_be_visible(timeout=20000)
            print(f"--- {single_date.strftime('%Y-%m-%d')} の日程追加が完了しました！ ---")
            time.sleep(3)

        print("\nすべての指定された期間の日程追加が完了しました。")
        browser.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使い方: python main.py YYYY-MM-DD YYYY-MM-DD")
        sys.exit(1)
    start_date_arg = sys.argv[1]
    end_date_arg = sys.argv[2]
    run(start_date_arg, end_date_arg)
```
**【重要】** 作成した`main.py`を開き、先頭部分の**設定項目（`TARGET_URL`と`EMERGENCY_CONTACT`）**を自分の情報に必ず書き換えてください。

#### 3-2. 日程「削除」スクリプトの作成
`stoc-aca-automation`フォルダ内に、`delete_schedules.py` という名前でファイルを作成し、以下の内容を貼り付けます。
（このスクリプトは特に設定を変更する必要はありません）

**`delete_schedules.py`**
```python
import sys
import time
from datetime import date, timedelta
from playwright.sync_api import sync_playwright, expect

# --- 設定項目 (認証ファイルのみ) ---
AUTH_FILE_PATH = 'playwright_auth.json'

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

def run(start_date_str, end_date_str):
    try:
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
    except ValueError:
        print("エラー: 日付の形式が正しくありません。YYYY-MM-DD形式で指定してください。")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=AUTH_FILE_PATH)
        page = context.new_page()

        for single_date in daterange(start_date, end_date):
            date_param = single_date.strftime('%Y-%-m-%-d')
            daily_schedule_url = f"https://www.street-academy.com/dashboard/steachers/manage_class_dates?date={date_param}"
            
            print(f"\n--- {single_date.strftime('%Y-%m-%d')} の日程削除を開始します ---")
            
            while True:
                print(f"日程一覧にアクセス中: {daily_schedule_url}")
                page.goto(daily_schedule_url, timeout=60000)
                page.wait_for_load_state('networkidle')
                
                schedule_links = page.locator('a.dashboard-session_container[href*="/show_attendance?sessiondetailid="]')
                
                if schedule_links.count() == 0:
                    no_schedule_text = page.locator("text=講座がありません")
                    if no_schedule_text.is_visible():
                        print("「講座がありません」と表示されています。")
                    else:
                        print("削除可能な日程は見つかりませんでした。")
                    print(f"{single_date.strftime('%Y-%m-%d')} の処理を終了します。")
                    break
                
                first_schedule_text = schedule_links.first.inner_text()
                print(f"  - 削除対象: {first_schedule_text.strip().replace('\n', ' ')}")
                
                schedule_links.first.click()

                cancel_button_1 = page.get_by_role("link", name="開催をキャンセルする")
                expect(cancel_button_1).to_be_visible(timeout=15000)
                cancel_button_1.click()
                
                modal_cancel_button = page.locator("#sa-modal-cancel").get_by_role("button", name="開催キャンセル")
                expect(modal_cancel_button).to_be_visible()

                page.once("dialog", lambda dialog: dialog.accept())
                modal_cancel_button.click()

                print("  - キャンセル処理を実行しました。次の処理に進みます。")
                time.sleep(3)

        print("\nすべての指定された期間の日程削除が完了しました。")
        browser.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使い方: python delete_schedules.py YYYY-MM-DD YYYY-MM-DD")
        sys.exit(1)
    
    start_date_arg = sys.argv[1]
    end_date_arg = sys.argv[2]
    run(start_date_arg, end_date_arg)
```

---

### ステップ4：【実行】自動化スクリプトを動かす

設定が完了したら、いつでもスクリプトを実行できます。

1.  ターミナルで`stoc-aca-automation`フォルダにいることを確認します。
2.  仮想環境を有効化します。（もし無効になっていたら）
    ```bash
    source .venv/bin/activate
    ```
3.  実行したい処理に合わせて、以下のコマンドを実行します。

#### ■ 日程を追加する場合
`python main.py`コマンドに続けて、**追加したい期間の開始日**と**終了日**を `YYYY-MM-DD` 形式で指定します。
```bash
# 2025年10月10日の1日だけ追加する場合
python main.py 2025-10-10 2025-10-10

# 2025年11月1日から11月7日まで追加する場合
python main.py 2025-11-01 2025-11-07
```

#### ■ 日程を削除する場合
**【注意】削除した日程は元に戻せません。日付をよく確認して慎重に実行してください。**
`python delete_schedules.py`コマンドに続けて、**削除したい期間の開始日**と**終了日**を指定します。
```bash
# 2025年9月2日の日程をすべて削除する場合
python delete_schedules.py 2025-09-02 2025-09-02

# 2025年12月20日から12月25日までの日程をすべて削除する場合
python delete_schedules.py 2025-12-20 2025-12-25
```

---

### （補足）仮想環境を終了するには

すべての作業が終わった後、ターミナルの行頭にある `(.venv)` の表示を消して元の状態に戻したい場合は、以下のコマンドを実行します。

```bash
deactivate
```
