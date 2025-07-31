import json

def parse_cookie_string(cookie_str):
    cookies = []
    for part in cookie_str.split(";"):
        if "=" in part:
            name, value = part.strip().split("=", 1)
            cookies.append({"name": name, "value": value, "domain": ".chatgpt.com", "path": "/"})
    return cookies

def get_cookies_from_file(filepath="cookies.json"):
    try: 
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception as e:
        return None
    
