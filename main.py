from seleniumwire import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as BS
import pandas as pd
from pandas import json_normalize
import fake_useragent
import time
import requests as rq
from urllib.parse import quote


def get_user_agent():
    '''
    формирует рандомные юзер агенты
    '''
    return fake_useragent.UserAgent().random


def do_search(driver, search_text_encode, page_num):
    '''
    поиск в строке поиска
    '''
    '''
    search_element = driver.find_element(
        By.ID, 
        'searchInput')
    search_element.clear()
    search_element.send_keys(text_search)
    search_element.send_keys(Keys.RETURN)
    '''
    url = 'https://www.wildberries.ru/catalog/0/search.aspx?page='+str(page_num)+'&sort=popular&search='+search_text_encode
    driver.get(url=url)
    time.sleep(5)
    

    

def get_json(url_search, search_text_encode, page_num, user_agent, proxy):
    '''
    получение списка скю в формате json через api
    '''
    headers = {
       
       'accept': '*/*',
       'accept-language': 'ru',
       'origin': 'https://www.wildberries.ru',
       'priority': 'u=1, i',
       'referer': 'https://www.wildberries.ru/catalog/0/search.aspx?page='+str(page_num)+'&sort=popular&search='+search_text_encode,
       'sec-ch-ua': 'Not(A:Brand";v="99", "Microsoft Edge";v="133", "Chromium";v="133',
       'sec-ch-ua-mobile': '?0',
       'sec-ch-ua-platform': 'Windows',
       'sec-fetch-dest': 'empty',
       'sec-fetch-mode': 'cors',
       'sec-fetch-site': 'cross-site',
       'user-agent': user_agent
    }


    response = rq.get(url=url_search, headers=headers, proxies=proxy)
    return response.json()


def prepare_items(response):
    '''
    подготовка данных из json
    return список со словарями
    '''
    products = []
    products_raw = response.get('products', None)
    
    if products_raw !=None and len(products_raw)>0:
        for product in products_raw:
            products.append({
                'brand': product.get('brand', None),
                'name': product.get('name', None),
                'feedbacks': product.get('feedbacks', None),
                'nmFeedbacks': product.get('nmFeedbacks', None),
                'id': product.get('id', None),
                'rating': product.get('rating', None),
                'reviewRating': product.get('reviewRating', None),
                'root': product.get('root', None),
                'optionId': product.get('sizes', None)[0].get('optionId', None),
                'basic': float(product.get('sizes', None)[0].get('price', None).get('basic', None)/100),
                'product': float(product.get('sizes', None)[0].get('price', None).get('product', None)/100)

            })

    return products


def scroll_website(count_of_scroll, driver):
    '''
    прокурутка веб страницы
    '''
    last_height = driver.execute_script("return document.body.scrollHeight")

    for _ in range(count_of_scroll):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def button_reviews_this_item(driver):
    '''
    Нажать на кнопку Этот вариант товара на листе с отзывами
    '''
    search_div = driver.find_elements(By.CLASS_NAME, 'product-feedbacks__title')
    max_index=len(search_div)
    search_div[max_index-1].click()


