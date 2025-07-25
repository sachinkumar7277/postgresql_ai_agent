import undetected_chromedriver as uc
import json
import time

# Step 1: Launch browser
options = uc.ChromeOptions()
options.add_argument("--start-maximized")
driver = uc.Chrome(options=options)

# Step 2: Open ChatGPT and wait for manual login
driver.get("https://chatgpt.com")
print("🚀 Please log in manually. Waiting 60 seconds...")

time.sleep(200)  # Give yourself time to log in manually

# Step 3: Save cookies
cookies = driver.get_cookies()
with open("cookies.json", "w") as f:
    json.dump(cookies, f)

print("✅ Cookies saved to cookies.json")
driver.quit()
