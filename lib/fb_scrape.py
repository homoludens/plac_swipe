from datetime import datetime
from selenium import webdriver, common
from selenium.webdriver.support.ui import WebDriverWait
# from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
# from selenium import webdriver
from bs4 import BeautifulSoup
import lxml
import logging
import sqlite3
from tkinter import messagebox
from urllib.parse import urlparse, urlunparse
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from groq_oglasi import groq_query, groq_format_response
from dotenv import load_dotenv
import os

# Replace with your OpenAI API key

load_dotenv('../.env')




logging.basicConfig(filename="newfile.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(console)

logger.debug('debug message')
logger.info('info message')
logger.warning('warn message')
logger.error('error message')
logger.critical('critical message')



def digits_only(input_string):
    return ''.join(filter(str.isdigit, input_string))

def recaptcha_modal_exists(driver):
    try:
        recaptcha = driver.find_element( By.ID, 'recaptcha-token')
    except common.exceptions.NoSuchElementException :
        print("no recatcha")
        # driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div/section/div/form/button").click()
    else:
        messagebox.showinfo(title='RECaptcha', message='Do REcaptcha, and then click OK.')


def clean_url(dirty_url):
    parsed_url = urlparse(dirty_url)
    output_url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        '',
        '', ''
    ))
    return output_url


def hover_element(driver, element):
    """
    Hover over time to force them to insert post link in dom. 
    """
    if isinstance(element, webdriver.remote.webelement.WebElement): 
        hover = ActionChains(driver).move_to_element(element)
        hover.perform()
        time.sleep(2)


def see_more_click(post):
    """
    If "see more" exist click on it to expand text.
    """
    try:
        see_more = post.find_element(By.XPATH, SEE_MORE)
        see_more.click()
    except Exception as e: 
        try:
            see_more = post.find_element(By.XPATH, SEE_MORE_2)
            see_more.click()
        except Exception as e: 
            # logger.info(e)
            logger.info('no see more')


def scroll_to_element(driver, element):

    try:
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()
    except Exception as e:
        logger.error(e)
        return False
    
    return True


MAX_POSTS = 100
# sqlite db
# cnx = sqlite3.connect('placevi_oglasi_FB14.sqlite')
cnx = sqlite3.connect('../data/placevi_oglasi.sqlite')

options = webdriver.ChromeOptions()
options.add_argument("--disable-notifications")
driver = webdriver.Chrome(options=options)

SCROLL_PAUSE_TIME = 7
output_list = []


fb_groups_links = [
    "https://www.facebook.com/groups/122209288328212/?sorting_setting=CHRONOLOGICAL_LISTINGS",
    "https://www.facebook.com/groups/262148338243718/?sorting_setting=CHRONOLOGICAL_LISTINGS",
    "https://www.facebook.com/groups/2536913206474787/?sorting_setting=CHRONOLOGICAL_LISTINGS",
    "https://www.facebook.com/groups/201505358849086/?sorting_setting=CHRONOLOGICAL_LISTINGS",
    "https://www.facebook.com/groups/853440135389904/?sorting_setting=CHRONOLOGICAL_LISTINGS",
    

    # trazi budzenje:
    # "https://www.facebook.com/groups/3423740061239331",
    # "https://www.facebook.com/groups/kuce.placevi.prodaja", 
    # "https://www.facebook.com/groups/3423740061239331", 

    # losi oglasi, uglavnom kola:
    # "https://www.facebook.com/groups/2564348517191038/?sorting_setting=CHRONOLOGICAL_LISTINGS",
    ]

driver.get(fb_groups_links[0])
username = os.getenv("FB_USERNAME")
password = os.getenv("FB_PASSWORD")

print(username)

time.sleep(2)
driver.find_element(By.CSS_SELECTOR, "[aria-label='Close']").click()

driver.find_element(By.NAME, "email").send_keys(username)
driver.find_element(By.NAME,  "pass").send_keys(password)

try:
    driver.find_element(By.CSS_SELECTOR, "[aria-label='Accessible login button']").click()
except:
    try:
        # driver.find_element(By.CSS_SELECTOR, "[aria-label='Log In']").click()
        driver.find_element(By.XPATH, '//*[@id="login_form"]/div[2]/div[3]/div/div').click()
    except:
        logger.error('no login')

time.sleep(3)

# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")

try:
    ad_link_df = pd.read_sql('select ad_link from facebook', cnx)
except pd.errors.DatabaseError:
    logger.warning('empty database')
    ad_link_df = pd.DataFrame([{
        "ad_link": ''
    }])


# html = driver.page_source
# soup = BeautifulSoup(html, 'html.parser')
# a = soup.select('div.html-div > span:nth-child(3) > span > a')
# for aa in a:
#     print(aa['href'])


