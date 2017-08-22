import scrapy
from helloscrapy.items import DmozItem
import pymysql
import pymysql.cursors
import os
import requests
from threading import Timer
import time

pymysql.install_as_MySQLdb()

class DoubanSpider(scrapy.Spider):
    # 爬虫名
    name = "58"
    # 合法域名
    allowed_domains = ["http://dy.58.com/"]
    # url入口
    start_urls = [
        "http://dy.58.com/dyxicheng/ershoufang/0/"
    ]

    def parse(self, response):
        # 下一页
        next_url = response.xpath("//a[@class='next']/@href").extract_first()
        if next_url:
            yield scrapy.Request(next_url, callback=self.parse, dont_filter=True)

        urls = response.xpath("//div[@class='list-info']/h2[@class='title']/a/@href").extract()
        if urls:
            for url in urls:
                yield scrapy.Request(url, callback=self.parse_detail, dont_filter=True)
                # time.sleep(60)

    def get_next_page(self, next_url):
        yield scrapy.Request(next_url, callback=self.parse, dont_filter=True)

    def parse_detail(self, response):

        print("-----------------parse_detail-----------------")
        # 查询各个信息
        url = response.url
        title = response.xpath("//div[@class='house-title']/h1/text()").extract_first()
        price_sum = response.xpath("//p[@class='house-basic-item1']/span[@class='price']/text()").extract_first() + response.xpath("//p[@class='house-basic-item1']/span[@class='price']/b/text()").extract_first()
        price_unit = response.xpath("//p[@class='house-basic-item1']/span[@class='unit']/text()").extract_first().replace(' ', '')
        floor = response.xpath("//div[@class='house-basic-item2']/p[@class='room']/span[@class='sub']/text()").extract_first()
        house_type = response.xpath("//div[@class='house-basic-item2']/p[@class='room']/span[@class='main']/text()").extract_first()
        decoration = response.xpath("//div[@class='house-basic-item2']/p[@class='area']/span[@class='sub']/text()").extract_first()
        area = response.xpath("//div[@class='house-basic-item2']/p[@class='area']/span[@class='main']/text()").extract_first()
        property_right = response.xpath("//div[@class='general-item general-situation']/div[@class='general-item-wrap']/ul[@class='general-item-right']/li[3]/span[@class='c_000']/text()").extract_first()
        build_time = response.xpath("//p[@class='toward']/span[@class='sub']/text()").extract_first()
        direction = response.xpath("//p[@class='toward']/span[@class='main']/text()").extract_first()
        garden_name = response.xpath("//h3[@class='xiaoqu-name']/a/text()").extract_first()
        telephone = response.xpath("//p[@class='phone-num']/text()").extract_first()
        username = response.xpath("//div[@class='side-left-wrap agent-info']/div[contains(@class, 'agent-name')]/a/text()").extract_first()
        user_type = response.xpath("//p[contains(@class, 'agent-belong')]/text()").extract_first().strip()
        # user_qr = response.xpath("//div[@id='wxChat']/p[@class='code']/img/@src").extract_first()
        # if user_qr:
        #     user_qr = user_qr.strip()
        # if not user_qr:
        #     user_qr = 'none'
        # print(
        #     "\nurl:" + url +
        #     "\ntitle:" + title +
        #     "\nprice_sum:" + price_sum +
        #     "\nprice_unit:" + price_unit +
        #     "\nfloor:" + floor +
        #     "\nhouse_type:" + house_type +
        #     "\ndecoration:" + decoration +
        #     "\narea:" + area +
        #     "\nproperty_right:" + property_right +
        #     "\nbuild_time:" + build_time +
        #     "\ndirection:" + direction +
        #     "\ngarden_name:" + garden_name +
        #     "\ntelephone:" + telephone +
        #     "\nusername:" + username +
        #     "\nuser_type:" + user_type
        # )

        helper = DBHelper()
        helper.deleteIfExist(url)
        helper.insertHouse(
        url,
        title,
        price_sum,
        price_unit,
        floor,
        house_type,
        decoration,
        area,
        property_right,
        build_time,
        direction,
        garden_name,
        telephone,
        username,
        user_type)

class DBHelper:

    def __init__(self):
        self.config = {
            'host' : '104.128.91.88',
            'port' : 3306,
            'user' : 'root',
            'passwd' : '911220',
            'db' : 'dy_house',
            'charset' : 'utf8',
            'cursorclass' : pymysql.cursors.DictCursor
        }
        self.connectDB()

    # 链接数据库，回头设计个连接池
    def connectDB(self):
        self.connection = pymysql.connect(**self.config)

    # 检测是否需要绑定
    def insertHouse(self,url,title,price_sum,price_unit,floor,house_type,decoration,area,property_right,build_time,direction,garden_name,telephone,username,user_type):
        self.connectDB()
        # sql
        sql = "insert into house(url,title,price_sum,price_unit,floor,house_type,decoration,area,property_right,build_time,direction,garden_name,telephone,username,user_type,location) values('%s', '%s','%s', '%s','%s', '%s','%s', '%s','%s', '%s','%s', '%s','%s', '%s', '%s', '%s')  " % (url,title,price_sum,price_unit,floor,house_type,decoration,area,property_right,build_time,direction,garden_name,telephone,username,user_type,"东营区 西城")
        cur = self.connection.cursor()
        cur.execute(sql)

        self.connection.commit()
        self.connection.close()

    def deleteIfExist(self, url):
        self.connectDB()
        sql = "select * from house where url=%s"
        cur = self.connection.cursor()
        cur.execute(sql, (url,))
        data = cur.fetchone()

        if data:
            self.connectDB()
            cur = self.connection.cursor()
            cur.execute("delete from house where url=%s", (url,))
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
