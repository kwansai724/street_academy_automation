import flet as ft
import time
from datetime import date, timedelta
from playwright.sync_api import sync_playwright, expect
import threading
import os

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

    log_text.value = "" # ログをクリア
    page_instance.update()

    try:
        task_func(log, *args)
    except Exception as e:
        log(f"予期せぬエラーが発生しました: {e}")
        print(f"エラー詳細: {e}")

def add_schedules_logic(log, url, contact, start_str, end_str):
    """ 日程追加のメインロジック """
    log("日程追加処理を開始します...")
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
            expect(page.get_by_text("講座の予約受付が開始されました！")).to_be_visible(timeout=20000)
            log(f"--- {single_date.strftime('%Y-%m-%d')} の日程追加が完了しました！ ---")
            time.sleep(3)
        
        browser.close()
        log("\nすべての処理が完了しました。")

def delete_schedules_logic(log, start_str, end_str, class_names_str):
    """ 日程削除のメインロジック """
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
            daily_schedule_url = f"https://www.street-academy.com/dashboard/steachers/manage_class_dates?date={date_param}"
            log(f"\n--- {single_date.strftime('%Y-%m-%d')} の日程削除を開始します ---")

            while True:
                log(f"アクセス中: {daily_schedule_url}")
                page.goto(daily_schedule_url, timeout=60000)
                page.wait_for_load_state('networkidle')
                
                all_schedule_links = page.locator('a.dashboard-session_container[href*="/show_attendance?sessiondetailid="]')
                
                if all_schedule_links.count() == 0:
                    log("この日付に削除対象の講座はありません。")
                    break
                
                target_link = None
                for i in range(all_schedule_links.count()):
                    link = all_schedule_links.nth(i)
                    link_text = link.inner_text()
                    if any(class_name in link_text for class_name in target_class_names):
                        target_link = link
                        break

                if target_link is None:
                    log("この日付に削除対象の講座はありません。")
                    break
                
                target_text = target_link.inner_text()
                log(f"  - 削除対象: {target_text.strip().replace('\n', ' ')}")
                
                target_link.click()
                
                cancel_button_1 = page.get_by_role("link", name="開催をキャンセルする")
                expect(cancel_button_1).to_be_visible()
                cancel_button_1.click()
                
                modal_cancel_button = page.locator("#sa-modal-cancel").get_by_role("button", name="開催キャンセル")
                expect(modal_cancel_button).to_be_visible()
                
                page.once("dialog", lambda dialog: dialog.accept())
                modal_cancel_button.click()
                
                log("  - キャンセル処理を実行しました。")
                time.sleep(3)
        
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

    # 日程追加用UI
    url_input = ft.TextField(label="日程追加ページのURL", value=TARGET_URL, width=600)
    contact_input = ft.TextField(label="緊急連絡先", value=EMERGENCY_CONTACT, width=300)
    add_start_date = ft.TextField(label="開始日 (YYYY-MM-DD)", width=200)
    add_end_date = ft.TextField(label="終了日 (YYYY-MM-DD)", width=200)
    
    def handle_add_schedules(e):
        run_in_thread(run_playwright_task, page, log_view, add_schedules_logic, url_input.value, contact_input.value, add_start_date.value, add_end_date.value)

    add_button = ft.ElevatedButton("日程を追加", on_click=handle_add_schedules, bgcolor="blue", color="white")

    # 日程削除用UI
    delete_start_date = ft.TextField(label="開始日 (YYYY-MM-DD)", width=200)
    delete_end_date = ft.TextField(label="終了日 (YYYY-MM-DD)", width=200)
    class_names_input = ft.TextField(
        label="削除対象の講座名 (複数ある場合は改行して入力)",
        multiline=True,
        min_lines=3,
        hint_text="例:\nNotebookLMに資料投入！\nAIとGASで夢の時短術！"
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
            url_input,
            contact_input,
            ft.Row([add_start_date, add_end_date]),
            add_button,
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
