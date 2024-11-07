import configuration as cf
import os
from dotenv import load_dotenv
import time
import json
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

results_lock = Lock()

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

def init_driver_and_login():
    """Initialize a WebDriver instance and log in to Facebook"""
    driver = cf.configure_driver()
    driver.get(cf.get_url())
    if not cf.login_facebook(fb_user, fb_password, driver):
        print("Login failed.")
        driver.quit()
        return None
    print("Login successful.")
    return driver

def process_links(links, driver, all_posts_comments):
    """Process a list of links with a single driver"""
    for timestamp, link in links:
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

def crawl(url, num_threads=3):
    """Main crawl function to process all links using multiple threads"""
    all_posts_comments = {}

    # Initialize drivers and log in
    drivers = [init_driver_and_login() for _ in range(num_threads)]
    drivers = [driver for driver in drivers if driver is not None]

    if not drivers:
        print("Failed to initialize any drivers.")
        return None

    # Get all links to process
    driver = drivers[0]
    driver.get(url)
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
    links_list = list(all_links.items())
    chunk_size = len(links_list) // len(drivers) + (1 if len(links_list) % len(drivers) else 0)
    link_chunks = [links_list[i:i + chunk_size] for i in range(0, len(links_list), chunk_size)]

    # Use ThreadPoolExecutor to handle each chunk with a separate driver
    with ThreadPoolExecutor(max_workers=len(drivers)) as executor:
        futures = [
            executor.submit(process_links, chunk, drivers[i], all_posts_comments)
            for i, chunk in enumerate(link_chunks)
        ]
        for future in futures:
            future.result()  # Wait for all threads to complete

    save_progress(all_posts_comments)
    print("Crawling completed")

    # Clean up all drivers
    for driver in drivers:
        driver.quit()

    return all_posts_comments

if __name__ == '__main__':
    # Set parameters
    url = cf.get_url()
    num_threads = 2  # Set the number of threads (and drivers)

    crawl(url, num_threads)
