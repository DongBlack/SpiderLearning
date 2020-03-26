from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from pyquery import PyQuery as pq
from pymongo import MongoClient


host = '47.93.245.48'
client = MongoClient(host,27017)
db = client.position
db.authenticate('DongBlack','zgp710913')
collection = db.position


options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-automation'])
browser = webdriver.Chrome(options=options)
wait = WebDriverWait(browser, 10)

def search():
    browser.get('https://www.lagou.com/hangzhou')
    input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#search_input"))
    )
    submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#search_button'))
    )
    input.send_keys('阿里')
    submit.click()
    pages = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#s_position_list > div.item_con_pager > div > span:nth-child(5)')))
    sleep(3)
    get_content()
    return pages.text

def next_page(page):
    try:
        next = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#s_position_list > div.item_con_pager > div > span.pager_next')))
        next.click()
        print('正在第{}页\n\n\n'.format(page))
        sleep(3)
        get_content()
    except TimeoutException:
        return next_page(page)

def  get_content():
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,'#s_position_list > ul > li.con_list_item.first_row.default_list')))
    html = browser.page_source
    doc = pq(html)
    items = doc('#s_position_list > ul')('li').items()
    for item in items:
        product = {
            'position': item('.position .p_top')('a').text().replace('\n',' '),
            'ability':item('.position .p_bot').text().replace('/','学历要求：')
        }
        save_to_mongo(product)


def save_to_mongo(product):
    db.position.insert(product)
    print(product)
    print('存储到mongodb\n')


def main():
    pages = int(search())
    for page in range(2,pages+1):
        next_page(page)


if __name__ == '__main__':
    main()