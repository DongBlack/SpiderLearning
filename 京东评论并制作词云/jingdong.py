import requests
import re
import json
import jieba
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from wordcloud import WordCloud

WC_MASK_IMG = 'gdock.jpg'
# 评论数据保存文件
COMMENT_FILE_PATH = 'comment.txt'
# 词云字体
WC_FONT_PATH = 'C:\Windows\Fonts\STHUPO.TTF'


def get_page(offset):
    url = 'https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98&productId=26215878181&score=0&sortType=5&page='+offset+'&pageSize=10&isShadowSku=0&fold=1'
    headers = {
        'authority': 'search.jd.com',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36',
        'sec-fetch-dest': 'document',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'referer': 'https://search.jd.com/Search?keyword=%E5%8F%8C%E5%8F%A3%E5%8D%83%E5%85%86%E7%BD%91%E5%8D%A1%E6%8B%86%E6%9C%BA&enc=utf-8&wq=%E5%8F%8C%E5%8F%A3%E5%8D%83%E5%85%86%E7%BD%91%E5%8D%A1%E6%8B%86ji&pvid=6ca8471695a84e37be4981f7dc6674f2',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cookie': 'shshshfpa=8ee9fb4c-3a29-449f-08b3-0aa3ee044707-1584700365; shshshfpb=fdKgwQy8doLa2HcmYXIemgg%3D%3D; __jdv=76161171|baidu|-|organic|%25E4%25BA%25AC%25E4%25B8%259C|1585184706713; __jdu=1584700362869439543573; areaId=6; ipLoc-djd=6-379-390-0; PCSYCityID=CN_140000_141000_141023; xtest=9885.cf6b6759; __jda=122270672.1584700362869439543573.1584700362.1584700362.1585184707.2; __jdc=122270672; shshshfp=e72e21c32e4b6f36d4fad054a686a289; 3AB9D23F7A4B3C9B=BK55QH3RLYARWQPFUUTYF4LXZ6XMQD2ZF6BYU7MUVYTGT7B6QYMEOKF42DRUGZEH5KSYQJ7ELXHY2JM6OZV4LG4TVY; qrsc=3; rkv=V0100; __jdb=122270672.5.1584700362869439543573|2.1585184707; shshshsID=216acda9f70cec5e0963d575c6fb28c5_5_1585184799621',
    }
    try:
        html = requests.get(url,headers = headers)
        if html.status_code == 200:
            return html.text
        else:
            print('请求异常')
            return html.status_code
    except:
        return None

def parse_page(html):
    reg = re.compile('fetchJSON_comment98\((.*?)\);',re.S)
    comment = re.search(reg,html)
    if comment:
        comment = json.loads(comment.group(1))
        comment = comment['comments']
        for item in comment:
            write_to_txt(item['content'])

def write_to_txt(content):
    with open('comment.txt','a', encoding='gbk') as f:
        f.write(content+'\n')
        f.close()

def cut_word():
    """
    对数据分词
    :return: 分词后的数据
    """
    with open(COMMENT_FILE_PATH) as file:
        comment_txt = file.read()
        wordlist = jieba.cut(comment_txt, cut_all=True)
        wl = " ".join(wordlist)
        print(wl)
        return wl


def create_word_cloud():
    """
    生成词云
    :return:
    """
    # 设置词云形状图片
    wc_mask = np.array(Image.open(WC_MASK_IMG))
    # 设置词云的一些配置，如：字体，背景色，词云形状，大小
    wc = WordCloud(background_color="white", max_words=2000, mask=wc_mask, scale=4,
                   max_font_size=50, random_state=42, font_path=WC_FONT_PATH)
    # 生成词云
    wc.generate(cut_word())

    # 在只设置mask的情况下,你将会得到一个拥有图片形状的词云
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.figure()
    plt.show()


def main():
    for offset in range(11):
        html = get_page(str(offset))
        parse_page(html)
    create_word_cloud()


if __name__ == '__main__':
    main()