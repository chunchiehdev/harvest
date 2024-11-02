import configuration as cf
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import time

load_dotenv()
fb_user = os.getenv('user')
fb_password = os.getenv('password')
current_path = os.getcwd()

def crawl(driver):

    try:
        path = os.path.abspath("index.html")

        driver.get(f"file://{path}")

        stories_container = driver.find_element(By.ID, "m_group_stories_container")

        next_page = stories_container.find_element(
                By.XPATH, 
                ".//div[1]/a[1]"
            )
        
        a = stories_container.find_element(
                By.XPATH, 
                "./div[1]/a[1]"
            )

        print("next_page.get_attribute", next_page.get_attribute('href'))
        print("first_div.get_attribute", a.get_attribute('href'))

        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return []
    
if __name__ == '__main__':

    
    driver = cf.configure_driver()
    # starter = 0
    # limit = 10

    crawl(driver)
  
    time.sleep(30)
    driver.quit()