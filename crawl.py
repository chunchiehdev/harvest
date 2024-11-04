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

load_dotenv()
fb_user = os.getenv('user')
fb_password = os.getenv('password')
current_path = os.getcwd()

if not fb_user or not fb_password:
    raise ValueError("Facebook username or password not set in environment variables.")

results_lock = Lock()

def save_progress(data):
    """save data regularly"""
    with tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8') as temp_file:
        json.dump(data, temp_file, ensure_ascii=False, indent=4)
        temp_file.flush()
        shutil.move(temp_file.name, 'all_posts_comments_progress.json')

def crawl(driver, url, username, password, threshold, ite):

    all_posts_comments = {}

    try:
        driver.get(url)
        # Login Facebook
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
        
        driver_pool = []
        max_workers = min(3, os.cpu_count() * 2)

        print(f"Initializing {max_workers} drivers...")

        for i in range(max_workers):
            try:
                new_driver = cf.configure_driver()
                new_driver.get(url)

                if not cf.login_facebook(username, password, new_driver):
                    print(f"Login failed for driver { i+1 }")
                    new_driver.quit()
                    continue
                print(f"Driver {i+1} logged in successfully")
                driver_pool.append(new_driver)
            except Exception as e:
                print(f"Failed to initialize driver {i+1}: {str(e)}")
                if new_driver:
                    new_driver.quit()

        if not driver_pool:
            print("No drivers successfully initialized")
            return None

        links_list = list(all_links.items())
        chunk_size = len(links_list) // len(driver_pool) + (1 if len(links_list) % len(driver_pool) else 0)
        link_chunks = [links_list[i:i + chunk_size] for i in range(0, len(links_list), chunk_size)]
        print(f"Divided {len(links_list)} links into {len(link_chunks)} chunks")

        def process_chunk(chunk, driver_index):
            """handing a set of links"""
            current_driver = driver_pool[driver_index]
            thread_results = {}
            
            for timestamp, link in chunk:
                try:
                    print(f"Driver {driver_index + 1} processing: {link}")
                    time.sleep(random.uniform(1, 3))
                    
                    current_driver.get(link)
                    article_info = cf.get_filtered_links_with_info_profile_comment(current_driver)

                    thread_results[timestamp] = {
                            "link": link,
                            "author": article_info.get("author"),
                            "content": article_info.get("content"),
                            "post_time": article_info.get("post_time"),
                            "comments": article_info.get("comments")
                    }
                          
                except Exception as e:
                    print(f"Error processing {link}: {str(e)}")
            
            with results_lock:
                for timestamp, data in thread_results.items():
                    # Check if this timestamp already exists to prevent duplicates
                    if timestamp not in all_posts_comments:
                        all_posts_comments[timestamp] = data
                    else:
                        print(f"Duplicate timestamp {timestamp} found, skipping.")
                if len(all_posts_comments) % 10 == 0:
                    save_progress(all_posts_comments)
                    print(f"Progress saved: {len(all_posts_comments)} posts processed")


            return thread_results

        threads = []

        for i, chunk in enumerate(link_chunks):
            if i < len(driver_pool):  # Ensure there are enough drivers
                thread = threading.Thread(
                    target=lambda c, di: process_chunk(c, di),
                    args=(chunk, i)
                )
                threads.append(thread)
                thread.start()
                print(f"Started thread {i+1} with {len(chunk)} links")

        for i, thread in enumerate(threads):
            thread.join()
            print(f"Thread {i+1} completed")

        print("Cleaning up drivers...")
        for d in driver_pool:
            try:
                d.quit()
            except Exception as e:
                print(f"Error closing driver: {str(e)}")

        # 儲存最終結果
        save_progress(all_posts_comments)
        print("Crawling completed")
        return all_posts_comments
    
    except Exception as e:
        print(f"Fatal error occurred: {str(e)}")
        # 確保清理所有資源
        try:
            for d in driver_pool:
                d.quit()
        except:
            pass
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