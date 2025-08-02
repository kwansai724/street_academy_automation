# ストアカ日程追加・削除 自動化ツール

面倒なストアカの講座日程の「一括追加」と「指定講座の一括削除」を、クリック操作で簡単に行うためのツールです。

## 機能
*   **日程の追加**: 指定した期間、毎日決まった時間帯（例: 9時〜22時）の日程をまとめて作成します。
*   **日程の削除**: 指定した期間と講座名に一致する日程だけを、まとめて削除します。

## 導入手順

### 1. 【事前準備】 必要なツールのインストール

お使いのPCにPythonと関連ツールをインストールします。お使いのOS（MacまたはWindows）に合わせて手順を実行してください。

---
#### <img src="https://www.apple.com/favicon.ico" width="16"> Macユーザー向け手順

##### 1-1. Homebrewのインストール確認と実行
Mac用のパッケージ管理ツール「Homebrew」を準備します。

まず、**ターミナル**を開き、以下のコマンドでHomebrewがインストール済みか確認します。
```sh
command -v brew
```
*   `/opt/homebrew/bin/brew` のようなパスが表示されれば、**インストール済み**です。次の手順に進んでください。
*   何も表示されなければ、**未インストール**です。以下のコマンドを貼り付けて実行し、Homebrewをインストールしてください。
    ```sh
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```

##### 1-2. Pythonのインストール確認と実行
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

##### 1-3. プロジェクトフォルダの準備と移動
作業用のフォルダを作成し、そこに移動します。
```sh
# 例: デスクトップにフォルダを作成
mkdir street_academy_automation
cd street_academy_automation
```
---
#### <img src="https://www.microsoft.com/favicon.ico" width="16"> Windowsユーザー向け手順

##### 1-1. Pythonのインストール確認と実行
まず、コマンドプロンプトまたはPowerShellでPythonがインストール済みか確認します。
```powershell
python --version
```
*   `Python 3.x.x` のようにバージョンが表示されれば、**インストール済み**です。次の「1-2. プロジェクトフォルダの準備」に進んでください。
*   `python は、内部コマンドまたは外部コマンド...` などのエラーが出れば、**未インストール**です。以下の手順でPythonをインストールしてください。

