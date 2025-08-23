import flet as ft
import time
from datetime import date, timedelta
from playwright.sync_api import sync_playwright, expect
import threading
import os

# 認証情報ファイルのパス (このままでOK)
AUTH_FILE_PATH = 'playwright_auth.json'

# ①：あなたの緊急連絡先(電話番号)に書き換えてください
EMERGENCY_CONTACT = '090-1234-5678' 

# ②：追加したい時間帯 (8時〜22時でよければ変更不要)
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

def add_schedules_logic(log, urls, contact, schedules_text):
    """個別日程で日程を追加するロジック"""
    log("個別日程による日程追加を開始します...")
    schedules = parse_custom_schedules(schedules_text)
    if not schedules:
        log("有効な日程が入力されていません。\n例: 2025-08-27\t14:00~15:30")
        return
    
    # URLを改行区切りで分割
    url_list = [url.strip() for url in urls.strip().split('\n') if url.strip()]
    if not url_list:
        log("エラー: 有効なURLが入力されていません。")
        return
    
    log(f"処理対象のURL数: {len(url_list)}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        if not os.path.exists(AUTH_FILE_PATH):
            log("エラー: 認証ファイル 'playwright_auth.json' が見つかりません。")
            return
        context = browser.new_context(storage_state=AUTH_FILE_PATH)
        page = context.new_page()
        
        for url_index, url in enumerate(url_list, 1):
            log(f"\n=== URL {url_index}/{len(url_list)}: {url} ===")
            for schedule_index, (date_str, start_str, end_str) in enumerate(schedules, 1):
                log(f"\n--- 日程 {schedule_index}/{len(schedules)}: {date_str} {start_str}~{end_str} を追加します ---")
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
                log(f"--- 日程 {schedule_index}/{len(schedules)}: {date_str} {start_str}~{end_str} の日程追加が完了しました！ ---")
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
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        if not os.path.exists(AUTH_FILE_PATH):
            log("エラー: 認証ファイル 'playwright_auth.json' が見つかりません。")
            return
        context = browser.new_context(storage_state=AUTH_FILE_PATH)
        page = context.new_page()

        for url_index, url in enumerate(url_list, 1):
            log(f"\n=== URL {url_index}/{len(url_list)}: {url} ===")
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

def delete_custom_schedules_logic(log, schedules_text, class_names_str):
    """個別日程で日程を削除するロジック"""
    log("個別日程による日程削除を開始します...")
    schedules = parse_custom_schedules(schedules_text)
    if not schedules:
        log("有効な日程が入力されていません。\n例: 2025-08-27\t14:00~15:30")
        return
    
    target_class_names = [name.strip() for name in class_names_str.strip().split('\n') if name.strip()]
    if not target_class_names:
        log("エラー: 削除対象の講座名が入力されていません。")
        return
    
    log(f"削除対象の講座名: {', '.join(target_class_names)}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        if not os.path.exists(AUTH_FILE_PATH):
            log("エラー: 認証ファイル 'playwright_auth.json' が見つかりません。")
            return
        context = browser.new_context(storage_state=AUTH_FILE_PATH)
        page = context.new_page()

        for schedule_index, (date_str, start_str, end_str) in enumerate(schedules, 1):
            log(f"\n--- 日程 {schedule_index}/{len(schedules)}: {date_str} {start_str}~{end_str} を削除します ---")
            
            # 日付パラメータを作成
            target_date = date.fromisoformat(date_str)
            date_param = target_date.strftime('%Y-%-m-%-d')
            
            ### 主催団体用
            base_url = f"https://www.street-academy.com/dashboard/organizers/schedule_list?date={date_param}"
            ### 個人用
            # base_url = f"https://www.street-academy.com/dashboard/steachers/manage_class_dates?date={date_param}"
            
            found_schedule = False
            
            # 削除対象の講座がすべて削除されるまで繰り返し
            while True:
                # 講座一覧ページにアクセス
                log(f"アクセス中: {base_url}")

                # 403 Forbidden検知＆リトライ
                for retry in range(3):  # 最大3回リトライ
                    page.goto(base_url, timeout=60000)
                    body_html = page.content()
                    if "403 Forbidden" in body_html:
                        log("403 Forbidden画面を検知。2分間待機してリトライします。")
                        time.sleep(120)
                    else:
                        break
                else:
                    log("403 Forbiddenが解消しませんでした。次の日程へ進みます。")
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
                    log("日程リンクも「講座がありません」も見つかりませんでした。次の日程へ進みます。")
                    break

                log("ページの読み込み完了。")
                all_schedule_links = schedule_links_locator

                if all_schedule_links.count() == 0:
                    log("この日付に削除可能な日程はありません。")
                    break

                # 削除対象の講座を探す
                target_link = None
                for i in range(all_schedule_links.count()):
                    try:
                        link = all_schedule_links.nth(i)
                        link_text = link.inner_text()
                        
                        # 講座名の一致を確認
                        if not any(class_name in link_text for class_name in target_class_names):
                            continue
                        
                        # 開始時刻の情報を抽出（例: "20:00" のような形式）
                        import re
                        time_match = re.search(r'(\d{1,2}):(\d{2})', link_text)
                        if time_match:
                            start_hour, start_min = map(int, time_match.groups())
                            link_start_time = f"{start_hour:02d}:{start_min:02d}"
                            
                            # 開始時刻が一致するかチェック
                            if link_start_time == start_str:
                                target_link = link
                                break
                    except Exception as e:
                        log(f"  - 講座情報の取得中にエラーが発生しました: {e}")
                        continue

                # 削除対象の講座が見つからない場合は終了
                if target_link is None:
                    if not found_schedule:
                        log(f"講座名と開始時刻 {start_str} に一致する日程が見つかりませんでした。")
                    break

                # 削除処理を実行
                try:
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

                    log(f"  - 日程削除が完了しました！")
                    time.sleep(3)
                    found_schedule = True
                    
                    # 削除処理が完了したら、講座一覧ページに戻って再度削除対象を探す
                    continue
                    
                except Exception as e:
                    log(f"  - 削除処理中にエラーが発生しました: {e}")
                    break

            # 日程が見つからなかった場合のログ
            if not found_schedule:
                log(f"日程 {schedule_index}/{len(schedules)}: {date_str} {start_str}~{end_str} は見つかりませんでした。")

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
        hint_text="例:\nNotebookLMに資料投入！\nAIとGASで夢の時短術！",
        hint_style=ft.TextStyle(color="#bbbbbb")
    )
    delete_by_name_button = ft.ElevatedButton("連続日程削除", bgcolor="red", color="white")

    # --- 個別日程削除用UI ---
    delete_custom_class_names_input = ft.TextField(
        label="削除対象の講座名 (複数ある場合は改行して入力)",
        multiline=True,
        min_lines=2,
        width=600,
        hint_text="例:\nNotebookLMに資料投入！\nAIとGASで夢の時短術！",
        hint_style=ft.TextStyle(color="#bbbbbb")
    )
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
                run_playwright_task(page, log_view, delete_custom_schedules_logic, delete_custom_schedules_input.value, delete_custom_class_names_input.value)
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
        delete_custom_class_names_input,
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
