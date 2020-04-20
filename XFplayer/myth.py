import requests
from bs4 import BeautifulSoup
import re


def getUrlList(page):
    url = 'http://www.pilizy.com/meishaonv/index-{}.html'.format(page)
    response = requests.get(url)
    html = response.content.decode('utf-8')
    bs = BeautifulSoup(html,"html.parser")
    td = bs.find('td')
    tbody = td.find_all('tbody')[1]
    trlist = tbody.find_all('tr')
    urllist = []
    for tr in trlist:
        if tr.find('a'):
            url = 'http://www.pilizy.com' + tr.find('a').get('href')
            urllist.append(url)
    print(urllist)
    return urllist

def detail(url):
    response = requests.get(url)
    html = response.content.decode('utf-8')
    reg = r'.*?《(.*?)》.*?'
    title = re.findall(reg,html)
    if title:
        title = title[0]
    reg2 = r'target="_blank">(.*?)</a></li>'
    xplayer = re.findall(reg2,html)[1:]
    return title,xplayer


def write(xplayer):
    with open("city.txt" , 'a+', encoding='utf8') as f:
        f.write(xplayer)
        f.write("\n")
        f.close()

if __name__ == '__main__':
    for page in range(15,16):
        print("接下来打印第{}页的url".format(page))
        urllist = getUrlList(page)
        print("进行第{}页的爬取".format(page))
        for url in urllist:
            try:
                title,xplayer = detail(url)
                print("{}正写入".format(title))
                if type(xplayer) ==list:
                    for temp in xplayer:
                        write(temp)
                else:
                    write(xplayer)
            except:
                pass