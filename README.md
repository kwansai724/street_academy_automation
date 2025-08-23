# ストアカ日程追加・削除 自動化ツール

面倒なストアカの講座日程の「追加」と「削除」を、クリック操作で簡単に行うためのツールです。

## 機能

### 📅 日程の追加
2つの方式で日程を追加できます：

#### 1. 個別日程追加
- **機能**: 日時を個別に指定して日程を追加
- **入力形式**: `日付 タブ文字 開始時間~終了時間`
- **例**: 
  ```
  2025-08-27	14:00~15:30
  2025-08-28	12:00~14:00
  2025-08-29	19:00~21:00
  ```
- **特徴**: 自由な日時で日程を設定可能

#### 2. 連続日程追加
- **機能**: 指定した期間に対して、8:00〜22:00までの講座を自動で追加
- **入力**: 開始日と終了日（YYYY-MM-DD形式）
- **自動生成される時間帯**: 
  - 8:00-9:00, 9:00-10:00, 10:00-11:00, ..., 22:00-23:00
- **特徴**: 期間内の毎日に同じ時間帯の講座を一括作成

#### 共通機能
- **複数URL対応**: 日程追加ページのURLを改行区切りで複数指定可能
- **オンライン開催**: 自動で「オンライン」形式を選択
- **緊急連絡先**: 設定した電話番号を自動入力

### 🗑️ 日程の削除
2つの方式で日程を削除できます：

#### 1. 個別日程削除
- **機能**: 日時を個別に指定して日程を削除
- **入力**: 講座名（複数の場合は改行区切り）、日程リスト
- **入力形式**: `日付 タブ文字 開始時間~終了時間`
- **例**: 
  ```
  2025-08-27	14:00~15:30
  2025-08-28	12:00~14:00
  ```
- **特徴**: 自由な日時で日程を削除可能

#### 2. 連続日程削除
- **機能**: 指定した期間の対象講座日程を一括削除
- **入力**: 講座名（複数の場合は改行区切り）、開始日、終了日
- **特徴**: 期間内の指定講座の全日程を一括削除

#### 共通機能
- **講座名フィルタリング**: 指定した講座名のみを削除対象とする
- **複数講座対応**: 複数の講座名を改行区切りで指定可能

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
import re

# 認証情報ファイルのパス (このままでOK)
AUTH_FILE_PATH = 'playwright_auth.json'

# ①：あなたの緊急連絡先(電話番号)に書き換えてください
EMERGENCY_CONTACT = '090-1234-5678' 

# ②：追加したい時間帯 (8時〜22時でよければ変更不要)
HOURS_TO_ADD = list(range(8, 23)) 

# 共通設定
BASE_URL = "https://www.street-academy.com"
ORGANIZER_SCHEDULE_URL = f"{BASE_URL}/dashboard/organizers/schedule_list"
TEACHER_SCHEDULE_URL = f"{BASE_URL}/dashboard/steachers/manage_class_dates"

class PlaywrightHelper:
    """Playwrightの共通処理を提供するヘルパークラス"""
    
    @staticmethod
    def create_browser_context():
        """ブラウザとコンテキストを作成"""
        if not os.path.exists(AUTH_FILE_PATH):
            raise Exception("認証ファイル 'playwright_auth.json' が見つかりません。")
        
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(storage_state=AUTH_FILE_PATH)
        return playwright, browser, context
    
    @staticmethod
    def handle_403_forbidden(page, log_func, max_retries=3):
        """403 Forbiddenエラーの処理"""
        for retry in range(max_retries):
            body_html = page.content()
            if "403 Forbidden" in body_html:
                log_func("403 Forbidden画面を検知。2分間待機してリトライします。")
                time.sleep(120)
            else:
                return True
        log_func("403 Forbiddenが解消しませんでした。")
        return False
    
    @staticmethod
    def wait_for_page_load(page, log_func, timeout=2):
        """ページの読み込み完了を待機"""
        schedule_links_locator = page.locator('a.dashboard-session_container[href*="/show_attendance?sessiondetailid="]')
        no_schedule_text_locator = page.locator("text=講座がありません")
        
        for _ in range(timeout):
            if schedule_links_locator.count() > 0 or no_schedule_text_locator.count() > 0:
                return True
            time.sleep(2)
        return False

