from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re

import time

def scroll_and_click_button(driver, max_attempts=3, scroll_amount=1000, timeout=10):
    '''
    Scroll down and click the "All comments | Most relevant" button
    
    Parameters:
    - driver: WebDriver instance
    - max_attempts: Maximum number of scroll attempts
    - scroll_amount: Pixels to scroll each time
    - timeout: Maximum wait time for button in seconds
    '''
    
    BUTTON_SELECTOR = "div.x9f619.x1n2onr6.x1ja2u2z.x6s0dn4.x3nfvp2.xxymvpz"
    
    for attempt in range(max_attempts):
        try:
            print(f"Attempt {attempt + 1}: Looking for comments button...")
            
            # Try to find and click the button
            button = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, BUTTON_SELECTOR))
            )
            button.click()
            print("Successfully clicked comments button")
            return True
            
        except TimeoutException:
            print(f"Button not found on attempt {attempt + 1}, scrolling down...")
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            
            # If this was the last attempt, raise the exception
            if attempt == max_attempts - 1:
                print("Failed to find button after maximum attempts")
                return False
                
        except ElementClickInterceptedException:
            print("Button found but couldn't be clicked, trying to scroll into better position...")
            # Try to scroll element into better position
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return False

    return False
def click_view_more_btn(driver):
    '''Click the view more button to change the show style of comments of a post'''

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # Find the view more button
    view_more_btn = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'more comments')]")))
    view_more_btn.click()
    print("View more button clicked successfully.")
    return None

def click_showed_type_btn(driver, btn_name):
    '''Click the button to show the most relevant comments or all comments under a post by the argument btn_name'''

    try:
        # Scroll down to the button and click
        driver.execute_script("window.scrollTo(0, window.scrollY)")  # Scroll to the top

        # Find the button by its text
        most_relevant_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), '%s')]"%(btn_name))))
        most_relevant_button.click()
    except Exception as e:
        print("Can not click", btn_name)
        return False

def show_more_comments1(driver, time = 50):
    while True:
        try:
            click_view_more_btn(driver)
            time -= 1
            if time < 0:
                break
        except Exception as e:
            print("Out of contents")
            break

def show_more_comments(driver):
    '''Show more comments under a post'''

    # Limit the number of attempts to load more comments
    max_attempts = 10  # Adjust based on typical post length and your needs
    attempts = 0
    last_count = 0
    stable_attempts = 3  # Number of attempts with no new comments before considering end

    # Keep trying to load more comments until the limit is reached
    while attempts < max_attempts:
        try:
            click_view_more_btn(driver)
            time.sleep(2)  # Give some time for comments to load
            current_count = len(driver.find_elements(By.XPATH, "//div[contains(@class, 'x1n2onr6 x46jau6')]"))

            if current_count == last_count:
                stable_attempts -= 1
                if stable_attempts == 0:
                    print("No more comments to load.")
                    break
            else:
                last_count = current_count
                stable_attempts = 3  # Reset the stable_attempts counter

            attempts += 1
        except Exception as e:
            print("All comments loaded.")
            break

def show_all_replies(driver, threshold, ite):
    '''Show all replies of comments under a post
    Limited time: start - end = 3s => If there is no comment shown in 3s, stop
    Threshold: maximum number of comments'''
    arr = []
    cnt = 1
    while True:
        start = time.time() 
        if cnt > threshold: #Threshold
            break
        try:
            # Find replied comments
            all_replied_comments = driver.find_elements(By.XPATH, "//div[contains(@class, 'x1n2onr6 x46jau6')]")
        except:
            break
        
        # save count of comments to check if all comments are shown
        arr.append(len(all_replied_comments))
        if arr.count(max(arr)) >= ite:
            print("All replies are shown")
            return
        
        # Try to show sub-replied comments in replied-comments
        for comment in all_replied_comments:

            driver.execute_script("window.scrollBy(0, -50);")  # Scroll down 50px to load more comments
        
            try:
                view_more_buttons = WebDriverWait(comment, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'html-div xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x78zum5 x1iyjqo2 x21xpn4 x1n2onr6')]")))
                view_more_buttons.click()
                sub_cmt = comment.find_elements(By.XPATH, "//div[contains(@class, 'x1n2onr6 x1swvt13 x1iorvi4 x78zum5 x1q0g3np x1a2a7pz')]")
                for sub_cmt in comment:
                    try:
                        view_more_sub_buttons = WebDriverWait(sub_cmt, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'html-div xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x78zum5 x1iyjqo2 x21xpn4 x1n2onr6')]")))
                        view_more_sub_buttons.click()
                        #cnt += 1
                    except:
                        break

                cnt += 1

            except Exception as e:
                break

            finally:
                end = time.time()
                if end - start > 3:
                    #print("Finally")
                    return

def filter_spam(text):
    '''Filter spam comments based on user-defined keywords'''

    spam_text = ['http', 'miễn phí', '100%', 'kèo bóng', 'khóa học', 'netflix', 'Net Flix', 'shopee', 'lazada']
    for spam in spam_text:
        if spam in text.lower():
            return True
    return False