time.sleep(60)


for fb_group_link in fb_groups_links:
    posts_elements = []
    output_list = []
    
    driver.get(fb_group_link)

    time.sleep(5)

    GROUP_TITLE_XPATH =  '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[1]/div[2]/div/div/div/div/div[1]/div/div/div/div/div/div[1]/h1/span/a'
    group_title = driver.find_element(By.XPATH, GROUP_TITLE_XPATH).text

    print(f"group: {group_title}, link:{fb_group_link}")
# //*[@id="mount_0_0_UV"]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[1]/div[2]/div/div/div/div/div[1]/div/div/div/div/div/div[1]/h1/span/a

    # POSTS_XPATH = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div[2]/div/div/div[1]/div[2]/div[2]/div[3]/div/div/div/div/div/div/div/div/div/div[13]/div/div'
    # POSTS_XPATH = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div[*]/div[2]/div/div[*]/div[1]/div[2]/div[2]/div[*]/div/div/div/div/div/div/div/div/div/div[13]/div'
    # POSTS_XPATH = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div[*]/div[2]/div/div[*]/div[1]/div[2]/div[2]/div[*]/div/div/div/div/div/div/div/div/div/div[13]/div'
    # POSTS_XPATH = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div[*]/div[*]/div/div[1]/div[2]/div[2]/div[*]/div[*]/div/div/div/div/div/div/div/div/div[13]/div'

    POSTS_XPATH = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div[2]/div[*]/div/div[1]/div[2]/div[2]/div[*]/div[*]/div/div/div/div/div/div/div/div/div[13]/div'
    POSTS_XPATH_2 = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div[*]/div[*]/div/div[1]/div[*]/div[2]/div[*]/div[*]/div/div/div/div/div/div/div/div/div/div[13]/div'


    # POSTS_XPATH = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div[*]/div[*]/div/div[1]/div[2]/div[2]/div[*]/div/div/div/div/div/div/div/div/div/div[13]/div'

# '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div[2]/div/div/div[1]/div[2]/div[2]/div[*]/div/div/div/div/div/div/div/div/div/div[13]/div'
# '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div[2]/div/div/div[1]/div[2]/div[2]/div[7]/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[3]/div[1]/div/div/span/div/div[5]/div
# '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div[2]/div/div/div[1]/div[2]/div[2]/div[9]/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[2]/div/div[2]/div/div[1]/span/h2/span/span/a'

    POST_TIME_HREF_XPATH =   "div/div[2]/div/div[2]/div/div[2]/span/div/span[1]/span/a"
    POST_TIME_HREF_XPATH_2 = "div/div[2]/div/div[2]/div/div[2]/span/div/span[3]/span/a"
                            #  "div/div[2]/div/div[2]/div/div[2]/span/div/span[1]/span/a"
    POST_TEXT_XPATH = 'div/div[3]/div[1]'
    # POST_TEXT_XPATH = 'div/div[3]/div[1]/div/div/div/span/div/div'
    POST_PRICE_XPATH = 'div/div[3]/div[2]/div[1]/div/a/div[1]/div/div[1]/span/span/span/div'
    POST_PRICE_XPATH = 'div/div[3]/div[*]/div[1]/div/a/div[1]/div/div[1]/span/span/span/div'
    POST_TITLE_XPATH = 'div/div[3]/div[*]/div[1]/div/a/div[1]/div/div[2]/span/span/div'
    # POST_AUTHOR_LINK = 'div/div[2]/div/div[2]/div/div[1]/span/h2/span/a'
    POST_AUTHOR_LINK = 'div/div[2]/div/div[2]/div/div[1]/span/h2/span/span/a'
    # POST_AUTHOR = 'div/div[2]/div/div[2]/div/div[1]/span/h2/strong/span'
    POST_AUTHOR = 'div/div[2]/div/div[2]/div/div[1]/span/h2/span/span/a'
    POST_IMAGE_URL = 'div/div[3]/div[3]/div[1]/div/div/div/div/div[*]/a/div[1]/div[1]/div/img'
    SEE_MORE =   'div/div[3]/div[1]/div/div/div/span/div[*]/div/div'
    # SEE_MORE_2 = 'div/div[3]/div[1]/div/div/div/span/div/div/div'
    # SEE_MORE =   'div/div[3]/div[1]/div/div/span/div/div[5]/div'
    SEE_MORE_2 = 'div/div[*]/div[*]/div/div/span/div/div[*]/div'

    post_elements_ids = []
    skipped_len = 0

    while len(output_list) + skipped_len < MAX_POSTS:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        
        posts_elements = driver.find_elements(By.XPATH, POSTS_XPATH)
        if len(posts_elements) < 1:
            posts_elements = driver.find_elements(By.XPATH, POSTS_XPATH_2)

        print(len(posts_elements))

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        print(f"last_height: {last_height}, new_height: {new_height}, ")

        

        for post in posts_elements:
            post_link = ''

            posts_elements = driver.find_elements(By.XPATH, POSTS_XPATH)
            if len(posts_elements) < 1:
                posts_elements = driver.find_elements(By.XPATH, POSTS_XPATH_2)

            if post not in posts_elements:
                continue
            
            if not scroll_to_element(driver, post):
                continue
            
            is_post_stale = expected_conditions.staleness_of(post)("")
            # try to avoid stale elements
            if (post.id not in post_elements_ids) and (not is_post_stale):
                
                time.sleep(2)
                
                # if author has tag "very responisve" or "top contributor" changes xpath
                try:
                    post_link = post.find_element(By.XPATH, POST_TIME_HREF_XPATH)
                    scroll_to_element(driver, post_link)
                    driver.execute_script("window.scrollBy(0,100)","")
                    post_date =  post_link.screenshot_as_base64
                except Exception as e:        
                    try:
                        post_link = post.find_element(By.XPATH, POST_TIME_HREF_XPATH_2)
                        scroll_to_element(driver, post_link)
                        driver.execute_script("window.scrollBy(0,100)","")
                        post_date =  post_link.screenshot_as_base64
                    except Exception as e:
                        post_link = '' 
                        post_date  = ''

                # //*[@id=":r1u:"]/span[1]/span/a
