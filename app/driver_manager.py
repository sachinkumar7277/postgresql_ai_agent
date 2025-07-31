import undetected_chromedriver as uc
from .cookies import get_cookies_from_file
from .session_utils import load_session_url
import time
import json

driver = None
def get_driver():
    global driver
    if driver is None:
        
        print("######################################### Setting up deriver  $$$$$$$$$$$$$$$$$$$$$$$$$$$$44")
        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        
        # Optional: headless mode if needed
        # options.add_argument("--headless=new")
        print("######################################### Adding chrome into driver  $$$$$$$$$$$$$$$$$$$$$$$$$$$$44")
        driver = uc.Chrome(options=options)
        print("######################################### Launching gpt  $$$$$$$$$$$$$$$$$$$$$$$$$$$$44")
        driver.get("https://chatgpt.com")
        print("######################################### Launched gpt  $$$$$$$$$$$$$$$$$$$$$$$$$$$$44")
        time.sleep(5)
        print("######################################### 5 sec delay here gpt  $$$$$$$$$$$$$$$$$$$$$$$$$$$$44")
        
        # Add cookies
        cookies = get_cookies_from_file()
        if cookies:
            print("######################################### Setting up cookies  $$$$$$$$$$$$$$$$$$$$$$$$$$$$44")
            for cookie in cookies:
                if cookie["name"].startswith("__Host-"):
                    print(f"❌ Skipping HTTP-only or secure cookie: {cookie['name']}")
                    continue
                try:
                    if 'sameSite' in cookie:
                        del cookie['sameSite']  # selenium sometimes errors on this
                    driver.add_cookie(cookie)
                except Exception as e:
                    print(f"❌ Failed to add cookie: {cookie}\nError: {e}")

        print("######################################### loading existing settion id  $$$$$$$$$$$$$$$$$$$$$$$$$$$$44")
        chatgpt_url = load_session_url()
        if chatgpt_url:
            print(f"Loading existing ChatGPT session: {chatgpt_url}")
            driver.get(chatgpt_url)
        else:
            print("Opening new ChatGPT session")
            driver.get("https://chatgpt.com/")
            time.sleep(150)  # Give yourself time to log in manually
            # Step 3: Save cookies
            cookies = driver.get_cookies()
            with open("cookies.json", "w") as f:
                json.dump(cookies, f)

            print("✅ Cookies saved to cookies.json")
            time.sleep(5)

    return driver


def login_into_ai_and_save_cookies():
    
    try:
        driver = get_driver()
        return {"status": 200, "msg": "login cookies saved"}
    except Exception as e:
        return {"error": e}
