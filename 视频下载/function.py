# -*- coding: UTF-8 -*-
import subprocess
from multiprocessing import Process
import requests
from bs4 import BeautifulSoup
import re
from pymongo import MongoClient
from threading import Thread


def get_urls(url, q):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    divs = soup.find_all('div', attrs={"class": "well well-sm"})[4:-3]
    for div in divs:
        a = div.a.prettify().split('\n')[0]
        href = '' + re.findall(r'"(.*?)"', a)[0]
        q.put(href)


def get_m3u8(href):
    response = requests.get(href)
    title = href.split("/")[-1]
    m3u8 = re.findall(r'<source src="(.*?)"', response.text)
    save_to_mongo({"_id": title, "href": href, "m3u8": m3u8[0], "flag": 0})
    print([title, m3u8])


def save_to_mongo(result):
    if collection.insert_one(result):
        print('存储到mongodb\n')


def get_ts(m3u8, q):
    response = requests.get(m3u8)
    ts_end = re.findall(',\\n(.*?.ts)\\n#', response.text)
    ts_head = re.findall(r'(.*?/bd/)', m3u8)[0]
    code = ts_end[0][:-6]
    for ts in ts_end:
        ts_num = (ts.replace(code, '')).zfill(len(str(len(ts_end))) + 3)
        q.put([ts_num, ts_head + ts])
    print('共有{}个ts文件将要下载'.format(len(ts_end)))


def download(ts_num, ts_url,pbar):
    with open(ts_num, 'ab') as filename:
        response = requests.get(ts_url)
        filename.write(response.content)
    filename.close()
    pbar.update(1)
    # print("{}已下载".format(ts_num))


def runcmd(command):
    '''
    :param command: 需要在cmd中执行的命令，对TS文件合并，移动
    :return: 命令执行结果
    '''
    ret = subprocess.run(command, shell=True, encoding="utf-8")
    if ret.returncode == 0:
        print("success:", ret)
    else:
        print("error:", ret)


class GetThread(Thread):
    def __init__(self, q):
        Thread.__init__(self)
        self.q = q

    def run(self):
        while not self.q.empty():
            href = self.q.get()
            get_m3u8(href)


class DownloadTread(Thread):
    def __init__(self, q,pbar):
        Thread.__init__(self)
        self.q = q
        self.pbar = pbar

    def run(self):
        while not self.q.empty():
            item = self.q.get()
            download(item[0], item[1],self.pbar)


class DownloadProcess(Process):  # 继承Process类
    def __init__(self, q):
        super(DownloadProcess,self).__init__()
        self.q = q

    def run(self):
        while not self.q.empty():
            item = self.q.get()
            download(item[0], item[1])


class GetProcess(Process):  # 继承Process类
    def __init__(self, q):
        super(GetProcess,self).__init__()
        self.q = q

    def run(self):
        while not self.q.empty():
            href = self.q.get()
            get_m3u8(href)


if __name__ == '__main__':
    host = '172.255.7.2'
    client = MongoClient(host, 27017)
    db = client.yzl138  # 连接系统默认数据库admin
    db.authenticate("admin", "password")
    collection = db.yzl138  # myset集合，同上解释
