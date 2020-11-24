# -*- coding: UTF-8 -*-
from function import *
from multiprocessing import Queue

def m3u8_to_mongo(collection):
    q = Queue()
    for page in range(1, 11):
        print('正在获取第{}页url'.format(page))
        url = 'http://www.yzl138.com/videos?page=' + str(page)
        get_urls(url, q)
    print('将爬取{}条数据'.format(q.qsize()))
    ts = []
    for i in range(8):
        t = GetThread(q)
        t.start()
        ts.append(t)
    for t in ts:
        t.join()


def m3u8_from_mongo():
    query = {"flag": 0}
    mydoc = collection.find_one(query)
    return mydoc


def video_download(index):
    for video in range(index):
        q = Queue()
        mydoc = m3u8_from_mongo()
        title = mydoc['_id']
        m3u8 = mydoc['m3u8']
        print('开始下载:《{}》'.format(title))
        get_ts(m3u8, q)
        process_list = []
        for i in range(5):
            p = DownloadProcess(q)
            p.start()
            process_list.append(p)
        for p in process_list:
            p.join()
        runcmd(["copy", "/b", "*.ts", title + ".mp4"])
        runcmd(["move", title + ".mp4", "D:\视频\Ysl138.com"])
        runcmd(["del", "/q", "*.ts"])
        print('《{}》下载完毕'.format(title))
        collection.update_one({'_id':title},{ "$set": { "flag": 1} })

if __name__ == '__main__':
    host = '172.255.7.2'
    client = MongoClient(host, 27017)
    db = client.yzl138  # 连接系统默认数据库admin
    db.authenticate("admin", "password")
    collection = db.yzl138  # myset集合，同上解释
    video_download(1)