class ScheduleHelper:
    """日程関連の共通処理を提供するヘルパークラス"""
    
    @staticmethod
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
    
    @staticmethod
    def extract_time_from_text(text):
        """テキストから開始時刻を抽出"""
        time_match = re.search(r'(\d{1,2}):(\d{2})', text)
        if time_match:
            start_hour, start_min = map(int, time_match.groups())
            return f"{start_hour:02d}:{start_min:02d}"
        return None
    
    @staticmethod
    def find_matching_schedule(links, class_names, start_time):
        """指定された条件に一致する日程を探す"""
        for i in range(links.count()):
            try:
                link = links.nth(i)
                link_text = link.inner_text()
                
                # 講座名の一致を確認
                if not any(class_name in link_text for class_name in class_names):
                    continue
                
                # 開始時刻の一致を確認（start_timeがNoneの場合は講座名のみでマッチング）
                if start_time is not None:
                    link_start_time = ScheduleHelper.extract_time_from_text(link_text)
                    if link_start_time != start_time:
                        continue
                
                return link
            except Exception:
                continue
        return None
    
    @staticmethod
    def delete_schedule(page, link, log_func):
        """日程の削除処理を実行"""
        try:
            target_text = link.inner_text()
            target_text_clean = target_text.strip().replace('\n', ' ')
            log_func(f"  - 削除対象: {target_text_clean}")
            
            # 削除前の講座一覧URLを保存
            original_url = page.url
            
            link.click()
            time.sleep(5)

            cancel_button_1 = page.get_by_role("link", name="開催をキャンセルする")
            expect(cancel_button_1).to_be_visible()
            cancel_button_1.click()
            time.sleep(5)

            modal_cancel_button = page.locator("#sa-modal-cancel").get_by_role("button", name="開催キャンセル")
            expect(modal_cancel_button).to_be_visible()

            page.once("dialog", lambda dialog: (time.sleep(5), dialog.accept()))
            modal_cancel_button.click()

            log_func(f"  - 日程削除が完了しました！")
            time.sleep(3)
            
            # 削除後に講座一覧に戻る
            page.goto(original_url, timeout=60000)
            time.sleep(3)
            
            return True
        except Exception as e:
            log_func(f"  - 削除処理中にエラーが発生しました: {e}")
            # エラーが発生した場合も講座一覧に戻る
            try:
                if 'original_url' in locals():
                    page.goto(original_url, timeout=60000)
                    time.sleep(3)
            except:
                pass
            return False
    
    @staticmethod
    def find_and_delete_schedules(page, log_func, class_names, start_time=None, max_pages=10):
        """指定された条件に一致する日程を探して削除する（ページング対応）"""
        found_any = False
        page_count = 0
        
        while page_count < max_pages:
            page_count += 1
            log_func(f"ページ {page_count} を確認中...")
            
            # ページの読み込みを待機
            if not PlaywrightHelper.wait_for_page_load(page, log_func):
                # 日程がないページの場合は正常終了として扱う
                no_schedule_text = page.locator("text=講座がありません")
                if no_schedule_text.count() > 0:
                    log_func("このページに日程はありません。")
                    break
                else:
                    log_func("ページの読み込みに失敗しました。")
                    break
            
            # このページで削除対象がなくなるまで繰り返し削除
            while True:
                # 日程リンクを取得
                all_schedule_links = page.locator('a.dashboard-session_container[href*="/show_attendance?sessiondetailid="]')
                
                if all_schedule_links.count() == 0:
                    log_func("このページに日程はありません。")
                    break
                
                # 削除対象の日程を探す
                target_link = ScheduleHelper.find_matching_schedule(all_schedule_links, class_names, start_time)
                
                if target_link is not None:
                    # 削除処理を実行
                    if ScheduleHelper.delete_schedule(page, target_link, log_func):
                        found_any = True
                        continue
                    else:
                        break
                else:
                    # 削除対象が見つからない場合はこのページの処理を終了
                    break
            
            # 次ページがあるか確認
            next_button = page.locator('a[rel="next"]')
            if next_button.count() > 0:
                href = next_button.first.get_attribute('href')
                if href:
                    next_url = BASE_URL + href
                    page.goto(next_url, timeout=60000)
                    if not PlaywrightHelper.handle_403_forbidden(page, log_func):
                        break
                    continue
            
            # 次ページがない場合は終了
            break
        
        return found_any

