
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
from urllib.parse import urlparse
from pprint import pprint

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
    url = "https://mbasic.facebook.com/groups/189797110788318/permalink/246400928461269/?rdid=BBmI8i684TUenNTT&share_url=https%3A%2F%2Fmbasic.facebook.com%2Fshare%2Fp%2FEQzShvUwvpDxmcsc%2F&_rdr"
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
        print("\nelement\n",element)
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
            print(f"Author: {author}, Content: {content}")

    return results

def get_filtered_links_with_info_profile_comment(driver, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete", message='website does not ready.'
        )
        time.sleep(2)  

        html_content = driver.page_source

        soup = BeautifulSoup(html_content, 'html.parser')

        get_comments_by_id(soup)
    except TimeoutException:
        print("Timeout waiting for comments to load")
        return []
    except Exception as e:
        print(f"Error getting comments: {str(e)}")
        return []
    # # # 抓取 m_story_permalink_view 內的主要內容
    # story_div = soup.find('div', id="m_story_permalink_view")

    # if story_div:
    #         # 你可以進一步處理找到的內容
    #         # 例如：提取文字內容
    #         text_content = story_div.find('div', class_="bv").get_text()
    #         # 提取作者資訊
    #         author = story_div.find('h3', class_="br bs bt bu").get_text()
            
    #         print("Content:", text_content)
    #         print("Author:", author)
    # else:
    #     print("找不到目標元素")
    # # 定義一個空的字典來存放提取的資訊
    # story_info = {}

    # # 提取發佈者名稱
    # user_name_tag = story_div.find('a', href=True)
    # story_info['user_name'] = user_name_tag.get_text(strip=True) if user_name_tag else "N/A"

    # # 提取發佈內容
    # content_tag = story_div.find('div', class_='bv')
    # story_info['content'] = content_tag.get_text(strip=True) if content_tag else "N/A"

    # # 提取發佈時間
    # time_tag = story_div.find('abbr')
    # story_info['time'] = time_tag.get_text(strip=True) if time_tag else "N/A"

    # # 提取社團名稱或頁面標題
    # group_tag = story_div.find('h3', class_='br')
    # story_info['group_name'] = group_tag.get_text(strip=True) if group_tag else "N/A"

    # # 提取讚數
    # likes_tag = story_div.find('div', class_='db')
    # story_info['likes'] = likes_tag.get_text(strip=True) if likes_tag else "N/A"

    # # 提取留言
    # comments = []
    # for comment_div in story_div.find_all('div', class_='dd'):
    #     comment_data = {}
    #     # 抓取留言者名稱
    #     commenter_tag = comment_div.find('a', href=True)
    #     comment_data['commenter'] = commenter_tag.get_text(strip=True) if commenter_tag else "N/A"
        
    #     # 抓取留言內容
    #     comment_content_tag = comment_div.find('div', class_='dx')
    #     comment_data['comment'] = comment_content_tag.get_text(strip=True) if comment_content_tag else "N/A"
        
    #     # 抓取留言時間
    #     comment_time_tag = comment_div.find('abbr')
    #     comment_data['comment_time'] = comment_time_tag.get_text(strip=True) if comment_time_tag else "N/A"
        
    #     comments.append(comment_data)

    # story_info['comments'] = comments

    # # 顯示提取的資訊
    # print("發佈者:", story_info['user_name'])
    # print("內容:", story_info['content'])
    # print("發佈時間:", story_info['time'])
    # print("社團或頁面名稱:", story_info['group_name'])
    # print("讚數:", story_info['likes'])
    # print("\n留言:")
    # for comment in story_info['comments']:
    #     print("留言者:", comment['commenter'])
    #     print("留言內容:", comment['comment'])
    #     print("留言時間:", comment['comment_time'])
    #     print("-----------")


