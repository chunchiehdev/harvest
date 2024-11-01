import configuration as cf
import pandas as pd
import numpy as np
import json
import os
import os 
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import time
from io import StringIO

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

        # if not cf.scroll_and_click_button(driver):
        #     print("Failed to scroll and click button.")
        #     return None

        cf.get_filtered_links_with_info_profile_comment(driver)
        
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