class URLHelper:
    """URL関連の共通処理を提供するヘルパークラス"""
    
    @staticmethod
    def build_schedule_url(date_param, is_organizer=True):
        """日程一覧のURLを構築"""
        base_url = ORGANIZER_SCHEDULE_URL if is_organizer else TEACHER_SCHEDULE_URL
        return f"{base_url}?date={date_param}"
    
    @staticmethod
    def format_date_param(target_date):
        """日付パラメータをフォーマット"""
        return target_date.strftime('%Y-%-m-%-d')

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
            
            # ログイン後の画面を待機（個人用と主催団体用の両方に対応）
            try:
                # 個人用と主催団体用のダッシュボードのどちらかを待機
                page.wait_for_url(
                    lambda url: url.startswith("https://www.street-academy.com/dashboard/steachers") or 
                               url.startswith("https://www.street-academy.com/dashboard/organizers"),
                    timeout=300000
                )
                
                # 実際に遷移したURLを確認してメッセージを表示
                current_url = page.url
                if current_url.startswith("https://www.street-academy.com/dashboard/steachers"):
                    update_status("個人用ダッシュボードにログインしました", "blue")
                elif current_url.startswith("https://www.street-academy.com/dashboard/organizers"):
                    update_status("主催団体用ダッシュボードにログインしました", "blue")
                else:
                    update_status(f"ダッシュボードにログインしました: {current_url}", "blue")
                    
            except Exception as e:
                # その他のダッシュボードページも確認
                current_url = page.url
                if current_url.startswith("https://www.street-academy.com/dashboard/"):
                    update_status(f"ダッシュボードにログインしました: {current_url}", "blue")
                else:
                    raise Exception(f"ログイン後のダッシュボードページに遷移しませんでした: {e}")
            
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

def add_schedules_logic(log, urls, contact, schedules_text):
    """個別日程で日程を追加するロジック"""
    log("個別日程による日程追加を開始します...")
    schedules = ScheduleHelper.parse_custom_schedules(schedules_text)
    if not schedules:
        log("有効な日程が入力されていません。\n例: 2025-08-27\t14:00~15:30")
        return
    
    # URLを改行区切りで分割
    url_list = [url.strip() for url in urls.strip().split('\n') if url.strip()]
    if not url_list:
        log("エラー: 有効なURLが入力されていません。")
        return
    
    log(f"処理対象のURL数: {len(url_list)}")
    
    try:
        playwright, browser, context = PlaywrightHelper.create_browser_context()
        page = context.new_page()
        
        for url_index, url in enumerate(url_list, 1):
            log(f"\n=== URL {url_index}/{len(url_list)}: {url} ===")
            for schedule_index, (date_str, start_str, end_str) in enumerate(schedules, 1):
                log(f"\n--- 日程 {schedule_index}/{len(schedules)}: {date_str} {start_str}~{end_str} を追加します ---")
                page.goto(url)
                expect(page.get_by_role("button", name="日程を複製する")).to_be_visible(timeout=30000)

                # オンライン選択肢があれば選択
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
                log(f"--- 日程 {schedule_index}/{len(schedules)}: {date_str} {start_str}~{end_str} の日程追加が完了しました！ ---")
                time.sleep(3)
    except Exception as e:
        log(f"エラーが発生しました: {e}")
    finally:
        if 'browser' in locals():
            browser.close()
        log("\nすべての処理が完了しました。")

