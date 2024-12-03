from fastapi import BackgroundTasks
from threading import Lock
import db as db
import configuration as cf
import time
from core.config import settings

crawl_status = {"status": "idle", "progress": 0, "total": 0}
results_lock = Lock()

def start_crawl_service(url: str, num_threads: int, background_tasks: BackgroundTasks):
    if crawl_status["status"] == "running":
        return {"error": "A crawl task is already running"}
    
    background_tasks.add_task(crawl, url, num_threads)
    crawl_status["status"] = "running"
    return {"message": "Crawling task started", "status": crawl_status}

def get_crawl_status_service():
    return crawl_status

def init_driver_and_login():
    if not settings.fb_user or not settings.fb_password:
        raise ValueError("Facebook username or password not configured properly.")
    
    """Initialize a WebDriver instance and log in to Facebook"""
    driver = cf.configure_driver()
    driver.get(cf.get_url())
    if not cf.login_facebook(settings.settings.fb_user, settings.fb_password, driver):
        print("Login failed.")
        driver.quit()
        return None
    print("Login successful.")
    return driver

def crawl(url: str, num_threads: int):
    global crawl_status
    crawl_status["status"] = "running"
    all_posts_comments = {}
    
    try:
        drivers = [init_driver_and_login() for _ in range(num_threads)]
        drivers = [driver for driver in drivers if driver]

        if not drivers:
            crawl_status["status"] = "failed"
            raise Exception("Failed to initialize drivers")

        driver = drivers[0]
        driver.get(url)
        all_links = cf.get_all_posts_links(driver)

        if not all_links:
            crawl_status["status"] = "failed"
            raise Exception("No links found")

        links_list = list(all_links.items())
        crawl_status["total"] = len(links_list)

        for timestamp, link in links_list:
            try:
                driver.get(link)
                article_info = cf.get_article_data(driver)
                all_posts_comments[timestamp] = article_info
                with results_lock:
                    crawl_status["progress"] += 1
            except Exception as e:
                print(f"Error processing {link}: {e}")

        db.save_to_database(all_posts_comments)
        crawl_status["status"] = "completed"
    except Exception as e:
        crawl_status["status"] = f"failed: {e}"
    finally:
        for driver in drivers:
            driver.quit()


