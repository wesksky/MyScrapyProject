import scrapy
from helloscrapy.items import DmozItem
import pymysql
import pymysql.cursors

pymysql.install_as_MySQLdb()

class DmozSpide(scrapy.Spider):
    # 爬虫名
    name = "huoying"
    # 合法域名
    allowed_domains = ["776dm.com"]
    # url入口
    start_urls = [
        "http://www.776dm.com/rexue/1463/"
    ]

    def parse(self, response):
        # self.idList = response.xpath("//div[@class='tb fix']/a[@rel='nofollow']/text()").extract()
        # self.titleList = response.xpath("//div[@class='tb fix']/a[@rel='nofollow']/@title").extract()
        # self.urlList = list()
        # helper = DBHelper()
        # helper.insertUrl(idList, titleList, urlList)

        next_url = response.xpath("//div[@class='tb fix']/a[@rel='nofollow']/@href").extract()
        for url in next_url:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_suburl)

    def parse_suburl(self, response):
        title = response.xpath("//div[@class='downloadBox']/span/h1/text()").extract()[0]
        url = response.xpath("//div[@class='downloadBox']/span/h1/a/text()").extract()[0]
        # 添加到数据库
        helper = DBHelper()
        helper.insertOneUrl(title, url)

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

    # 关闭数据库
    def closeDB(self):
        self.connection.close()

    # 检测是否需要绑定
    def insertUrl(self, urlid, title, url):
        # sql
        self.connectDB()
        for i in range(len(url)):
            sql = "replace into huoying values('%s', '%s', '%s')  " % (urlid[i], title[i], "http://www.776dm.com" + url[i])
            print("http://www.776dm.com" + url[i])
            cur = self.connection.cursor()
            cur.execute(sql)

        self.connection.commit()
        self.closeDB()

    # 检测是否需要绑定
    def insertOneUrl(self, title, url):
        # sql
        sql = "replace into huoying(title, url) values('%s', '%s')  " % (title, url)
        cur = self.connection.cursor()
        cur.execute(sql)

        self.connection.commit()
        self.connection.close()
