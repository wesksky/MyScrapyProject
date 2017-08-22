import scrapy
from helloscrapy.items import DmozItem
import pymysql
import pymysql.cursors
from scrapy.spiders import CrawlSpider,Rule
import requests
# from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

class DmozSpide(scrapy.Spider):
    # 爬虫名
    name = "zh_login_test"
    # 合法域名
    allowed_domains = ["zhihu.com"]
    # url入口
    start_urls = [
        "https://www.zhihu.com/"
    ]

    # rules = (
    #     Rule(SgmlLinkExtractor(allow=('/question/\d*')),process_request="request_question"),
    # )

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
        "Connection": "keep-alive",
        "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        "Referer": "http://www.zhihu.com/",
        "X-Requested-With": "XMLHttpRequest",
        "Host": "www.zhihu.com",
        "Origin": "https://www.zhihu.com",
        "Referer": "https://www.zhihu.com/"
    }

    # 开始进入页面
    def start_requests(self):
        print("---------------------- start request ----------------------")
        yield scrapy.Request("https://www.zhihu.com/#signin",
                    headers = self.headers,
                    meta={"cookiejar":1},
                    callback=self.post_login)

    def post_login(self, response):
        print("---------------------- start login ----------------------")
        # 递交登陆表单
        xsrf = response.xpath('//div[@class="view view-signin"]/form/input[@name="_xsrf"]/@value').extract()[0]
        print("xsrf:" + xsrf)
        yield scrapy.FormRequest("https://www.zhihu.com/login/phone_num",
                                            meta={'cookiejar':response.meta['cookiejar']},
                                            headers = self.headers,
                                            formdata = {
                                                '_xsrf':xsrf,
                                                'password':'9112201',
                                                'captcha_type':'cn',
                                                'phone_num':'18768177619'},
                                            callback = self.after_login)

    def after_login(self, response):
        print("---------------------- after login ----------------------")
        # 登录成功后递归爬取页面 (这里是默认知乎返回的用户推荐question)
        for url in self.start_urls:
            print("start request:" + url)
            yield scrapy.Request(url, meta={'cookiejar':1}, headers = self.headers, callback=self.parse)

    def request_question(self,request):
        return scrapy.Request(request.url,meta={'cookiejar':1},headers = self.headers,callback=self.parse_question)

    def parse_question(self,response):
        sel = Selector(response)
        item = zhihuItem()
        item['qestionTitle'] = sel.xpath("//div[@id='zh-question-title']//h2/text()").extract_first()
        item['image_urls'] = sel.xpath("//img[@class='origin_image zh-lightbox-thumb lazy']/@data-original").extract()
        return item

    # 登陆后第一个
    def parse(self, response):
        print("---------------------- parse ----------------------")
        next_url = response.xpath("//div[@class='Card TopstoryItem']/div[@data-za-module='FeedItem']/div[@data-za-module='AdItem']/a/h2/@href").extract()
        for url in next_url:
            print("parse url:" + url)
            # yield scrapy.Request(response.urljoin(url), callback=self.parse_suburl)

    def parse_suburl(self, response):
        print("555")
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
    def insertOneUrl(self, title, url):
        # sql
        sql = "replace into huoying(title, url) values('%s', '%s')  " % (title, url)
        cur = self.connection.cursor()
        cur.execute(sql)

        self.connection.commit()
        self.connection.close()
