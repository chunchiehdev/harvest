from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time


def get_url():
    '''Get the URL of a Facebook post from the user input'''
    # get url from input
    # url = input("Enter the URL: ")
    url = "https://mbasic.facebook.com/groups/189797110788318/"
    return url

def save_to_csv(df, file_name):
    '''Save the dataframe to a CSV file'''
    df.to_csv(file_name, index=False)

def convert_to_timestamp(time_str):

    is_pm = '下午' in time_str

    time_str = time_str.replace('上午', '').replace('下午', '')

    dt = datetime.strptime(time_str, "%Y年%m月%d日%I:%M")
    
    hour = dt.hour
    if is_pm and hour != 12:
        hour += 12
    elif not is_pm and hour == 12:
        hour = 0

    dt = dt.replace(hour=hour)

    timestamp = int(time.mktime(dt.timetuple()))
    return timestamp

def get_comments_by_id(soup):

    comments = soup.find_all('div', id=lambda x: x and x.isdigit())
    
    if not comments:
        print("No comments found. HTML content:", soup.prettify()[:500])  # 印出部分HTML以便偵錯
        return [], []
    
    results = []
    comment_ids = []  # 新增一個用來儲存 ID 的列表


    for comment in comments:
        comment_id = comment.get('id')  # 獲取每個評論的唯一ID
        if comment_id:
            comment_ids.append(comment_id)
        author = comment.find('h3').find('a').text if comment.find('h3') else "Unknown Author"
        content_div = comment.find('div', {'class': lambda x: x and (len(x) == 2 or len(x) == 3)})
        
        if content_div:        
            content = content_div.text
            results.append({"author": author, "content": content})

    return results, comment_ids

def load_all_comments(driver, timeout=10, max_retries=3):
    all_comments = []
    seen_ids = set()  # 使用集合來存儲已處理過的留言內容


    while True:
        # 確保頁面完全載入
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # 獲取當前頁面的留言
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        comments, comment_ids = get_comments_by_id(soup)

        for comment, comment_id in zip(comments, comment_ids):
            if comment_id and comment_id not in seen_ids:  # 檢查ID是否已處理
                all_comments.append(comment)
                seen_ids.add(comment_id)

        retries = 0
        while retries < max_retries:
            try:

                # 等待"查看更多留言"按鈕出現
                see_more_div = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[id^='see_next_']"))
                )
                
                see_more_link = see_more_div.find_element(By.TAG_NAME, 'a').get_attribute("href")
                
                driver.get(see_more_link)

                time.sleep(2)
                print("click and look for more comment...")
                
                # 驗證新內容已載入

                new_html = driver.page_source
                new_soup = BeautifulSoup(new_html, 'html.parser')
                new_comments, new_comment_ids = get_comments_by_id(new_soup)
                if not new_comments:
                    print("No new comments loaded.")
                    break

                for comment, comment_id in zip(new_comments, new_comment_ids):
                    if comment_id and comment_id not in seen_ids:  # 檢查ID是否已處理
                        all_comments.append(comment)
                        seen_ids.add(comment_id)

                break
                
                
            except StaleElementReferenceException:
                retries += 1
                print("The element has expired. Retrying... ({retries}/{max_retries})")
                time.sleep(2) 
                
            except TimeoutException:
                print("Can not find more comment button")
                return all_comments
                
            except Exception as e:
                print(f"Click error: {str(e)}")
                retries += 1
                time.sleep(2)
                
        if retries >= max_retries:
            print(f"Max retrues. ({max_retries}), Stop load")
            break

        # 確認是否還有更多留言按鈕
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[id^='see_next_'] a"))
            )
        except TimeoutException:
            print("No more button.")
            break

    return all_comments
def get_filtered_links_with_info_profile_comment(driver, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script(
                "return document.readyState === 'complete' && !!document.querySelector('div[id]')"
            )
        )
        time.sleep(0.5)  

        article_author = None
        article_content = ""

        container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "m_story_permalink_view"))
            )

        try:
            author_element = container.find_element(By.XPATH, ".//header//h3//a | .//header//h3/strong/a")
            print()
            print(f"Author Element Preview: {author_element.text[:10]}...")
            print()
            article_author = author_element.text if author_element else "Unknown"
            
            print("article_author", article_author)

        except Exception as e:
            print(f"Error extracting article author: {str(e)}")
        
        try:
            
            content_elements = container.find_elements(
                By.XPATH, ".//header/following-sibling::*//div | .//header/following-sibling::*//p"
            )
            for element in content_elements:
                
                if element.text.strip():
                    article_content += element.text.strip() + "\n"
            
        except Exception as e:
            print(f"Error extracting article content: {str(e)}")
        
        post_time = None
        try:
            post_time = container.find_element(By.XPATH, ".//footer//abbr").text
        except Exception as e:
            print(f"Error extracting post time: {str(e)}")

        comments = load_all_comments(driver, timeout)

        return {
            "author": article_author,
            "content": article_content.strip(),
            "post_time": post_time,
            "comments": comments
        }

    except Exception as e:
        print(f"Error getting comments: {str(e)}")
        return {"author": None, "content": None, "comments": []}


def get_all_posts_links(driver):
    
    all_links = {}
    
    def get_current_page_links():
        try:
            stories_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "m_group_stories_container"))
            )
            posts = WebDriverWait(stories_container, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'article'))
            )
            
            for post in posts:
                try:
                    time_str = WebDriverWait(post, 5).until(
                        EC.presence_of_element_located((By.XPATH, ".//footer/div[1]//abbr"))
                    ).text.strip()

                    link = WebDriverWait(post, 5).until(
                        EC.presence_of_element_located((By.XPATH, ".//footer/div[2]//a"))
                    ).get_attribute('href')

                    timestamp = convert_to_timestamp(time_str)

                    all_links[timestamp] = link  # Store link with timestamp as key

                except Exception as e:
                    print(f"Error getting link: {e}")

            return stories_container
        
        except Exception as e:
            print(f"Error finding container: {e}")
            return None
    
    def find_next_page_link(container):

        next_page_exists = container.find_elements(By.XPATH, "./div[1]/a[1]")

        if not next_page_exists:
            
            return None
        try:
            next_page = WebDriverWait(container, 10).until(
                        EC.presence_of_element_located((By.XPATH, "./div[1]/a[1]"))
            )

            return next_page.get_attribute("href")
        except Exception as e:
            
            return None
    
    def save_progress():
        with open('links_progress.json', 'w', encoding='utf-8') as f:
            json.dump(all_links, f, ensure_ascii=False, indent=4)

    retry_count = 0
    max_retries = 3
    
    while True:
        try:

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "m_group_stories_container"))
            )
            
            container = get_current_page_links()

            if not container:
                    if retry_count < max_retries:
                        retry_count += 1
                        print(f" Retry {retry_count} ...")
                        time.sleep(2)
                        continue
                    break
            
            retry_count = 0  

            if len(all_links) % 10 == 0:
                save_progress()
            
            next_link = find_next_page_link(container)
            if not next_link:
                break
                
            print(f"Have collected {len(all_links)} links so far")
            
            driver.get(next_link)

            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
        except Exception as e:
            print(f"Process error: {e}")
            if retry_count < max_retries:
                retry_count += 1
                print(f"Retry {retry_count} ...")
                time.sleep(2)
                continue
            break
    
    save_progress()
    print(f"Total collect {len(all_links)} links")
    
    return all_links
    
