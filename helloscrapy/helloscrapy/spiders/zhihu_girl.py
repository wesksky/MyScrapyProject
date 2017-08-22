import scrapy
from helloscrapy.items import DmozItem
import pymysql
import pymysql.cursors

pymysql.install_as_MySQLdb()



class DmozSpide(scrapy.Spider):
    # 爬虫名
    name = "zhihu_girl"
    # 合法域名
    allowed_domains = ["www.zhihu.com"]
    # url入口
    start_urls = [
        "https://www.zhihu.com/collection/38624707"
    ]

    mId = 1

    def parse(self, response):
        titles = response.xpath("//div[@id='zh-list-collection-wrap']/div/h2[@class='zm-item-title']/a/text()").extract()
        new_urls = response.xpath("//div[@id='zh-list-collection-wrap']/div/h2[@class='zm-item-title']/a/@href").extract()

        helper = DBHelper()
        if titles:
            for i in range(len(titles)):
                # 插入
                helper.insertTitle(mId, titles[i], new_urls[i])
                mId += 1
                # 带参数递归
                request = scrapy.Request("https://www.zhihu.com/" + new_urls[i], callback=self.parse_detail)
                request.meta['id'] = mId
                yield request

        # for url in next_url:
        next_url = response.xpath("//div[@class='border-pager']/div[@class='zm-invite-pager']/span[last()]/a/@href").extract()
        if next_url:
            print("https://www.zhihu.com/collection/38624707" + next_url[0])
            yield scrapy.Request("https://www.zhihu.com/collection/38624707" + next_url[0], callback=self.parse)

    def parse_detail(self, response):
        # 取参
        title_id = response.meta['id']

        urls = response.xpath("//div[@class='downloadBox']/span/h1/text()").extract()[0]
        # 添加到数据库
        helper = DBHelper()
        helper.insertPics(title_id, urls)

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
    def insertPics(self, title_id, urls):
        # sql
        for url in urls:
            sql = "replace into zhihu_girl_pic(title_id, url) values(%s, %s)  "
            cur = self.connection.cursor()
            cur.execute(sql, (title_id, url))

        self.connection.commit()
        self.connection.close()

    def insertTitles(self, titles, urls):
        for i in range(len(titles)):
            sql = "replace into zhihu_girl_post(title, url) values(%s, %s) "
            cur = self.connection.cursor()
            cur.execute(sql, (titles[i], urls[i]))

        self.connection.commit()
        self.connection.close()

    def insertTitle(self, _id, title, url):
        sql = "replace into zhihu_girl_post(id, title, url) values(%s, %s, %s) "
        cur = self.connection.cursor()
        cur.execute(sql, (_id, title, url))

        self.connection.commit()
        self.connection.close()
