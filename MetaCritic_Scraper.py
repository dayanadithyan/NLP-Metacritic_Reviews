#!/usr/bin/env python
# coding: utf-8

# ## MetaCritic Scraper

# In[112]:


# import standard libs

import numpy as np
import pandas as pd
from sys import exit
import time
import re
import random

# import scraping libs

from selenium import webdriver
from bs4 import BeautifulSoup
import urllib.parse
from lxml import html
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium import webdriver 
# from selenium_move_cursor.MouseActions import move_to_element_chrome


# ## Section 1: Sub-routines

# ### Navigation

# In[ ]:


#Setting up Selenium Webdriver

def find_driver()

    chrome_path = input(r"Enter path to your chrome driver ... Example: 'C:\Users\Dayans\Desktop\Other\chromedriver.exe' without quotes")

    driver = webdriver.Chrome(chrome_path)


# In[114]:


def load_website():
    
    
    ## get user input for url to scrape
    
    url = input("Enter the MetaCritic page you wish to scrape:")
    
    driver.get(url)
    

    ## driver.get('https://www.metacritic.com/game/pc/dota-2/user-reviews?sort-by=date&num_items=100')

    
    ## display product name
    
    product_title = driver.find_element_by_css_selector('div[class="product_title"]').text
    
    print(f'Site loaded for product : {product_title}')
    
    
    ## sleep to ensure page is loaded correctly
    
    time.sleep(5)
    


# In[116]:


def click_next():
    
    driver.find_element_by_css_selector('span[class="flipper next"]').click()
    


# ### Data extraction

# In[ ]:


def get_page_source():
   
    source = driver.page_source
    
    return BeautifulSoup(source, "html.parser")


# In[118]:


def make_soup():
    
    soup = get_page_source()
    page = driver.page_source
    tree = html.fromstring(page)
    
    return soup,page,tree


# In[119]:


def extract_reviews_from_page(soup):
    
    '''
    BeautifulSoup for extracting elements 
    '''
    
    main_list = []
    
    review_cards = soup.find_all("div", attrs={"class":'review_content'})
    
    for review in review_cards:
        
        temp_list = []
        
        date = review.find("div", attrs={"class": "date"}).text
        
        rating = review.find("div", attrs={"class": "review_grade"}).text
        
        review = review.find("div", attrs={"class": "review_body"}).text
        
        try:
            user = review.find("div", attrs={"class": "name"}).text
                
        except:
            user = 'Anonymous'
        
        temp_list.append(user)
        temp_list.append(date)
        temp_list.append(rating)
        temp_list.append(review)
        
        main_list.append(temp_list)
        
    return main_list
        
 


# In[ ]:


def get_no_pages():
    
    '''
    Gets the numbers of pages for the product to figure out pagination range
    '''
    
    product_title = driver.find_element_by_css_selector('div[class="product_title"]').text
    
    number_of_pages = driver.find_element_by_css_selector('li[class="page last_page"]').text
    
    number_of_pages = re.findall(r'\d+',number_of_pages)
    
    page_count = int(number_of_pages[0])
    
    num_reviews = 100 * page_count
    
    print(f"{product_title} has {page_count} pages of reviews. \nThat's approximately {num_reviews} reviews!")
    
    return page_count


# ## Section 2: Main scraping function

# In[122]:


def main_scraper():
    
    '''
    Scrapes each page using BS4 and paginates till end
    '''

    load_website()

    reviews = []

    page_count = get_no_pages()

    current_page = 0

    for i in range(page_count):

        get_page_source()

        soup,page,tree = make_soup()

        reviews_in_page = extract_reviews_from_page(soup)

        reviews.append(reviews_in_page)

        current_page += 1

        print(f'Page {current_page} complete. Moving onto next page ...')

        click_next()
        
    return reviews
    
    


# In[ ]:


def product_name():
    
    product_name = driver.find_element_by_css_selector('div[class="product_title"]').text
    
    return product_name


# #### Begin

# In[123]:


find_driver()

product = product_name()

all_reviews = main_scraper()


# In[ ]:


## close driver
driver.close()


# ## Section 3: Data cleaning and storage

# In[137]:


final_list = []

for page_of_reviews in all_reviews:
    for review in page_of_reviews:
        final_list.append(review)
        


# In[142]:


print(f"{len(final_list)} reviews collected in total ... Time to clean and save ...")


# In[190]:


def make_dataframe():
    
    df = pd.DataFrame(final_list)
    
    df.columns = ['user', 'date', 'rating', 'review']
    
    return df
    


# In[191]:


df = make_dataframe()


# In[193]:


def clean_ratings():
    
    print('Cleaning ratings ...')

    ls = []

    ls2 = []

    for index, row in df.iterrows():
        ls.append(row['rating'])

    for rating in ls:
        final_numerical_rating = re.findall(r'\d+',rating)
        ls2.append(int(final_numerical_rating[0]))

    df['rating'] = ls2


# In[201]:


def clean_review():
    
    print('Cleaning reviews ...')
    
    ls = []
    
    ls2 = []
    
    for index, row in df.iterrows():
        ls.append(row['review'])
        
    for review in ls:
        
        clean_review = review.replace('\n', '')
        ls2.append(clean_review)
                   
    df['review'] = ls2
    


# In[204]:


clean_ratings()


# In[202]:


clean_review()


# In[205]:


df.head()


# In[ ]:


## drop all foreign language reviews


# In[209]:


def is_english(string):
    
    '''
    Determine if string is English or not
    '''
    
    try:
        string.encode(encoding='utf-8').decode('ascii')
        
    except UnicodeDecodeError:
        return False
    
    else:
        return True


# In[222]:


def remove_foreign_langs():
    
    '''
    Iterates through dataframe to drop all non-English rows
    '''
    
    print('Removing all non-English reviews ...')

   
    for index,row in df.iterrows():

        test = is_english(row['review'])

        if test == False:

            df.drop(index, inplace=True)

        else:
            pass
        
    print(f'{len(final_list) - len(df)} rows removed ... {len(df)} rows remain ...')
    


# In[223]:


remove_foreign_langs()


# In[224]:


df.head()


# In[ ]:


### save to csv 


# In[ ]:


def save_file_and_exit():
    
    df.to_csv(f'MetacriticReviews_{product}.csv')
    
    print('File saved ... Now exiting ...')
    
    exit()
    


# In[ ]:


save_file_and_exit()


# ### END

# In[225]:


# df.to_csv('MetacriticReviews_DOTA2.csv')

