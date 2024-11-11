import configuration as cf
import os
from dotenv import load_dotenv
import time
import json
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor
from threading import Lock, Thread

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
                if os.path.exists(cf.POSTS_COMMENTS_PATH):
                    os.remove(cf.POSTS_COMMENTS_PATH)
                shutil.move(temp_file_path, cf.POSTS_COMMENTS_PATH)
            except Exception as e:
                print(f"Error moving temporary file: {str(e)}")
                print(f"Data saved in temporary file: {temp_file_path}")
    except Exception as e:
        print(f"Error in save_progress: {str(e)}")

def save_progress_async(data):
    """Start asynchronous saving of progress data."""
    Thread(target=save_progress, args=(data,)).start()

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
    local_results = {}

    for timestamp, link in links:
        try:
            print(f"Processing link {link} at {timestamp}...")
            driver.get(link)
            article_info = cf.get_article_data(driver)

            local_results[timestamp] = {
                "link": link,
                "author": article_info.get("author"),
                "content": article_info.get("content"),
                "post_time": article_info.get("post_time"),
                "file_links": article_info.get("file_links"),
                "comments": article_info.get("comments")
            }

        except Exception as e:
            print(f"Error processing {link}: {str(e)}")
    # Update the global dictionary once per batch to minimize lock contention
    with results_lock:
        all_posts_comments.update(local_results)

    # Save progress asynchronously every 50 entries to reduce I/O overhead
    if len(all_posts_comments) % 50 == 0:
        save_progress_async(all_posts_comments)

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
    print("start ...")
    # Set parameters
    start_time = time.time()

    url = cf.get_url()
    num_threads = 4  # Set the number of threads (and drivers)

    crawl(url, num_threads)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Total execution time: {elapsed_time:.2f} seconds")
