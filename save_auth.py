from playwright.sync_api import sync_playwright, expect

AUTH_FILE_PATH = 'playwright_auth.json'
# ログイン後に遷移する実際のURL
LOGIN_SUCCESS_URL = "https://www.street-academy.com/dashboard/steachers"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    # ストアカのログインページにアクセス
    print("ストアカのログインページを開きます。")
    page.goto("https://www.street-academy.com/d/users/sign_in")
    
    print("\nブラウザ上で手動でログインしてください。")
    print(f"ログイン後、'{LOGIN_SUCCESS_URL}' に遷移すると自動的に終了します。")
    
    # ログイン後、指定されたダッシュボードURLにリダイレクトされるのを待つ
    # タイムアウトは5分 (300,000ミリ秒) に設定
    try:
        expect(page).to_have_url(LOGIN_SUCCESS_URL, timeout=300000)
        print("\nログインを検知しました。")
    except Exception as e:
        print(f"\nログインがタイムアウトまたは検知できませんでした: {e}")
        # エラーが出た場合、現在のURLを出力してデバッグしやすくする
        current_url = page.url
        print(f"現在のURL: {current_url}")
        print("想定されるURLと異なっている可能性があります。")
        browser.close()
        exit()

    # ログイン後の状態をファイルに保存
    context.storage_state(path=AUTH_FILE_PATH)
    
    print(f"認証情報を {AUTH_FILE_PATH} に保存しました。")
    browser.close()
