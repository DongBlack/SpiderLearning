from urllib import request
import re
import pymysql


'''
1.功能：武动乾坤文章爬取
2.urlopen请求网站，正则表达式匹配
3.请求头的设置，User-Agent
4.代理IP设置
5.数据库连接与写入
'''

class Sql(object):
    conn = pymysql.connect(host = '47.93.245.48', port = 3306,user='novel',passwd = 'zgp710913',db = 'novel',charset = 'utf8')
    def addnovel(self,chapter,chapter_url,content):
        cur = self.conn.cursor()
        cur.execute("insert into novel(Chapter,Chapter_url,Content) values(%s,%s,%s);", (chapter,chapter_url,content))
        self.conn.commit()




def getChapterList():
    url = 'https://www.12zw.com/1/1227/'
    req = request.Request(url,headers=headers)
    res = request.urlopen(req)
    html = res.read().decode('gbk')
    reg = r'<dd><a href="(.*?)">(.*?)</a></dd>'
    return re.findall(reg,html)

def getContent():
    temp = 0
    ip_list = [{"http": "39.102.39.56:8118"}, {"http": "47.93.245.48:8118"}]
    ip = ip_list[0]
    for i in chapter_list:
        try:
            temp +=1
            chapter_url = 'https://www.12zw.com/1/1227/' + i[0]
            chapter_req = request.Request(chapter_url,headers=headers)
            if temp%60 <=20:
                ip = 'localhost'
                chapter_res = request.urlopen(chapter_req)
            if temp%60>20 and temp%60<=40:
                ip = ip_list[0]
                handler = request.ProxyHandler(ip)
                opener = request.build_opener(handler)
                chapter_res = opener.open(chapter_req)
            if temp%60>40:
                ip = ip_list[1]
                handler = request.ProxyHandler(ip)
                opener = request.build_opener(handler)
                chapter_res = opener.open(chapter_req)
            # chapter_res = request.urlopen(chapter_req)
            chapter_html = chapter_res.read().decode('gbk')
            chapter_reg = r'<div id="content">(.*?)</div>'
            content = re.findall(chapter_reg,chapter_html)
            print('正在存储章节{},使用的ip：{}'.format(i[1],ip))
            mysql.addnovel(i[1],i[0],content)
        except:
            pass


        # return re.findall(chapter_reg,chapter_html)
mysql = Sql()
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36'
}

chapter_list = getChapterList()
getContent()
mysql.conn.close()



