from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import random

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
    chrome_options = Options()

    # Turn off Chrome notification and set language to English
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--headless")  
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
    chrome_options.add_argument("--disable-dev-shm-usage")  
    chrome_options.add_argument("--disable-gpu")  
    chrome_options.add_argument("--disable-software-rasterizer") 
    chrome_options.add_argument("--disable-extensions")  
    chrome_options.add_argument("--window-size=1920,1080")  
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver

def set_up_driver(url, service):
    '''Set up the driver and get url'''
    driver = configure_driver()

    # get url
    driver.get(url)
    return driver