# //*[@id=":r1u:"]/span[1]/span/a/span/span/canvas
                try:
                    hover_element(driver, post_link)
                except Exception as e:
                    logger.error(f"hover_element: {e}")
                    continue

                try:
                    post_link = post.find_element(By.XPATH, POST_TIME_HREF_XPATH).get_attribute('href') 
                except Exception as e:        
                    try:
                        post_link = post.find_element(By.XPATH, POST_TIME_HREF_XPATH_2).get_attribute('href') 
                    except Exception as e:
                        logger.error(f"no post_link: post.id {e}")
                        continue
                        post_link = ''         
            
            post_link = clean_url(post_link)
            print(f"post_link: {post_link}")

            if len(output_list) < 1:
                output_list_temp = [{"ad_link": ''}]
            else:
                output_list_temp = output_list

            if (post_link != '') and (post_link not in ad_link_df.ad_link.to_list()) and (post_link not in pd.DataFrame(output_list_temp).ad_link.to_list()):
                see_more_click(post)
                
                try:
                    post_text = post.find_element(By.XPATH, POST_TEXT_XPATH).text
                except Exception as e:
                    logger.error(e)
                    # continue
                try:
                    post_price_full = post.find_element(By.XPATH, POST_PRICE_XPATH).text
                    post_price = digits_only(post_price_full)
                except Exception as e:
                    logger.error(e)
                    # continue

                try:
                    post_title = post.find_element(By.XPATH, POST_TITLE_XPATH).text
                except Exception as e:
                    logger.error(e)
                    # continue



                try:
                    post_author = post.find_element(By.XPATH, POST_AUTHOR_LINK).get_attribute('href')
                    post_author = clean_url(post_author)
                except NoSuchElementException as e:
                    try:
                        post_author = post.find_element(By.XPATH, POST_AUTHOR).text
                    except:
                        post_author = 'Anonymous member'

                # print(f'post autor: {post_author}')

                try:
                    post_images = post.find_elements(By.XPATH, POST_IMAGE_URL)
                
                    list_of_images = []
                    for image in post_images:
                        list_of_images.append(image.get_attribute('src'))

                except Exception as e:
                    list_of_images = []



                try:
                    groq_response = groq_query(f"{post_title} {post_text}") 
                    groq_response = groq_format_response(groq_response)
                except Exception as e:
                    logging.error(f" groq error {e}")
                    pass   

                post_elements_ids.append(post.id)
                output_list.append(
                            {
                                "ad_link": post_link, 
                                "ad_date": post_date,
                                "ad_full_title": post_title,
                                "ad_full_price": post_price,
                                "ad_full_description": post_text,
                                "ad_full_image": str(list_of_images),
                                "ad_user_page": post_author,
                                "llm_village": groq_response["village"],
                                "llm_driving_distance": groq_response["driving_distance"],
                                "llm_gps_coordinates": groq_response["gps_coordinates"],
                                "date": datetime.now(),
                            }
                        )
            else:
                skipped_len = skipped_len + 1
                logger.info('Post in database')
        
    output_df = pd.DataFrame(output_list)
    if not output_df.empty:
        output_df.to_csv(f'output_text_fb_{datetime.now()}.csv')
        output_df.to_sql(name='facebook', con=cnx, if_exists='append', index=False)

print("DONE!")

