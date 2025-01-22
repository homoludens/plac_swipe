from selenium import webdriver, common
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
from selenium import webdriver
from bs4 import BeautifulSoup
import lxml
import logging
import sqlite3
from tkinter import messagebox
from datetime import datetime
from groq_oglasi import groq_query, groq_format_response
from dotenv import load_dotenv
import os

# Replace with your OpenAI API key

load_dotenv('../')


def digits_only(input_string):
    return ''.join(filter(str.isdigit, input_string))


def recaptcha_modal_exists(driver):

    MODAL_RECAPTCHA = "/html/body/div[2]/div/div/aside/div[1]"

    try:
        # recaptcha = driver.find_element( By.ID, 'recaptcha-token')
        recaptcha = driver.find_element( By.XPATH,MODAL_RECAPTCHA)
    except common.exceptions.NoSuchElementException :
        print("no recatcha")
        # driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div/section/div/form/button").click()
    else:
        messagebox.showinfo(title='RECaptcha', message='Do REcaptcha, and then click OK.')



# sqlite db
# cnx = sqlite3.connect('placevi_oglasi_KPtest8.sqlite')
cnx = sqlite3.connect('../data/placevi_oglasi.sqlite')

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)


# login to KP.com

# KP credentials

username = os.getenv("KP_USERNAME")
password = os.getenv("KP_PASSWORD")


driver.get("https://kupujemprodajem.com/login")
driver.find_element(By.ID, "email").send_keys(username)
driver.find_element(By.ID,  "password").send_keys(password)
time.sleep(3)




try:
    hcaptcha = driver.find_element( By.XPATH, '//*[@id="__next"]/div/div[2]/div/section/div/form/div[3]')
except common.exceptions.NoSuchElementException :
    print("no hcatcha")
    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div/section/div/form/button").click()
else:
    messagebox.showinfo(title='Captcha', message='Do captcha, and then click OK.')

# html = driver.page_source
# soup = BeautifulSoup(html, 'html.parser')
# a = soup.select('div.html-div > span:nth-child(3) > span > a')
# for aa in a:
#     print(aa['href'])

# search_link = "https://kupujemprodajem.com/pretraga?categoryId=26&groupId=232&priceFrom=6000&priceTo=16000&currency=eur"
# search_link = "https://kupujemprodajem.com/pretraga?categoryId=26&groupId=737&priceTo=26000&currency=eur"
search_links = [
    # "https://kupujemprodajem.com/nekretnine-kupoprodaja/seoska-domacinstva/pretraga?categoryId=26&groupId=737&priceFrom=23000&priceTo=24000&currency=eur&hasPrice=yes",
    "https://kupujemprodajem.com/pretraga?categoryId=26&groupId=737&priceTo=46000&currency=eur",
    "https://kupujemprodajem.com/pretraga?categoryId=26&groupId=231&priceTo=46000&currency=eur",
    "https://kupujemprodajem.com/pretraga?categoryId=26&groupId=230&priceTo=46000&currency=eur"
]

