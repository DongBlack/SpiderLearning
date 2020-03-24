import os
import re
from hashlib import md5
from urllib.parse import urlencode
import json
from pymongo import MongoClient
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import requests
from multiprocessing import Pool


host = '47.93.245.48'
client = MongoClient(host, 27017,connect=False)
db = client.thread    # 连接系统默认数据库admin
db.authenticate("DongBlack", "zgp710913")
collection = db.jiepai   # myset集合，同上解释

def get_page(url,ip):
    headers = {
        'authority': 'www.toutiao.com',
        'accept': 'application/json, text/javascript',
        'sec-fetch-dest': 'empty',
        'x-requested-with': 'XMLHttpRequest',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'referer': 'https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cookie': 'tt_webid=6807560240521135629; s_v_web_id=verify_k85583ox_6Pb8H4y4_1LmQ_4Zai_9xv3_5YJr5YCAyHz4; WEATHER_CITY=%E5%8C%97%E4%BA%AC; tt_webid=6807560240521135629; ttcid=2c899b9bec3d42e5bd6711f8bf3d6be129; csrftoken=6c021b4d51f851cee9a9eaca7a5390fb; SLARDAR_WEB_ID=c250266a-ba10-4623-bebf-38a332d11957; __tasessionId=fpkn3xbq51585013644772; tt_scid=J3FoyeBs2l.xc6DEuMrPW.fU8iptWvak-2ghqoiLkyAhL9My4uxuX814bTzkBkXk9cb2',
    }
    response = requests.get(url,headers = headers,proxies = ip)
    try:
        if response.status_code == 200:
            return response
        else:
            return response.status_code
    except RequestException:
        print('请求索引页出错')
        return None
def make_url(offset):
    params = (
        ('aid', '24'),
        ('app_name', 'web_search'),
        ('offset', offset*20),
        ('format', 'json'),
        ('keyword', '\u8857\u62CD'),
        ('autoload', 'true'),
        ('count', '20'),
        ('en_qc', '1'),
        ('cur_tab', '1'),
        ('from', 'search_tab'),
        ('pd', 'synthesis'),
        ('timestamp', '1585013743795')
    )
    url = 'https://www.toutiao.com/api/search/content/?' + urlencode(params)
    return url

def parse_page(html):
    data = json.loads(html)
    if data and 'data' in data.keys():
        for item in data.get('data'):
            yield item.get('article_url')

def detail_page(detail_url):
    detail_html = get_page(detail_url,ip).text
    if detail_html:
        soup = BeautifulSoup(detail_html,'lxml')
        try:
            title = soup.select('title')[0].get_text()
            print(title)
            print('ip为：{}'.format(ip))
        except:
            return None
        images_pattern = r'gallery: JSON.parse\((.*?)\),'
        result = re.findall(images_pattern,detail_html)
        if result:
            # print(result)
            data = json.loads(result[0])
            data = json.loads(data)
            if data and 'sub_images' in data.keys():
                sub_images = data.get('sub_images')
                count = data.get('count')
                images = [item.get('url') for item in sub_images]
                # for i in range(len(images)):
                #     download_images(i,images[i],title)
                return {
                    'title': title,
                    'url':detail_url,
                    'count':count,
                    'images': images
                }
        else:
            html = detail_html.encode('utf-8').decode("unicode-escape")
            reg = r'content:(.*?)slice'
            result2 = re.findall(reg, html)
            if result2:
                reg2 = r'<img src.*?&quot;(.*?)\\&quot; img_width'
                if reg2:
                    images = re.findall(reg2, result2[0])
                    # for i in range(len(images)):
                    #     download_images(i,images[i],title)
                        # save_to_mongo(image)
                    return {
                        'title': title,
                        'url': detail_url,
                        'count': len(images),
                        'images':images
                    }

def save_to_mongo(result):
    if db.jiepai.insert(result):
        print('存储到mongodb\n')
        return True
    return False

def download_images(i,url,title):
    content = get_page(url,ip).content
    file_path = '{}'.format(title) + '{}'.format(i) + '.png'
    if not os.path.exists(file_path):
        with open(file_path,'wb') as f:
            f.write(content)
            f.close()

def main(offset):
    ask = 0
    global ip
    ip = ''
    url = make_url(offset)
    try:
        html = get_page(url,ip).text
        for detail_url in parse_page(html):
            try:
                if ask%20 <10:
                    ip = ''
                elif ask%20 >15:
                    ip = {"http": "39.102.39.56:8118"}
                else:
                    ip =  {"http": "47.93.245.48:8118"}
                if detail_url :
                    result = detail_page(detail_url)
                    if result:
                        save_to_mongo(result)
                        ask+=1
            except:
                pass
    except:
        pass
if __name__ == '__main__':
    group = [x for x in range(9)]
    pool = Pool()
    pool.map(main,group)