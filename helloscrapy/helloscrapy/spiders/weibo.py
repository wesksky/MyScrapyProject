import scrapy
from helloscrapy.items import DmozItem
import pymysql
import pymysql.cursors
import os
import requests

pymysql.install_as_MySQLdb()

class DoubanSpider(scrapy.Spider):
    # 爬虫名
    name = "weibo"
    # 合法域名
    allowed_domains = ["weibo.com/"]
    # url入口
    start_urls = [
        "http://weibo.com/"
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
        helper = DBHelper()
        articles = response.xpath("//div[@class='note-container']")
        for article in articles:
            url = article.xpath(".//a[@class='j a_unfolder_n']/@href").extract()[0]
            title = article.xpath(".//div[@class='note-header-container']/h3/a/@title").extract()[0]

            if url:
                # 去解析详细页面
                yield scrapy.Request(url, callback=self.parse_detail, dont_filter=True)

            if url and title:
                helper.insertOneUrl(title, url)


        next_url = response.xpath("//div[@class='paginator']/span[@class='next']/a/@href").extract()
        if next_url:
            yield scrapy.Request(next_url[0], callback=self.parse, dont_filter=True)

class DBHelper:

    def __init__(self):
        self.config = {
            'host' : '104.128.91.88',
            'port' : 3306,
            'user' : 'root',
            'passwd' : '911220',
            'db' : 'scrapy',
            'charset' : 'utf8',
            'cursorclass' : pymysql.cursors.DictCursor
        }
        self.connectDB()

    # 链接数据库，回头设计个连接池
    def connectDB(self):
        self.connection = pymysql.connect(**self.config)

    # 检测是否需要绑定
    def insertOneUrl(self, title, url):
        self.connectDB()
        # sql
        sql = "replace into douban(title, url) values('%s', '%s')  " % (title, url)
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
