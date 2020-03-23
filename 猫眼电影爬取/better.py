import json
import re
import requests
from requests.exceptions import RequestException
from threading import Thread
from queue import Queue

'''
改进：顺序多进程
'''
def get_one_page(url):
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0'
    }
    try:
        response = requests.get(url, headers = headers)
        if response.status_code == 200:
            return response.text
        return response.status_code
    except RequestException:
        return None


# 对网页进行解析
def parse_one_page(html):
    pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?title="(.*?)".*?data-src="(.*?)".*?star">(.*?)</p>'
                         '.*?releasetime">(.*?)</p>.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>', re.S)
    items = re.findall(pattern, html)
    for item in items:
        yield {
            'index': item[0],
            'title': item[1],
            'image': item[2],
            'actor': item[3].strip()[3:],
            'time': item[4].strip()[5:],
            'score': item[5]+item[6]
        }

class MyThread(Thread):
    def __init__(self, q):
        Thread.__init__(self)
        self.q = q

    def run(self):
        global index
        while not self.q.empty():
            data = self.q.get()
            print(data[0])
            html = get_one_page(data[1])
            print(html)
        # 如果当前标记比保存的小说章节序号大于1，阻塞
            while data[0] > index + 1:
                pass

            # 刚好大于1时，通过，保存章节
            if data[0] == index + 1:
                for item in parse_one_page(html):
                    print(item)
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
                index += 1




if __name__ == '__main__':
    index = -1
    url_list = []
    for i in range(0, 10):
        offset = i * 10
        url = 'https://maoyan.com/board/4?offset=' + str(offset)
        url_list.append(url)
    with open("results.txt", 'w', encoding='utf8') as f:
        q = Queue()
        for i,url in enumerate(url_list):
            q.put((i, url))


        ts = []
        for i in range(5):
            t = MyThread(q)
            t.start()
            ts.append(t)
        for t in ts:
            t.join()