def add_continuous_schedules_logic(log, urls, contact, start_str, end_str):
    """ 連続日程追加のロジック """
    log("連続日程追加処理を開始します...")
    start_date = date.fromisoformat(start_str)
    end_date = date.fromisoformat(end_str)
    
    # URLを改行区切りで分割
    url_list = [url.strip() for url in urls.strip().split('\n') if url.strip()]
    if not url_list:
        log("エラー: 有効なURLが入力されていません。")
        return
    
    log(f"処理対象のURL数: {len(url_list)}")
    
    try:
        playwright, browser, context = PlaywrightHelper.create_browser_context()
        page = context.new_page()

        for url_index, url in enumerate(url_list, 1):
            log(f"\n=== URL {url_index}/{len(url_list)}: {url} ===")
            for single_date in daterange(start_date, end_date):
                log(f"\n--- {single_date.strftime('%Y-%m-%d')} の日程を追加します ---")
                page.goto(url)
                expect(page.get_by_role("button", name="日程を複製する")).to_be_visible(timeout=30000)

                # 「オンライン」のラジオボタンを選択
                online_radio_button = page.locator("#is_online_check")
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
    except Exception as e:
        log(f"エラーが発生しました: {e}")
    finally:
        if 'browser' in locals():
            browser.close()
        log("\nすべての処理が完了しました。")

def delete_schedules_logic(log, start_str, end_str, class_names_str):
    """ 連続日程削除のロジック """
    log("連続日程削除処理を開始します...")
    target_class_names = [name.strip() for name in class_names_str.strip().split('\n') if name.strip()]
    if not target_class_names:
        log("エラー: 削除対象の講座名が入力されていません。")
        return

    log(f"削除対象の講座名: {', '.join(target_class_names)}")
    start_date = date.fromisoformat(start_str)
    end_date = date.fromisoformat(end_str)

    try:
        playwright, browser, context = PlaywrightHelper.create_browser_context()
        page = context.new_page()

        for single_date in daterange(start_date, end_date):
            log(f"\n--- {single_date.strftime('%Y-%m-%d')} の日程削除を開始します ---")
            date_param = URLHelper.format_date_param(single_date)
            base_url = URLHelper.build_schedule_url(date_param)

            # 共通化されたページング処理を使用
            log(f"アクセス中: {base_url}")
            page.goto(base_url, timeout=60000)
            if not PlaywrightHelper.handle_403_forbidden(page, log):
                continue

            found_any = ScheduleHelper.find_and_delete_schedules(page, log, target_class_names, None)
            
            if not found_any:
                log("この日付に削除対象の講座はありませんでした。")
    except Exception as e:
        log(f"エラーが発生しました: {e}")
    finally:
        if 'browser' in locals():
            browser.close()
        log("\nすべての処理が完了しました。")

