import requests
from lxml import etree
from threading import Thread
from queue import Queue
from urllib import request
import re
import warnings

warnings.filterwarnings("ignore")



"""
1.SSL异常的处理
2.Xpath匹配，requests请求
3.写入TXT文件
4.多线程有序爬取
"""
class MyThread(Thread):
    def __init__(self, q):
        Thread.__init__(self)
        self.q = q

    def run(self):
        global index
        while not self.q.empty():
            data = self.q.get()
            url = root1 + ''.join(data[1])
            response = requests.get(url, headers=headers,verify=False)
            page = etree.HTML(response.content)

            chapter = page.xpath("//h1/text()")
            chapter = ''.join(chapter)
            print("爬取 -> %s" % chapter, index)

            content = page.xpath("//div[@id='content']/text()")
            content = '\n'.join(content)
            content = content.replace("\xa0\xa0\xa0\xa0", "")

            # 如果当前标记比保存的小说章节序号大于1，阻塞
            while data[0] > index + 1:
                pass

            # 刚好大于1时，通过，保存章节
            if data[0] == index + 1:
                print("保存 -> %s" % chapter, index)
                f.write('\n' + chapter + '\n')
                f.write(content)
                index += 1


if __name__ == '__main__':
    root = "https://www.bqg3.com/1_1330/"
    root1 = "https://www.bqg3.com/"
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36'
    }

    index = -1  # 章节标记，表示保存的章数

    response = requests.get(root, headers=headers)
    page = etree.HTML(response.content)
    title = ''.join(page.xpath("//h1/text()"))  # 小说名
    req = request.Request(root, headers=headers)
    res = request.urlopen(req)
    html = res.read().decode('gbk')
    reg = r'<dd><a href="(.*?)">.*?</a></dd>'
    hrefs = re.findall(reg, html)

    with open("%s.txt" % title, 'w', encoding='utf8') as f:
        f.write(title)  # 先写入小说名
        q = Queue()
        # print(hrefs)
        for i, href in enumerate(hrefs):
            q.put((i, href))

        ts = []
        for i in range(5):
            t = MyThread(q)
            t.start()
            ts.append(t)
        for t in ts:
            t.join()