1.  [Python公式サイトのダウンロードページ](https://www.python.org/downloads/)にアクセスします。
2.  「Download Python 3.x.x」ボタンをクリックしてインストーラーをダウンロードします。
3.  インストーラーを起動し、**必ず「Add Python 3.x to PATH」のチェックボックスにチェックを入れてから**、「Install Now」をクリックします。

    ![Python for Windows Installer](https://docs.python.org/3/_images/win_installer.png)

##### 1-2. プロジェクトフォルダの準備と移動
作業用のフォルダを作成し、そこに移動します。**コマンドプロンプト**または**PowerShell**を開いて実行してください。
```powershell
# 例: デスクトップにフォルダを作成
cd ~/Desktop
mkdir street_academy_automation
cd street_academy_automation
```
---
#### 1-4. 仮想環境の作成と有効化 (Mac / Windows共通)

プロジェクト専用のクリーンな環境を作ります。これ以降のコマンドは、Macは**ターミナル**、Windowsは**コマンドプロンプト**で実行します。

① **仮想環境の作成** (フォルダ内で初回のみ)
```sh
# Mac / Windows 共通
python -m venv .venv
```

② **仮想環境の有効化** (このフォルダで作業する際は毎回実行)
*   **Mac の場合:**
    ```sh
    source .venv/bin/activate
    ```
*   **Windows の場合:**
    ```powershell
    .\.venv\Scripts\activate
    ```
実行後、コマンドプロンプトの行頭に `(.venv)` と表示されればOKです。

#### 1-5. 必要なライブラリのインストール (Mac / Windows共通)
仮想環境が有効な状態で、自動化に必要なライブラリとブラウザをインストールします。
```sh
# Mac / Windows 共通
pip install flet playwright
playwright install
```

### 2. 【ファイル作成】 `app.py` ファイルを用意する

先ほど作成した`street_academy_automation`フォルダ内に、`app.py` という名前でファイルを作成し、以下の内容を**すべて**コピー＆ペーストして保存してください。

```python
import flet as ft
import time
from datetime import date, timedelta
from playwright.sync_api import sync_playwright, expect
import threading
import os

# 認証情報ファイルのパス (このままでOK)
AUTH_FILE_PATH = 'playwright_auth.json'

# ①：あなたの日程追加ページのURLに書き換えてください
# 例: 'https://www.street-academy.com/session_details/new_multi_session?classdetailid=123456'
TARGET_URL = 'https://www.street-academy.com/session_details/new_multi_session?classdetailid=123456'

# ②：あなたの緊急連絡先(電話番号)に書き換えてください
EMERGENCY_CONTACT = '090-1234-5678' 

# ③：追加したい時間帯 (8時〜22時でよければ変更不要)
HOURS_TO_ADD = list(range(8, 23)) 


def do_login(page_instance: ft.Page, status_text: ft.Text):
    """ 認証情報ファイルを作成する処理 """
    def update_status(value, color):
        status_text.value = value
        status_text.color = color
        page_instance.update()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            page.goto("https://www.street-academy.com/d/users/sign_in")
            update_status("ブラウザでログインしてください...", "black")
            
            page.wait_for_url("https://www.street-academy.com/dashboard/steachers", timeout=300000)
            
            context.storage_state(path=AUTH_FILE_PATH)
            browser.close()
        
        update_status("認証成功！ 'playwright_auth.json' を保存しました。", "green")
    except Exception as e:
        update_status(f"ログインに失敗またはタイムアウトしました: {e}", "red")

def run_playwright_task(page_instance: ft.Page, log_text: ft.Text, task_func, *args):
    """Playwrightタスクを別スレッドで実行するための共通ラッパー"""
    def log(message):
        log_text.value += message + "\n"
        page_instance.update()

    log_text.value = ""
    page_instance.update()

    try:
        task_func(log, *args)
    except Exception as e:
        log(f"予期せぬエラーが発生しました: {e}")
        print(f"エラー詳細: {e}")

def add_schedules_logic(log, url, contact, schedules_text):
    """個別日程で日程を追加するロジック"""
    log("個別日程による日程追加を開始します...")
    schedules = parse_custom_schedules(schedules_text)
    if not schedules:
        log("有効な日程が入力されていません。\n例: 2025-08-27\t14:00~15:30")
        return
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        if not os.path.exists(AUTH_FILE_PATH):
            log("エラー: 認証ファイル 'playwright_auth.json' が見つかりません。")
            return
        context = browser.new_context(storage_state=AUTH_FILE_PATH)
        page = context.new_page()
        for date_str, start_str, end_str in schedules:
            log(f"\n--- {date_str} {start_str}~{end_str} の日程を追加します ---")
            page.goto(url)
            expect(page.get_by_role("button", name="日程を複製する")).to_be_visible(timeout=30000)

            # オンライン選択肢があれば選択（既存ロジック流用）
            online_radio_button = page.locator("#is_online_check")
            if online_radio_button.is_visible():
                log("開催形式の選択肢を検出。「オンライン」を選択します。")
                online_radio_button.check()
                expect(online_radio_button).to_be_checked()
                log("「オンライン」を選択しました。")

            first_block = page.locator('div[data-repeater-item]').first
            y, m, d = map(int, date_str.split('-'))
            first_block.locator('select[name*="[session_startdate_year]"]').select_option(str(y))
            first_block.locator('select[name*="[session_startdate_month]"]').select_option(str(m))
            first_block.locator('select[name*="[session_startdate_day]"]').select_option(str(d))
            start_hour, start_min = map(int, start_str.split(':'))
            end_hour, end_min = map(int, end_str.split(':'))
            first_block.locator('select.js_start_time_hour').select_option(str(start_hour))
            first_block.locator('select.js_start_time_minute').select_option(str(start_min))
            first_block.locator('select.js_end_time_hour').select_option(str(end_hour))
            first_block.locator('select.js_end_time_minute').select_option(str(end_min))
            log(f"{start_hour:02d}:{start_min:02d} - {end_hour:02d}:{end_min:02d} の日程を設定しました。")

            page.locator("#session_detail_multi_form_emergency_contact").fill(contact)
            time.sleep(1)
            page.get_by_role("button", name="プレビュー画面で確認").click()
            confirm_button = page.get_by_role("button", name="確定")
            expect(confirm_button).to_be_visible(timeout=15000)
            time.sleep(1)
            confirm_button.click()
            log("完了ページへの遷移を待っています...")
            button1 = page.get_by_role("link", name="集客する")
            button2 = page.get_by_role("link", name="日程追加")
            expect(button1.or_(button2).first).to_be_visible(timeout=20000)
            log(f"--- {date_str} {start_str}~{end_str} の日程追加が完了しました！ ---")
            time.sleep(3)
        browser.close()
        log("\nすべての処理が完了しました。")


def parse_custom_schedules(text):
    """個別日程リストのテキストをパースして [(date, start, end)] のリストにする"""
    result = []
    for line in text.strip().splitlines():
        if not line.strip():
            continue
        try:
            date_part, time_part = line.strip().split('\t')
            start_time, end_time = time_part.split('~')
            result.append((date_part.strip(), start_time.strip(), end_time.strip()))
        except Exception:
            continue
    return result

def add_continuous_schedules_logic(log, url, contact, start_str, end_str):
    """ 連続日程追加のロジック """
    log("連続日程追加処理を開始します...")
    start_date = date.fromisoformat(start_str)
    end_date = date.fromisoformat(end_str)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        if not os.path.exists(AUTH_FILE_PATH):
            log("エラー: 認証ファイル 'playwright_auth.json' が見つかりません。")
            return
        context = browser.new_context(storage_state=AUTH_FILE_PATH)
        page = context.new_page()

        for single_date in daterange(start_date, end_date):
            log(f"\n--- {single_date.strftime('%Y-%m-%d')} の日程を追加します ---")
            page.goto(url)
            expect(page.get_by_role("button", name="日程を複製する")).to_be_visible(timeout=30000)

            # 「オンライン」のラジオボタンをIDで特定
            online_radio_button = page.locator("#is_online_check")
            
            # ラジオボタンが表示されているか（=対面/オンラインの選択肢があるか）を確認
            if online_radio_button.is_visible():
                log("開催形式の選択肢を検出。「オンライン」を選択します。")
                online_radio_button.check()
                expect(online_radio_button).to_be_checked()
                log("「オンライン」を選択しました。")
            
            first_block = page.locator('div[data-repeater-item]').first
            first_block.locator('select[name*="[session_startdate_year]"]').select_option(str(single_date.year))
            first_block.locator('select[name*="[session_startdate_month]"]').select_option(str(single_date.month))
            first_block.locator('select[name*="[session_startdate_day]"]').select_option(str(single_date.day))
            first_block.locator('select.js_start_time_hour').select_option(str(HOURS_TO_ADD[0]))
            first_block.locator('select.js_end_time_hour').select_option(str(HOURS_TO_ADD[0] + 1))
            log(f"{HOURS_TO_ADD[0]}:00 - {HOURS_TO_ADD[0]+1}:00 の日程を設定しました。")

            for hour in HOURS_TO_ADD[1:]:
                page.get_by_role("button", name="日程を複製する").click()
                last_block = page.locator('div[data-repeater-item]').last
                expect(last_block).to_be_visible()
                end_hour = hour + 1 if hour < 23 else 23
                last_block.locator('select.js_start_time_hour').select_option(str(hour))
                last_block.locator('select.js_end_time_hour').select_option(str(end_hour))
                log(f"{hour}:00 - {end_hour}:00 の日程を設定しました。")

            page.locator("#session_detail_multi_form_emergency_contact").fill(contact)
            page.get_by_role("button", name="プレビュー画面で確認").click()
            confirm_button = page.get_by_role("button", name="確定")
            expect(confirm_button).to_be_visible(timeout=15000)
            confirm_button.click()
            
            log("完了ページへの遷移を待っています...")
            button1 = page.get_by_role("link", name="集客する")
            button2 = page.get_by_role("link", name="日程追加")
            expect(button1.or_(button2).first).to_be_visible(timeout=20000)
            
            log(f"--- {single_date.strftime('%Y-%m-%d')} の日程追加が完了しました！ ---")
            time.sleep(3)
        
        browser.close()
        log("\nすべての処理が完了しました。")

def delete_schedules_logic(log, start_str, end_str, class_names_str):
    """ 講座名でフィルタリングして日程を削除する """
    log("日程削除処理を開始します...")
    target_class_names = [name.strip() for name in class_names_str.strip().split('\n') if name.strip()]
    if not target_class_names:
        log("エラー: 削除対象の講座名が入力されていません。")
        return

    log(f"削除対象の講座名: {', '.join(target_class_names)}")
    start_date = date.fromisoformat(start_str)
    end_date = date.fromisoformat(end_str)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        if not os.path.exists(AUTH_FILE_PATH):
            log("エラー: 認証ファイル 'playwright_auth.json' が見つかりません。")
            return
        context = browser.new_context(storage_state=AUTH_FILE_PATH)
        page = context.new_page()

        for single_date in daterange(start_date, end_date):
            date_param = single_date.strftime('%Y-%-m-%-d')
            ### 主催団体用
            base_url = f"https://www.street-academy.com/dashboard/organizers/schedule_list?date={date_param}"
            ### 個人用
            # base_url = f"https://www.street-academy.com/dashboard/steachers/manage_class_dates?date={date_param}"
            log(f"\n--- {single_date.strftime('%Y-%m-%d')} の日程削除を開始します ---")

            next_url = base_url
            found_any = False
            while True:
                url = next_url
                log(f"アクセス中: {url}")

                # 403 Forbidden検知＆リトライ
                for retry in range(3):  # 最大3回リトライ
                    page.goto(url, timeout=60000)
                    body_html = page.content()
                    if "403 Forbidden" in body_html:
                        log("403 Forbidden画面を検知。2分間待機してリトライします。")
                        time.sleep(120)
                    else:
                        break
                else:
                    log("403 Forbiddenが解消しませんでした。次の日付へ進みます。")
                    break

                log("ページの読み込みを待っています...")
                schedule_links_locator = page.locator('a.dashboard-session_container[href*="/show_attendance?sessiondetailid="]')
                no_schedule_text_locator = page.locator("text=講座がありません")

                # どちらかが見つかるまで最大2秒待つ
                found = False
                for _ in range(2):
                    if schedule_links_locator.count() > 0 or no_schedule_text_locator.count() > 0:
                        found = True
                        break
                    time.sleep(2)
                if not found:
                    log("日程リンクも「講座がありません」も見つかりませんでした。次の日付へ進みます。")
                    break

                log("ページの読み込み完了。")
                all_schedule_links = schedule_links_locator

                if all_schedule_links.count() == 0:
                    # ページ内に日程がなければ、次ページがあるか確認して終了判定
                    next_button = page.locator('a[rel="next"]')
                    if next_button.count() > 0:
                        href = next_button.first.get_attribute('href')
                        if href:
                            next_url = "https://www.street-academy.com" + href
                            continue
                    if not found_any:
                        log("この日付に削除可能な日程はありません。")
                    break

                target_link = None
                for i in range(all_schedule_links.count()):
                    link = all_schedule_links.nth(i)
                    link_text = link.inner_text()
                    if any(class_name in link_text for class_name in target_class_names):
                        target_link = link
                        break

                if target_link is None:
                    # 次ページがあれば巡回、なければ終了
                    next_button = page.locator('a[rel="next"]')
                    if next_button.count() > 0:
                        href = next_button.first.get_attribute('href')
                        if href:
                            next_url = "https://www.street-academy.com" + href
                            continue
                    if not found_any:
                        log("この日付に削除対象の講座はありませんでした。")
                    break

                found_any = True
                target_text = target_link.inner_text()
                target_text_clean = target_text.strip().replace('\n', ' ')
                log(f"  - 削除対象: {target_text_clean}")
                target_link.click()
                time.sleep(5)

                cancel_button_1 = page.get_by_role("link", name="開催をキャンセルする")
                expect(cancel_button_1).to_be_visible()
                cancel_button_1.click()
                time.sleep(5)

                modal_cancel_button = page.locator("#sa-modal-cancel").get_by_role("button", name="開催キャンセル")
                expect(modal_cancel_button).to_be_visible()

                page.once("dialog", lambda dialog: (time.sleep(5), dialog.accept()))
                modal_cancel_button.click()

                log("  - キャンセル処理を実行しました。")
                time.sleep(3)
                # 削除後は同じページを再読込して再度巡回
                # ページングのためnext_urlをリセット（同じページを再読込）
                next_url = url

            # 次の日付へ
        browser.close()
        log("\nすべての処理が完了しました。")

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

def main(page: ft.Page):
    page.title = "ストアカ日程自動化ツール"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_width = 700
    page.window_height = 800

    def check_auth_status():
        if os.path.exists(AUTH_FILE_PATH):
            return "認証済み", "green"
        else:
            return "未認証 (最初にログインを実行してください)", "red"

    def run_in_thread(target_func, *args):
        thread = threading.Thread(target=target_func, args=args, daemon=True)
        thread.start()

    initial_text, initial_color = check_auth_status()
    auth_status_text = ft.Text(value=initial_text, color=initial_color)
    
    def handle_login(e):
        thread = threading.Thread(target=do_login, args=(page, auth_status_text), daemon=True)
        thread.start()
    
    login_button = ft.ElevatedButton("ログイン / 認証情報を作成 (初回のみ)", on_click=handle_login)


    # --- 日程追加方式の選択ラジオボタン ---
    add_mode = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="custom", label="個別日程追加"),
            ft.Radio(value="normal", label="連続日程追加")
        ]),
        value="custom"
    )

    # --- 連続日程追加用UI ---
    url_input = ft.TextField(label="日程追加ページのURL", value=TARGET_URL, width=600)
    contact_input = ft.TextField(label="緊急連絡先", value=EMERGENCY_CONTACT, width=300)
    add_start_date = ft.TextField(label="開始日 (YYYY-MM-DD)", width=200)
    add_end_date = ft.TextField(label="終了日 (YYYY-MM-DD)", width=200)
    add_button = ft.ElevatedButton("連続日程追加", bgcolor="blue", color="white")

    # --- 個別日程追加用UI ---
    custom_schedules_input = ft.TextField(
        label="個別日程リスト (例: 2025-08-27\t14:00~15:30)",
        multiline=True,
        min_lines=3,
        width=600,
        hint_text="例:\n2025-08-27\t14:00~15:30\n2025-08-28\t12:00~14:00",
        hint_style=ft.TextStyle(color="#bbbbbb")
    )
    add_custom_button = ft.ElevatedButton("個別日程追加", bgcolor="green", color="white")

    # 排他制御用フラグ
    add_running = {'value': False}

    def set_add_running(state: bool):
        add_running['value'] = state
        add_button.disabled = state
        add_custom_button.disabled = state
        page.update()

    def handle_add_schedules(e):
        if add_running['value']:
            return
        set_add_running(True)
        def wrapped():
            try:
                run_playwright_task(page, log_view, add_continuous_schedules_logic, url_input.value, contact_input.value, add_start_date.value, add_end_date.value)
            finally:
                set_add_running(False)
        run_in_thread(wrapped)
    add_button.on_click = handle_add_schedules

    def handle_add_custom_schedules(e):
        if add_running['value']:
            return
        set_add_running(True)
        def wrapped():
            try:
                run_playwright_task(page, log_view, add_schedules_logic, url_input.value, contact_input.value, custom_schedules_input.value)
            finally:
                set_add_running(False)
        run_in_thread(wrapped)
    add_custom_button.on_click = handle_add_custom_schedules

    # --- 日程追加フォームの切り替え ---
    normal_add_form = ft.Column([
        url_input,
        contact_input,
        ft.Row([add_start_date, add_end_date]),
        add_button
    ])
    custom_add_form = ft.Column([
        url_input,
        contact_input,
        custom_schedules_input,
        add_custom_button
    ])

    add_form_container = ft.Container()

    def update_add_form(_=None):
        if add_mode.value == "normal":
            add_form_container.content = normal_add_form
        else:
            add_form_container.content = custom_add_form
        page.update()

    add_mode.on_change = update_add_form
    update_add_form()

    # 日程削除用UI
    delete_start_date = ft.TextField(label="開始日 (YYYY-MM-DD)", width=200)
    delete_end_date = ft.TextField(label="終了日 (YYYY-MM-DD)", width=200)
    class_names_input = ft.TextField(
        label="削除対象の講座名 (複数ある場合は改行して入力)",
        multiline=True,
        min_lines=3,
        hint_text="例:\nNotebookLMに資料投入！\nAIとGASで夢の時短術！",
        hint_style=ft.TextStyle(color="#bbbbbb")
    )
    
    def handle_delete_schedules(e):
        run_in_thread(run_playwright_task, page, log_view, delete_schedules_logic, delete_start_date.value, delete_end_date.value, class_names_input.value)
    
    delete_button = ft.ElevatedButton("指定した講座の日程を削除", on_click=handle_delete_schedules, bgcolor="red", color="white")

    # ログ表示用UI
    log_view = ft.Text("", selectable=True, font_family="monospace", size=12)
    log_container = ft.Container(
        content=ft.Column([log_view], scroll=ft.ScrollMode.ADAPTIVE, expand=True),
        border=ft.border.all(1, "grey"),
        padding=10,
        expand=True,
    )
    
    page.add(
        ft.Column([
            ft.Row([login_button, auth_status_text], alignment=ft.MainAxisAlignment.START),
            ft.Divider(),
            ft.Text("日程の追加", size=20, weight=ft.FontWeight.BOLD),
            add_mode,
            add_form_container,
            ft.Divider(),
            ft.Text("日程の削除", size=20, weight=ft.FontWeight.BOLD),
            class_names_input,
            ft.Row([delete_start_date, delete_end_date]),
            delete_button,
            ft.Divider(),
            ft.Text("実行ログ", size=16),
            log_container
        ], expand=True, scroll=ft.ScrollMode.ADAPTIVE)
    )

if __name__ == "__main__":
    ft.app(target=main)
```

【重要】 作成した`app.py`を開き、先頭部分の**設定項目（`TARGET_URL`と`EMERGENCY_CONTACT`）**を自分の情報に必ず書き換えてください。

---

### ステップ3：【初回のみ】認証情報ファイルを作成する

1.  **仮想環境を有効化**します。（「1-4. 仮想環境の作成と有効化 (Mac / Windows共通)」の②）
2.  `python app.py` を実行してツールを起動します。
3.  ウィンドウが表示されたら、一番上にある【ログイン / 認証情報を作成 (初回のみ)】ボタンをクリックします。
4.  ブラウザが起動するので、**手動でストアカにログイン**してください。
5.  ログインが完了すると、ブラウザは自動で閉じ、ツール画面の「未認証」という表示が【認証済み】に変わります。これで認証は完了です。

---

### ステップ4：【実行】自動化ツールを動かす

1.  `python app.py` でツールを起動します（仮想環境の有効化を忘れずに）。
2.  **日程を追加する場合**:
    *   【日程追加ページのURL】と【緊急連絡先】が正しいか確認・修正します。
    *   追加したい【開始日】と【終了日】を`YYYY-MM-DD`形式で入力します。
    *   【日程を追加】ボタンをクリックします。
3.  **日程を削除する場合**:
    *   削除したい【講座名】をテキストエリアに1行ずつ入力します。
    *   削除したい【開始日】と【終了日】を入力します。
    *   【指定した講座の日程を削除】ボタンをクリックします。

実行すると、ブラウザが自動で立ち上がり、処理が開始されます。下部の「実行ログ」に進捗が表示されます。

---

### （補足）仮想環境を終了するには

すべての作業が終わった後、ターミナルの行頭にある `(.venv)` の表示を消して元の状態に戻したい場合は、以下のコマンドを実行します。

```sh
deactivate
```

---

## 日常的な使い方（2回目以降の作業）

初回セットアップが完了していれば、次回からはこの手順だけでツールを使えます。

### ステップ1：ツールの起動

1.  **ターミナル**（Windowsの場合は**コマンドプロンプト**）を開きます。
2.  `cd` コマンドで、前回作成した `stoc-aca-automation` フォルダに移動します。
    ```sh
    # 例
    cd ~/Desktop/stoc-aca-automation
    ```
3.  **仮想環境を有効化**します。
    *   **Mac の場合:**
        ```sh
        source .venv/bin/activate
        ```
    *   **Windows の場合:**
        ```powershell
        .\.venv\Scripts\activate
        ```
4.  ツールを起動します。
    *   **Mac の場合:** `python app.py`
    *   **Windows の場合:** `python app.py`

### ステップ2：日程の追加または削除

ツールが起動したら、あとは画面の指示に従って操作します。

*   **日程を追加する場合**:
    1.  必要であれば【日程追加ページのURL】などを修正します。
    2.  追加したい【開始日】と【終了日】を`YYYY-MM-DD`形式で入力します。
    3.  【日程を追加】ボタンをクリックします。
*   **日程を削除する場合**:
    1.  削除したい【講座名】をテキストエリアに1行ずつ入力します。
    2.  削除したい【開始日】と【終了日】を入力します。
    3.  【指定した講座の日程を削除】ボタンをクリックします。

実行するとブラウザが自動で動き出し、処理が終わると自動で閉じます。

### ステップ3：ツールの終了

1.  ツールウィンドウを閉じます。
2.  ターミナルで `deactivate` コマンドを実行して、仮想環境を終了します。
    ```sh
    deactivate
    ```
