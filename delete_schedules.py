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
                    # 「講座がありません」が表示されているか確認
                    no_schedule_text = page.locator("text=講座がありません")
                    if no_schedule_text.is_visible():
                        print("「講座がありません」と表示されています。")
                    else:
                        # 念のため、他の理由で日程がない場合もログに残す
                        print("削除可能な日程は見つかりませんでした。")
                    
                    print(f"{single_date.strftime('%Y-%m-%d')} の処理を終了します。")
                    break # whileループを抜けて、次の日付の処理へ

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
                time.sleep(3) # サーバー処理とページ遷移のために3秒待機

        print("\nすべての指定された期間の日程削除が完了しました。")
        browser.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使い方: python delete_schedules.py YYYY-MM-DD YYYY-MM-DD")
        sys.exit(1)
    
    start_date_arg = sys.argv[1]
    end_date_arg = sys.argv[2]
    run(start_date_arg, end_date_arg)