def delete_custom_schedules_logic(log, schedules_text, class_names_str):
    """個別日程で日程を削除するロジック"""
    log("個別日程による日程削除を開始します...")
    schedules = ScheduleHelper.parse_custom_schedules(schedules_text)
    if not schedules:
        log("有効な日程が入力されていません。\n例: 2025-08-27\t14:00~15:30")
        return
    
    target_class_names = [name.strip() for name in class_names_str.strip().split('\n') if name.strip()]
    if not target_class_names:
        log("エラー: 削除対象の講座名が入力されていません。")
        return
    
    log(f"削除対象の講座名: {', '.join(target_class_names)}")

    try:
        playwright, browser, context = PlaywrightHelper.create_browser_context()
        page = context.new_page()

        for schedule_index, (date_str, start_str, end_str) in enumerate(schedules, 1):
            log(f"\n--- 日程 {schedule_index}/{len(schedules)}: {date_str} {start_str}~{end_str} を削除します ---")
            
            # 日付パラメータを作成
            target_date = date.fromisoformat(date_str)
            date_param = URLHelper.format_date_param(target_date)
            base_url = URLHelper.build_schedule_url(date_param)
            
            found_schedule = False
            
            # 共通化されたページング処理を使用
            log(f"アクセス中: {base_url}")
            page.goto(base_url, timeout=60000)
            if not PlaywrightHelper.handle_403_forbidden(page, log):
                continue

            found_schedule = ScheduleHelper.find_and_delete_schedules(page, log, target_class_names, start_str)
            
            if not found_schedule:
                log(f"講座名と開始時刻 {start_str} に一致する日程が見つかりませんでした。")

            # 日程が見つからなかった場合のログ
            if not found_schedule:
                log(f"日程 {schedule_index}/{len(schedules)}: {date_str} {start_str}~{end_str} は見つかりませんでした。")
    except Exception as e:
        log(f"エラーが発生しました: {e}")
    finally:
        if 'browser' in locals():
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
    url_input = ft.TextField(
        label="日程追加ページのURL (複数の場合は改行して入力)", 
        width=600,
        multiline=True,
        min_lines=3,
        hint_text="例:\nhttps://www.street-academy.com/session_details/new_multi_session?classdetailid=123456\nhttps://www.street-academy.com/session_details/new_multi_session?classdetailid=789012",
        hint_style=ft.TextStyle(color="#bbbbbb")
    )
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

    # --- 日程削除方式の選択ラジオボタン ---
    delete_mode = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="custom", label="個別日程削除"),
            ft.Radio(value="normal", label="連続日程削除")
        ]),
        value="custom"
    )

    # --- 連続日程削除用UI ---
    delete_start_date = ft.TextField(label="開始日 (YYYY-MM-DD)", width=200)
    delete_end_date = ft.TextField(label="終了日 (YYYY-MM-DD)", width=200)
    class_names_input = ft.TextField(
        label="削除対象の講座名 (複数ある場合は改行して入力)",
        multiline=True,
        min_lines=3,
        width=600,
        hint_text="例:\nNotebookLMに資料投入！\nAIとGASで夢の時短術！",
        hint_style=ft.TextStyle(color="#bbbbbb")
    )
    delete_by_name_button = ft.ElevatedButton("連続日程削除", bgcolor="red", color="white")

    # --- 個別日程削除用UI ---
    delete_custom_schedules_input = ft.TextField(
        label="削除対象の日程リスト (例: 2025-08-27\t14:00~15:30)",
        multiline=True,
        min_lines=3,
        width=600,
        hint_text="例:\n2025-08-27\t14:00~15:30\n2025-08-28\t12:00~14:00",
        hint_style=ft.TextStyle(color="#bbbbbb")
    )
    delete_custom_button = ft.ElevatedButton("個別日程削除", bgcolor="orange", color="white")

    # 排他制御用フラグ
    delete_running = {'value': False}

    def set_delete_running(state: bool):
        delete_running['value'] = state
        delete_by_name_button.disabled = state
        delete_custom_button.disabled = state
        page.update()

    def handle_delete_schedules(e):
        if delete_running['value']:
            return
        set_delete_running(True)
        def wrapped():
            try:
                run_playwright_task(page, log_view, delete_schedules_logic, delete_start_date.value, delete_end_date.value, class_names_input.value)
            finally:
                set_delete_running(False)
        run_in_thread(wrapped)
    delete_by_name_button.on_click = handle_delete_schedules

    def handle_delete_custom_schedules(e):
        if delete_running['value']:
            return
        set_delete_running(True)
        def wrapped():
            try:
                run_playwright_task(page, log_view, delete_custom_schedules_logic, delete_custom_schedules_input.value, class_names_input.value)
            finally:
                set_delete_running(False)
        run_in_thread(wrapped)
    delete_custom_button.on_click = handle_delete_custom_schedules

    # --- 日程削除フォームの切り替え ---
    normal_delete_form = ft.Column([
        class_names_input,
        ft.Row([delete_start_date, delete_end_date]),
        delete_by_name_button
    ])
    custom_delete_form = ft.Column([
        class_names_input,
        delete_custom_schedules_input,
        delete_custom_button
    ])

    delete_form_container = ft.Container()

    def update_delete_form(_=None):
        if delete_mode.value == "normal":
            delete_form_container.content = normal_delete_form
        else:
            delete_form_container.content = custom_delete_form
        page.update()

    delete_mode.on_change = update_delete_form
    update_delete_form()

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
            delete_mode,
            delete_form_container,
            ft.Divider(),
            ft.Text("実行ログ", size=16),
            log_container
        ], expand=True, scroll=ft.ScrollMode.ADAPTIVE)
    )