def get_review(driver, url_review, count_of_scroll, id):
    '''
    парсинг комментариев
    '''
    data_rev=[]

    driver.get(url_review)
    time.sleep(10)

    button_reviews_this_item(driver)
    
    scroll_website(count_of_scroll, driver)
    
    #поиск в html блока с комментариями
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        main_div_main = body.find_element(By.TAG_NAME, "main")
        main_container = main_div_main.find_element(By.ID, "mainContainer")
        main_container_p1 = main_container.find_element(By.ID, "appReactRoot")
        section_review = main_container_p1.find_element(By.TAG_NAME, "section")
        main_review_div = section_review.find_element(By.CLASS_NAME, "product-feedbacks__main")
        user_review_part = main_review_div.find_element(By.CLASS_NAME, "user-activity__tab-content")
        comment_list = user_review_part.find_element(By.TAG_NAME, "ul")
    except:
        data_rev = None
        return data_rev

    #все комментарии
    html = comment_list.get_attribute('innerHTML')
    soup = BS(html, 'html.parser') 
    all_li = soup.find_all('li', attrs={"itemprop":"review"})

    #парсинг комментариев
    for rev in all_li:
        
        review_head = rev.find('div', class_="feedback__top-wrap").find('div', class_='feedback__info')
        
        try:
            author_name = review_head.find('div', class_="feedback__info-header").find("p").text
        except AttributeError:
            author_name = None

        try:
            sales_status = review_head.find('div', class_="feedback__info-header").find('ul').text
        except:
            sales_status = None

        try:
            date_review = review_head.find('div', class_="feedback__wrap hide-mobile").find('div', class_='feedback__date').text
        except AttributeError:
            date_review = None
        
        try:
            review_rating = review_head.find('div', class_="feedback__wrap hide-mobile").find('div', class_='feedback__rating-wrap').find('span', class_='feedback__rating')['class']
            review_rating=review_rating[2]
        except AttributeError:
            review_rating = None

        try:                                                                     
            review_content = rev.find('div', class_="feedback__content").text
        except AttributeError:
            review_content = None
        
        data_rev.append([author_name, sales_status, date_review, review_rating, review_content, id])

    return data_rev
        

    
    
    

def list_sku(search_text,count_of_page,proxy):
    '''
    основаная функция для получения списка скю
    '''

    #окно EDGE
    user_agent = get_user_agent()
    options = webdriver.EdgeOptions()
    options.add_argument(f"user-agent={user_agent}")
    
    driver = webdriver.Edge(options=options)
    driver.maximize_window()


    products = []

    
    search_text_encode = quote(search_text)
    

    for page_num in range(1,count_of_page+1):

        
        #поиск товаров
        do_search(driver, search_text_encode, page_num) 

        #поиск api со списком товаров
        for request in driver.requests:
            
            a = request.url.find("search.wb.ru")
            b = request.url.find("page")
            if request.response and a!=-1 and b!=-1:
                url_search = request.url
                
        #получить из api список товаров
        response = get_json(url_search, search_text_encode, page_num, user_agent, proxy)
        products += prepare_items(response)
        
        

    #сохранить
    pd.DataFrame(products).to_csv('C:/Users/Oktyabrina/Desktop/webscraper/data/product.csv', index=False)

    

def list_review(count_of_scroll):
    '''
    Основная функция для получения комменатриев
    '''
    #окно EDGE
    user_agent = get_user_agent()
    options = webdriver.EdgeOptions()
    options.add_argument(f"user-agent={user_agent}")
    options.add_experimental_option("detach", True)
    driver = webdriver.Edge(options=options)
    driver.maximize_window()

    #список скю из csv
    df = pd.read_csv('C:/Users/Oktyabrina/Desktop/webscraper/data/product.csv')

    #получить комментарии
    data_rev = [[]]
    for num_row in range(df.shape[0]):
        url_review = 'https://www.wildberries.ru/catalog/'+str(df['id'].iloc[num_row])+'/feedbacks?imtId='+str(df['root'].iloc[num_row])+'&size='+str(df['id'].iloc[num_row])
        res = get_review(driver, url_review,count_of_scroll, df['id'].iloc[num_row])
        if res!=None: data_rev.extend(res)
        #time.sleep(5)

    #датафрейм комментариев
    df_review = pd.DataFrame(data=data_rev, columns=['Автор','Статус заказа', 'Дата отзыва', 'Кол-во звезд', 'Текст отзыва', 'Артикул'] )
    
    pd.DataFrame(df_review).to_csv('C:/Users/Oktyabrina/Desktop/webscraper/data/review.csv', index=False)

    

if __name__ == '__main__':
    search_text='свечи ароматические'
    count_of_scroll = 1000
    count_of_page = 2

    login = 'user307032'
    password = '64ialz'
    address = '46.174.199.236'
    port = '3195'

    proxy = {
        'http': f'http://{login}:{password}@{address}:{port}',
        'https': f'http://{login}:{password}@{address}:{port}',
    }


    list_sku(search_text,count_of_page,proxy)
    #list_review(count_of_scroll)