for search_link in search_links:
    recaptcha_modal_exists(driver)
    driver.get(search_link)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # find number of pages
    div = soup.select_one(".Pagination_numbers__9OjwH > div:nth-last-child(2)")

    last_page_element = soup.select_one(".Pagination_numbers__9OjwH > div:nth-last-child(1) > a:nth-child(1)")
    try:
        last_page = int(last_page_element.text)
    except:
        last_page = 1

    # if last_page:
    #     last_page = int(last_page_element.text)
    # else:
    #     last_page = 1

    logging.info(last_page)

    output_list = []

    try:
        ad_link_df = pd.read_sql('select ad_link from kupujem_prodajem', cnx)
    except pd.errors.DatabaseError:
        logging.warning('empty database')
        ad_link_df = pd.DataFrame([{
            "ad_link": ''
        }])

    # get all pages
    for page in range(1, last_page + 1):
        recaptcha_modal_exists(driver)
        print("Skeniram stranu " + str(page) + "/" + str(last_page))

        paged_link = search_link + "&page=" + str(page)

        time.sleep(5)
        driver.get(paged_link)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # ads = soup.select(".AdItem_price__SkT1P")

        ads = soup.select(".AdItem_adHolder__CWcMj")
        
        recaptcha_modal_exists(driver)

        for ad in ads:
            recaptcha_modal_exists(driver)
            ad_full_image = ''
            ad_user_page = ''
            ad_full_title = ''
            ad_full_price = ''
            ad_full_description = ''

            
            # print(ad)
            ad_link = 'https://kupujemprodajem.com' + ad.select_one('.AdItem_adInfoHolder__FYK1b').select_one('a').attrs['href']
            if ad_link not in ad_link_df.ad_link.to_list():
                ad_title = ad.select_one('.AdItem_adInfoHolder__FYK1b').select_one('a').text
                ad_short_description = ad.select_one('.AdItem_adInfoHolder__FYK1b').select_one('p').text
                ad_price = ad.select_one('.AdItem_price__SkT1P').text

                recaptcha_modal_exists(driver)
                driver.get(ad_link)

                time.sleep(10)

                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                
                try:
                    ad_full_title = soup.select_one(".AdViewInfo_name__VIhrl").text
                    ad_full_price = soup.select_one(".AdViewInfo_price__J_NcC").text
                    ad_full_price = digits_only(ad_full_price)
                    ad_full_description = soup.select_one(".AdViewDescription_descriptionHolder__kOWyx").text
                    ad_date = soup.select_one(".AdViewInfoStats_infoStat__018hF:nth-child(3)").text
                except Exception as e:
                    logging.error(e)
                
                try:
                    ad_full_image_elements =  soup.select(".GallerySlideItem_imageGalleryImage__UlbIb")
                    ad_full_image = []
                    
                    for image in ad_full_image_elements: 
                        ad_full_image.append(image.attrs['src'])
                    
                    ad_full_image = str(ad_full_image)

                except Exception as e:
                    logging.error("error ad_full_image")
                    ad_full_image = ''
                
                try:
                    ad_user_page = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[3]/div/div/div[2]/section[1]/div[2]/section[2]/div/div[3]/a").get_attribute('href')
                except Exception as e:
                    logging.error("error ad_user_page")

                # try:
                #     recaptcha = driver.find_element( By.ID, 'recaptcha-token')
                # except common.exceptions.NoSuchElementException :
                #     print("no recatcha")
                #     # driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div/section/div/form/button").click()
                # else:
                #     messagebox.showinfo(title='RECaptcha', message='Do REcaptcha, and then click OK.')
                recaptcha_modal_exists(driver)
                ad_phone_number = ''
                try:
                    PHONE_XPATH = "/html/body/div[1]/div/div[3]/div/div/div[2]/section[1]/div[2]/section[2]/div/div[3]/div/button/div[1]/span"
                    click_for_phone = driver.find_element(By.XPATH, PHONE_XPATH)
                    recaptcha_modal_exists(driver)
                    click_for_phone.click()
                except Exception as e:
                    logging.error("error click_for_phone")
                else:
                    ad_phone_number = driver.find_element(By.XPATH, PHONE_XPATH).text

                try:
                    groq_response = groq_query(f"{ad_full_title} {ad_full_description}") 
                    groq_response = groq_format_response(groq_response)
                except Exception as e:
                    logging.error(f" groq error {e}")
                    pass   
                
                output_list.append(
                    {
                        "ad_link": ad_link, 
                        "ad_date": ad_date,
                        "ad_full_title": ad_full_title,
                        "ad_full_price": ad_full_price,
                        "ad_full_description": ad_full_description + ' ' + ad_phone_number,
                        "ad_full_image": ad_full_image,
                        "ad_user_page": ad_user_page,
                        "llm_village": groq_response["village"],
                        "llm_driving_distance": groq_response["driving_distance"],
                        "llm_gps_coordinates": groq_response["gps_coordinates"],
                        "date": datetime.now(),
                    }
                )
            else:
                logging.info('add exists in database')


    output_df = pd.DataFrame(output_list)
    if not output_df.empty:
        output_df.to_csv('output_text.csv')
        output_df.to_sql(name='kupujem_prodajem', con=cnx, if_exists='append', index=False)
