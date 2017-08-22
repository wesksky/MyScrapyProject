import scrapy
from helloscrapy.items import DmozItem
import pymysql
import pymysql.cursors
import os
import requests
import urllib

pymysql.install_as_MySQLdb()

class DoubanSpider(scrapy.Spider):
    # 爬虫名
    name = "proxy"
    # 合法域名
    allowed_domains = ["douban.com"]
    # url入口
    start_urls = [
        "http://www.xicidaili.com/nn/"
    ]

    def parse_detail(self, response):
        pics = response.xpath("//div[@class='image-wrapper']/img/@src").extract()
        helper = DBHelper()
        for url in pics:
            filename = os.path.basename(url)
            self.download(url, filename)
            helper.insertOnePic(url)

    def download(self, url, filename):
        mfile = requests.get(url, timeout=10)
        fp = open('pictures/' + filename, 'wb')
        fp.write(mfile.content)
        fp.close()

    def parse(self, response):
        l = []
        helper = DBHelper()
        proxys = response.xpath("//tr[@class='odd']")
        if proxys:
            for p in proxys:
                ip = p.xpath("./td[2]/text()").extract_first()
                port = p.xpath("./td[3]/text()").extract_first()
                print(ip + ":" + port)
                # usage = self.test_proxy(ip + ":" + port)
                # if usage:
                #     helper = DBHelper()
                #     helper.insertIp(ip + ":" + port)

        next_url = response.xpath("//a[@class='next_page']/@href").extract_first()
        if next_url:
            yield scrapy.Request("http://www.xicidaili.com" + next_url, callback=self.parse, dont_filter=True)

    def url_user_agent(self,proxy,url):
        proxy_support = urllib.request.ProxyHandler({'http':proxy})
        opener = urllib.request.build_opener(proxy_support)
        urllib.request.install_opener(opener)
        i_headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.48'}
        req = urllib.request.Request(url,headers=i_headers)
        html = urllib.request.urlopen(req,timeout=2)
        if url == html.geturl():
            doc = html.read()
            return doc
        return

    def test_proxy(self, ip):
        url = 'http://dy.58.com'
        try:
            doc = self.url_user_agent(ip ,url)
            return True
        except Exception as e:
            return False

class DBHelper:

    def __init__(self):
        self.config = {
            'host' : '104.128.91.88',
            'port' : 3306,
            'user' : 'root',
            'passwd' : '911220',
            'db' : 'my_proxy',
            'charset' : 'utf8',
            'cursorclass' : pymysql.cursors.DictCursor
        }
        self.connectDB()

    # 链接数据库，回头设计个连接池
    def connectDB(self):
        self.connection = pymysql.connect(**self.config)

    # 检测是否需要绑定
    def insertIp(self, ip):
        self.connectDB()
        # sql
        sql = "insert into my_proxy(ip) values('%s')  " % (ip,)
        cur = self.connection.cursor()
        cur.execute(sql)

        self.connection.commit()
        self.connection.close()

    def insertOnePic(self, picurl):
        self.connectDB()
        # sql
        sql = "replace into douban_pic(url) values('%s')  " % (picurl)
        cur = self.connection.cursor()
        cur.execute(sql)

        self.connection.commit()
        self.connection.close()