if __name__ == "__main__":
    ft.app(target=main)
```

【重要】 作成した`app.py`を開き、先頭部分の**設定項目（`EMERGENCY_CONTACT`）**を自分の情報に必ず書き換えてください。

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
    *   **個別日程追加**の場合:
        - 「個別日程追加」を選択
        - 日程リストに日時を入力（例: `2025-08-27	14:00~15:30`）
        - 【個別日程追加】ボタンをクリック
    *   **連続日程追加**の場合:
        - 「連続日程追加」を選択
        - 追加したい【開始日】と【終了日】を`YYYY-MM-DD`形式で入力
        - 【連続日程追加】ボタンをクリック（8:00〜22:00の講座が自動生成）
3.  **日程を削除する場合**:
    *   **個別日程削除**の場合:
        - 「個別日程削除」を選択
        - 削除したい講座名を入力
        - 削除したい日程リストを入力（例: `2025-08-27	14:00~15:30`）
        - 【個別日程削除】ボタンをクリック
    *   **連続日程削除**の場合:
        - 「連続日程削除」を選択
        - 削除したい講座名を入力
        - 削除したい【開始日】と【終了日】を入力
        - 【連続日程削除】ボタンをクリック（期間内の指定講座の全日程を削除）

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
2.  `cd` コマンドで、前回作成した `street_academy_automation` フォルダに移動します。
    ```sh
    # 例
    cd ~/Desktop/street_academy_automation
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
    2.  **個別日程追加**の場合:
        - 「個別日程追加」を選択
        - 日程リストに日時を入力（例: `2025-08-27	14:00~15:30`）
        - 【個別日程追加】ボタンをクリック
    3.  **連続日程追加**の場合:
        - 「連続日程追加」を選択
        - 追加したい【開始日】と【終了日】を`YYYY-MM-DD`形式で入力
        - 【連続日程追加】ボタンをクリック（8:00〜22:00の講座が自動生成）
*   **日程を削除する場合**:
    1.  **個別日程削除**の場合:
        - 「個別日程削除」を選択
        - 削除したい講座名を入力
        - 削除したい日程リストを入力（例: `2025-08-27	14:00~15:30`）
        - 【個別日程削除】ボタンをクリック
    2.  **連続日程削除**の場合:
        - 「連続日程削除」を選択
        - 削除したい講座名を入力
        - 削除したい【開始日】と【終了日】を入力
        - 【連続日程削除】ボタンをクリック（期間内の指定講座の全日程を削除）

実行するとブラウザが自動で動き出し、処理が終わると自動で閉じます。

### ステップ3：ツールの終了

1.  ツールウィンドウを閉じます。
2.  ターミナルで `deactivate` コマンドを実行して、仮想環境を終了します。
    ```sh
    deactivate
    ```
