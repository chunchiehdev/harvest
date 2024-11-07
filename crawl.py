import configuration as cf
import os
from dotenv import load_dotenv
import time
import json
import threading
from threading import Lock
import tempfile
import shutil
import random
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

load_dotenv()
fb_user = os.getenv('user')
fb_password = os.getenv('password')
current_path = os.getcwd()

if not fb_user or not fb_password:
    raise ValueError("Facebook username or password not set in environment variables.")

results_lock = threading.Lock()

def save_progress(data):
    """save data regularly"""
    try: 
        temp_file_path = None
        with tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8') as temp_file:
            temp_file_path = temp_file.name
    
            json.dump(data, temp_file, ensure_ascii=False, indent=4)
            temp_file.flush()
            
        time.sleep(0.1)

        if temp_file_path:
            try:
                if os.path.exists('posts_comments.json'):
                    os.remove('posts_comments.json')
                shutil.move(temp_file_path, 'posts_comments.json')
            except Exception as e:
                print(f"Error moving temporary file: {str(e)}")
                print(f"Data saved in temporary file: {temp_file_path}")
    except Exception as e:
        print(f"Error in save_progress: {str(e)}")

def process_link(link, timestamp, driver, all_posts_comments):
    """Process a single link with the given driver"""
    try:
        print(f"Processing link {link} at {timestamp}...")
        time.sleep(random.uniform(1, 3))
        
        driver.get(link)
        article_info = cf.get_article_data(driver)
        
        result = {
            "link": link,
            "author": article_info.get("author"),
            "content": article_info.get("content"),
            "post_time": article_info.get("post_time"),
            "file_links": article_info.get("file_links"),
            "comments": article_info.get("comments")
        }

        with results_lock:
            if timestamp not in all_posts_comments:
                all_posts_comments[timestamp] = result
                # Save progress every 10 posts
                if len(all_posts_comments) % 10 == 0:
                    save_progress(all_posts_comments)
                    print(f"Progress saved: {len(all_posts_comments)} posts processed")

    except Exception as e:
        print(f"Error processing {link}: {str(e)}")

def crawl(url, username, password, threshold, ite):
    """Main crawl function to process all links"""
    all_posts_comments = {}

    try:
        driver = cf.configure_driver()

        driver.get(url)
        # Login to Facebook
        if not cf.login_facebook(username, password, driver):
            print("Login failed.")
            return None
        print("Login successful. Starting to scrape data...")
        
        retry_count = 0
        max_retries = 3
        all_links = None

        while retry_count < max_retries:
            try:
                all_links = cf.get_all_posts_links(driver)
                break
            except Exception as e:
                retry_count += 1
                print(f"Error getting links (attempt {retry_count}/{max_retries}): {e}")
                if retry_count == max_retries:
                    raise
                time.sleep(2)

        if not all_links:
            print("No links found.")
            return None

        print(f"Found {len(all_links)} links")
                
        with open('post_links.json', 'w', encoding='utf-8') as f:
            json.dump(all_links, f, ensure_ascii=False, indent=4)
        
        links_list = list(all_links.items())

        for timestamp, link in links_list:
            process_link(link, timestamp, driver, all_posts_comments)

        save_progress(all_posts_comments)
        print("Crawling completed")
        return all_posts_comments

    except Exception as e:
        print(f"Fatal error occurred: {str(e)}")
        return []
    finally:
        driver.quit()  

if __name__ == '__main__':
    threshold = 60 #Base on the Internet speed (300 - 400)
    ite = 20 # Use to check whether it reaches the end of the page (Should be 20 - 30)

    # Login info
    username = fb_user 
    password = fb_password 

    url = cf.get_url()

    crawl(url, username, password, threshold, ite)
  