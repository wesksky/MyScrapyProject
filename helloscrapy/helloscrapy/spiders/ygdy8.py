import scrapy
import pymysql
import pymysql.cursors
import os
import requests
import urljoin from urlparse

pymysql.install_as_MySQLdb()

class DoubanSpider(scrapy.Spider):
    # 爬虫名
    name = "ygdy8_moives"
    # 合法域名
    allowed_domains = ["http://www.ygdy8.net/"]
    # url入口
    start_urls = [
        "http://www.ygdy8.net/html/gndy/china/index.html",
        "http://www.ygdy8.net/html/gndy/oumei/index.html"
    ]

    def __init__(self):
        self._HOST = "http://www.ygdy8.net"

    def parse(self, response):
        # 下一页
        next_url = response.xpath("//a[text()='下一页']/@href").extract_first()

        if next_url:
            yield scrapy.Request(urljoin(response.url, next_url), callback=self.parse, dont_filter=True)

        urls = response.xpath("//b/a[last()]/@href").extract()
        for url in urls:
            yield scrapy.Request(self._HOST + url, callback=self.parse_detail, dont_filter=True)

    def parse_detail(self, response):
        urls = response.xpath("//tbody/tr/td/a/@href").extract()
        movie_name = response.xpath("//div[@class='bd3r']/div[@class='co_area2']/div[@class='title_all']/h1/font/text()").extract_first()
        if urls:
            for url in urls:
                helper = DBHelper()
                helper.insertOneMovie(url, movie_name)

class DBHelper:
    def __init__(self):
        self.config = {
            'host' : '104.128.91.88',
            'port' : 3306,
            'user' : 'root',
            'passwd' : '911220',
            'db' : 'my_movies',
            'charset' : 'utf8',
            'cursorclass' : pymysql.cursors.DictCursor
        }
        self.connectDB()

    # 链接数据库，回头设计个连接池
    def connectDB(self):
        self.connection = pymysql.connect(**self.config)

    def insertOneMovie(self, url, movie_name):
        self.connectDB()
        file_name = url.split('/')[-1]

        # sql
        sql = "insert into movies(url, movie_name, file_name) values(%s, %s, %s)"
        cur = self.connection.cursor()
        cur.execute(sql, (url, movie_name, file_name))

        self.connection.commit()
        self.connection.close()
