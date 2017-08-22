import scrapy
import pymysql
import pymysql.cursors
import urllib.parse

pymysql.install_as_MySQLdb()

class DmozSpide(scrapy.Spider):
    # 爬虫名
    name = "porn"
    # 合法域名
    allowed_domains = ["http://91.p9a.space/"]
    # url入口
    start_urls = [
        "http://91.p9a.space/forumdisplay.php?fid=21"
    ]

    def parse(self, response):
        next_url = response.xpath("//div[@class='pages_btns s_clear']/div[@class='pages']/a[@class='next']/@href").extract()
        detail_urls = response.xpath("//span[contains(@id, 'thread')]/a/@href").extract()

        # 解析详细页面
        for url in detail_urls:
            parse_u = self.allowed_domains[0] + url
            yield scrapy.Request(parse_u, callback=self.parse_detail, dont_filter=True)

        # 解析
        if next_url:
            yield scrapy.Request(urllib.parse.unquote(self.allowed_domains[0] + next_url[0]), callback=self.parse, dont_filter=True)

    def parse_detail(self, response):
        title = response.xpath("//h1/text()").extract()
        images = response.xpath("//img[contains(@id, 'aimg')]/@file").extract()
        filenames = response.xpath("//img[contains(@id, 'aimg')]/@alt").extract()

        # 添加到数据库
        helper = DBHelper()
        helper.insertPicUrl(self.allowed_domains[0], title[0], images, filenames)


    # def parse_suburl(self, response):
    #     title = response.xpath("//div[@class='downloadBox']/span/h1/text()").extract()[0]
    #     url = response.xpath("//div[@class='downloadBox']/span/h1/a/text()").extract()[0]
    #     # 添加到数据库
    #     helper = DBHelper()
    #     helper.insertOneUrl(title, url)


class DBHelper:

    def __init__(self):
        self.config = {
            'host' : '104.128.91.88',
            'port' : 3306,
            'user' : 'root',
            'passwd' : '911220',
            'db' : 'porn',
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
    def insertPicUrl(self, host, title, images, filenames):
        # sql
        self.connectDB()
        for i in range(len(images)):
            sql = "replace into bbs_91pron(url, title, url_type, filename) values(%s, %s, %s, %s)"
            print(host + images[i])
            cur = self.connection.cursor()
            cur.execute(sql, (host + images[i], title, "1", filenames[i]))

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
