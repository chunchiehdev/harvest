import configuration as cf
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import time
import json

load_dotenv()
fb_user = os.getenv('user')
fb_password = os.getenv('password')
current_path = os.getcwd()

def crawl(driver, url, username, password, threshold, ite):

    try:
        driver.get(url)

        # Login Facebook
        if not cf.login_facebook(username, password, driver):
            print("Login failed.")
            return None

        print("Login successful. Starting to scrape data...")

        get_all_links = cf.get_all_posts_links(driver)
        print()
        print(get_all_links)
        print()
        print(f"總共收集到 {len(get_all_links)} 個連結")
                
        with open('post_links.json', 'w', encoding='utf-8') as f:
            json.dump(get_all_links, f, ensure_ascii=False, indent=4)
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return []
    
if __name__ == '__main__':

    cnt = 0
    threshold = 60 #Base on the Internet speed (300 - 400)
    ite = 20 # Use to check whether it reaches the end of the page (Should be 20 - 30)

    # Login info
    username = fb_user #your fb username
    password = fb_password #your fb password

    url = cf.get_url()
    driver = cf.configure_driver()
    # starter = 0
    # limit = 10

    crawl(driver, url, username, password, threshold, ite)
  
    time.sleep(30)
    driver.quit()