def get_comments(driver, limit_text=2500):
    '''Get comments under a post and filter spam comments
    Return:  - dataframe of comments: id, text, is_spam, tag_name.
             - number of comments'''
    cnt = 0
    treasured_comments = []
    is_spam = 0
    comments = driver.find_elements(By.XPATH, "//div[contains(@class, 'x1n2onr6 x1swvt13 x1iorvi4 x78zum5 x1q0g3np x1a2a7pz') or contains(@class, 'x1n2onr6 xurb0ha x1iorvi4 x78zum5 x1q0g3np x1a2a7pz')]")
    for comment in comments:
        try:
            # Check if comment contains text
            text_ele = comment.find_element(By.XPATH, ".//div[contains(@class, 'xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs')]")
            username = comment.find_element(By.XPATH, ".//span[@class='x3nfvp2']/span")

            if text_ele:
                try:
                    name_tag = text_ele.find_element(By.XPATH, ".//span[@class='xt0psk2']/span")
                    name_tag = name_tag.text
                except:
                    name_tag = None

                # Limit the number of comments  
                cnt += 1
                if cnt > limit_text:
                    break
                text = text_ele.text
                if cnt % 10 == 0:
                    print("Count: ", cnt)

                # Filter spam comments    
                if filter_spam(text):
                    is_spam = 1
                else:
                    is_spam = 0
                treasured_comments.append({
                    "id" : cnt,
                    "username": username.text,
                    "text": text,
                    'tag_name': name_tag,
                    'is_spam': is_spam
                })
        except Exception as e:
            continue
    print("Crawl successfully!!! \nTotal Comments: ", cnt)
    return treasured_comments, cnt

def get_url():
    '''Get the URL of a Facebook post from the user input'''
    #get url from input
    # url = input("Enter the URL: ")
    url = "https://mbasic.facebook.com/groups/189797110788318/"
    return url


def save_to_csv(df, file_name):
    '''Save the dataframe to a CSV file'''
    df.to_csv(file_name, index=False)

def get_filtered_links_with_info(driver):
    '''
    get match data
    '''
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    links_info = []
    pattern = r'https://mbasic\.facebook\.com/groups/.*'
    
    for element in soup.find_all('a', href=True):
        href = element['href']
        if href.startswith('/'):
            href = f"https://mbasic.facebook.com{href}"
            
        if re.match(pattern, href):
            # create dic
            link_data = {
                'url': href,
                'text': element.get_text(strip=True),  # text
                'parent_element': str(element.parent.name),  # father
                'classes': element.get('class', []),  # CSS 
                'id': element.get('id', '')  # elementID
            }
            links_info.append(link_data)
    
    # remove duplicate
    seen_urls = set()
    unique_links_info = []
    for item in links_info:
        if item['url'] not in seen_urls:
            seen_urls.add(item['url'])
            unique_links_info.append(item)
    
    return unique_links_info

def get_comments_by_id(soup):

    comments = soup.find_all('div', id=lambda x: x and x.isdigit())
    
    if not comments:
        print("No comments found. HTML content:", soup.prettify()[:500])  # 印出部分HTML以便偵錯
        return []
    
    results = []

    for comment in comments:
        author = comment.find('h3').find('a').text if comment.find('h3') else "Unknown Author"
        content_div = comment.find('div', {'class': lambda x: x and (len(x) == 2 or len(x) == 3)})
        if content_div:        
            content = content_div.text
            results.append({"author": author, "content": content})
            
    return results

def load_all_comments(driver, timeout=10):
    all_comments = []

    while True:
        
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        comments = get_comments_by_id(soup)
        all_comments.extend(comments)
        
        try:

            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div[id^='see_next_'] a"))
            )
            element.click()
            print("點擊查看更多留言...")            

            time.sleep(2)
            
        except TimeoutException:
            print("沒有更多的『查看更多留言』按鈕，留言加載完成。")
            break
        except Exception as e:
            print(f"發生錯誤: {str(e)}")
            break

    return all_comments

def get_filtered_links_with_info_profile_comment(driver, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete", message='website does not ready.'
        )
        time.sleep(2)  
 
        all_comments = load_all_comments(driver, timeout)

        return all_comments  # 返回所有留言的清單

    except TimeoutException:
        print("Timeout waiting for comments to load")
        return []
    except Exception as e:
        print(f"Error getting comments: {str(e)}")
        return []

def get_all_posts_links(driver):
    
    all_links = {}
    
    def get_current_page_links():
        try:
            stories_container = driver.find_element(By.ID, "m_group_stories_container")
            posts = stories_container.find_elements(By.TAG_NAME, 'article')
            
            for post in posts:
                try:
                    time_str = post.find_element(By.XPATH, ".//footer/div[1]//abbr").text.strip()
                    link = post.find_element(By.XPATH, ".//footer/div[2]//a").get_attribute('href')
                    
                    all_links[time_str] = link  # Store link with timestamp as key

                except Exception as e:
                    print(f"無法獲取文章連結: {e}")

            return stories_container
        except Exception as e:
            print(f"無法找到 stories container: {e}")
            return None
    
    def find_next_page_link(container):

        next_page_exists = container.find_elements(By.XPATH, "./div[1]/a[1]")

        if not next_page_exists:
            print("已到達最後一頁")
            return None
        try:
            next_page = WebDriverWait(container, 10).until(
                        EC.presence_of_element_located((By.XPATH, "./div[1]/a[1]"))
            )

            return next_page.get_attribute("href")
        except Exception as e:
            print(f"無法獲取下一頁連結: {e}")
            return None
    
    while True:

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "m_group_stories_container"))
        )
        
        container = get_current_page_links()
        if not container:
            break
            
        next_link = find_next_page_link(container)
        if not next_link:
            break
            
        print(f"目前已收集 {len(all_links)} 個連結")
        print(f"準備進入下一頁: {next_link}")
        
        try:
            driver.get(next_link)
        
            time.sleep(2)
        except Exception as e:
            print(f"無法進入下一頁: {e}")
            break
    
    return all_links
    
