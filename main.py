import sys
import time
from datetime import date, timedelta
from playwright.sync_api import sync_playwright, expect

# --- 設定項目 ---
AUTH_FILE_PATH = 'playwright_auth.json'
TARGET_URL = 'https://www.street-academy.com/session_details/new_multi_session?classdetailid=196562'
HOURS_TO_ADD = list(range(9, 23))
EMERGENCY_CONTACT = '090-3057-8657' # ご自身のものに書き換えてください

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

def add_schedule_for_day(page, target_date):
    """HTML構造に完全準拠した日程追加関数"""
    print(f"\n--- {target_date.strftime('%Y-%m-%d')} の日程を追加します ---")

    # 最初の1つの日程ブロックを特定
    first_block = page.locator('div[data-repeater-item]').first
    
    # 最初のブロックの日付を設定
    print("最初の日付を設定中...")
    first_block.locator('select[name*="[session_startdate_year]"]').select_option(str(target_date.year))
    first_block.locator('select[name*="[session_startdate_month]"]').select_option(str(target_date.month))
    first_block.locator('select[name*="[session_startdate_day]"]').select_option(str(target_date.day))
    
    # 最初の時間 (9時) を設定
    start_hour = HOURS_TO_ADD[0]
    end_hour = start_hour + 1
    first_block.locator('select.js_start_time_hour').select_option(str(start_hour))
    # ★★★ 終了時間を設定する処理を追加 ★★★
    first_block.locator('select.js_end_time_hour').select_option(str(end_hour))
    print(f"{start_hour}:00 - {end_hour}:00 の日程を設定しました。")
    time.sleep(0.5)

    # 2つ目以降の時間 (10時から22時) をループで追加
    for hour in HOURS_TO_ADD[1:]:
        print(f"{hour}時の日程を追加します...")
        
        page.get_by_role("button", name="日程を複製する").click()
        
        last_block = page.locator('div[data-repeater-item]').last
        expect(last_block).to_be_visible()

        # 新しいブロックの時間を設定
        start_hour = hour
        end_hour = start_hour + 1 if start_hour < 23 else 23 # 23時の次は24時にならないように
        
        last_block.locator('select.js_start_time_hour').select_option(str(start_hour))
        # ★★★ 終了時間を設定する処理を追加 ★★★
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
            # ★★★ 緊急連絡先のセレクタをID指定に修正 ★★★
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
