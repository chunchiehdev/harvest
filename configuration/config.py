from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import random
import os
from dotenv import load_dotenv


load_dotenv()
path_mac = os.getenv('driver_path_mac')
path_windows = os.getenv('driver_path_win')

def type_like_human(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.5))  # random delay 0.1 to 0.5

def login_facebook(username, password, driver):
    '''Log in to Facebook'''

    try:
        username_field = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "email"))
        )
        type_like_human(username_field, username)  # Simulate human typing of the username

        password_field = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "pass"))
        )
        type_like_human(password_field, password)  # Simulate human typing of the password
        
        time.sleep(random.uniform(1, 3)) 
        password_field.send_keys(Keys.RETURN)
        print("Logged in successfully")
        return True

    except Exception as e:
        print(f"Login failed: {str(e)}")
        return False
       
def configure_driver():
    '''Configure the webdriver'''

    # Configurations
    webdriver_path = path_mac 
    chrome_options = Options()

    # Turn off Chrome notification and set language to English
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})

    # Start the service
    service = Service(webdriver_path)

    # Start the driver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver


def set_up_driver(url, service):
    '''Set up the driver and get url'''
    driver = configure_driver()

    # get url
    driver.get(url)
    return driver
# def configure_driver():
#     '''Configure the webdriver with optimized settings'''
    
#     chrome_options = Options()
    
#     # 基本設置
#     chrome_options.add_argument("--disable-notifications")  # 禁用通知
#     chrome_options.add_experimental_option('prefs', {
#         'intl.accept_languages': 'en,en_US',  # 設置語言
#         'profile.default_content_setting_values': {
#             'notifications': 2,  # 禁用通知
#             'images': 2,  # 禁用圖片加載以提升速度
#             'javascript': 1  # 啟用 JavaScript
#         },
#         'profile.managed_default_content_settings': {
#             'images': 2  # 禁用圖片
#         }
#     })
    
#     # 性能優化設置
#     chrome_options.add_argument('--disable-gpu')  # 禁用GPU加速
#     chrome_options.add_argument('--no-sandbox')  # 禁用沙盒模式
#     chrome_options.add_argument('--disable-dev-shm-usage')  # 禁用共享內存
#     chrome_options.add_argument('--disable-infobars')  # 禁用信息欄
#     chrome_options.add_argument('--disable-extensions')  # 禁用擴展
#     chrome_options.add_argument('--disable-browser-side-navigation')  # 禁用瀏覽器側邊導航
#     chrome_options.add_argument('--disable-site-isolation-trials')  # 禁用站點隔離
#     chrome_options.add_argument('--ignore-certificate-errors')  # 忽略證書錯誤
#     chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # 避免被檢測為自動化測試
    
#     # 記憶體優化
#     chrome_options.add_argument('--aggressive-cache-discard')  # 積極丟棄快取
#     chrome_options.add_argument('--disable-cache')  # 禁用快取
#     chrome_options.add_argument('--disable-application-cache')  # 禁用應用程式快取
#     chrome_options.add_argument('--disable-offline-load-stale-cache')  # 禁用離線加載過期快取
#     chrome_options.add_argument('--disk-cache-size=0')  # 將磁碟快取大小設為0
    
#     # 添加 user-agent
#     chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
#     try:
#         # 創建並配置 service
#         service = Service(path_mac)
        
#         # 創建 driver
#         driver = webdriver.Chrome(service=service, options=chrome_options)
        
#         # 設置頁面加載超時
#         driver.set_page_load_timeout(30)
        
#         # 設置腳本超時
#         driver.set_script_timeout(30)
        
#         # 設置隱式等待時間
#         driver.implicitly_wait(10)
        
#         return driver
        
#     except Exception as e:
#         print(f"Error configuring driver: {str(e)}")
#         raise

