import scrapy
from helloscrapy.items import DmozItem
from scrapy.spiders import CrawlSpider,Rule
from helloscrapy.items import TumblrUserInfoItem
import requests

from helloscrapy.Dao.TumblrUser import TumblrUserHelper
from helloscrapy.Dao.TumblrPic import TumblrPicHelper

# from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

TUMBLR_HOST = "https://www.tumblr.com"

class DmozSpide(scrapy.Spider):
    # 爬虫名
    name = "tumblr"
    # 合法域名
    allowed_domains = ["tumblr.com"]
    # url入口
    start_urls = [
        "https://www.tumblr.com/dashboard"
    ]

    # 伪造headers
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
        "Connection": "keep-alive",
        "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
    }

    # 开始进入页面
    def start_requests(self):
        print("---------------------- start request ----------------------")
        yield scrapy.Request("https://www.tumblr.com/login",
                    headers = self.headers,
                    meta={"cookiejar":1},
                    callback=self.post_login)

    def post_login(self, response):
        print("---------------------- start login ----------------------")
        # 递交登陆表单
        form_key = response.xpath("//meta[@id='tumblr_form_key']/@content").extract()[0]
        print("xsrf:" + form_key)
        yield scrapy.FormRequest("https://www.tumblr.com/login",
                                            meta={'cookiejar':response.meta['cookiejar'],'dont_redirect': True,"handle_httpstatus_list": [302]},
                                            headers = self.headers,
                                            formdata = {
                                                'determine_email':'601814590@qq.com',
                                                'user[email]':'601814590@qq.com',
                                                'user[password]':'wesksky0712',
                                                'context':'login',
                                                'version':'STANDARD',
                                                'http_referer':'https://www.tumblr.com/logout',
                                                'form_key':form_key,
                                                'seen_suggestion':'0',
                                                'used_suggestion':'0',
                                                'used_auto_suggestion':'0',
                                                'random_username_suggestions':'["SweetFuryCollector","JollyStudentDeer","TooWolfCollector","ImpossibleDefendorCollection","LoudlySwagBouquet"]'},
                                            callback = self.after_login)

    # 登陆结束后执行该方法
    def after_login(self, response):
        print("---------------------- after login ----------------------")
        # 爬取关注用户
        print("after login parse url:" + TUMBLR_HOST + "/following")
        yield scrapy.Request(TUMBLR_HOST + "/following", meta={'cookiejar':response.meta['cookiejar']}, callback=self.parse_follow)

    # 爬取关注用户，其中包含分页。爬取后跳转开始爬取用户帖子内容
    def parse_follow(self, response):
        # 从我的follows出发，爬取当前关注的所有用户
        print("---------------------- start parse following ----------------------")
        userhosts = response.xpath("//div[@id='left_column']/div[contains(@class, 'follower')]/div[@class='info']/div[@class='name']/a/text()").extract()
        if userhosts:
            for userhost in userhosts:
                userUrl = "https://" + userhost + ".tumblr.com/"
                item = TumblrUserInfoItem()
                item['user_host'] = userhost
                yield scrapy.Request(userUrl, meta={'cookiejar':response.meta['cookiejar'], 'item':item}, callback=self.parse_userinfo)

        # 分页
        next_url = response.xpath("//div[@id='pagination']/a[last()]/@href").extract_first()
        if next_url:
            print("next url:" + next_url)
            yield scrapy.Request(TUMBLR_HOST + next_url, meta={'cookiejar': response.meta['cookiejar']}, callback=self.parse_follow)

    # 获取用户信息（第一页）
    def parse_userinfo(self, response):
        # 获取传递信息
        item = response.meta['item']
        # 判断是否还需递归分页
        has_no_more_page = response.xpath("//div[@class='posts-no-posts content']").extract_first()
        # 获取用户数据
        user_avatar = response.xpath("//figure[@class='avatar-wrapper animate']/a/img/@src").extract_first()
        user_name = response.xpath("//div[@class='title-group animate']/h1[@class='blog-title']/a/text()").extract_first()
        user_description = response.xpath("//div[@class='title-group animate']/span[@class='description']/text()").extract_first()

        # 将爬取到的用户数据装载至item传入下一页面
        item['user_avatar'] = user_avatar
        item['user_name'] = user_name
        item['user_description'] = user_description

        # if user_avatar:
        #     print("user avatar:" + user_avatar)
        # if user_name:
        #     print("user name:" + user_name)
        # if user_description:
        #     print("user description:" + user_description)

        # 该方法爬取第一页，如果不是空，则爬取第二页
        if not has_no_more_page:
            item['page'] = 2
            yield scrapy.Request("https://" + item['user_host'] + ".tumblr.com/page/2", meta={'cookiejar':response.meta['cookiejar'], 'item': item}, callback=self.parse_userinfo_more)

        # 判断用户是否存在，不存在则插入该用户
        user_helper = TumblrUserHelper()
        isExist = user_helper.isUserExist(item['user_host'])
        if not isExist:
            user_helper.insertUser(user_name, user_avatar, user_description, item['user_host'])

        # 爬取发帖内容
        self.dispatchTypeByClass(response, item['user_host'])

    # 爬取用户详情内容（分页第二页之后）
    def parse_userinfo_more(self, response):
        # 获取当前页数
        item = response.meta['item']
        page = item['page']
        # 判断是否还需递归分页
        has_no_more_page = response.xpath("//div[@class='posts-no-posts content']").extract_first()

        # 如果没有爬取到无内容则继续向下爬取
        if not has_no_more_page:
            item['page'] = int(page) + 1
            print("get " + item['user_host'] + " page:" + str(item['page']))
            yield scrapy.Request("https://" + item['user_host'] + ".tumblr.com/page/" + str(item['page']), meta={'cookiejar':response.meta['cookiejar'], 'item': item}, callback=self.parse_userinfo_more)

        # 爬取发帖内容
        self.dispatchTypeByClass(response, item['user_host'])


    # ---------------------------- 以下为工具方法 ----------------------------

    # 将当前页面的所有数据进行分类并存储
    def dispatchTypeByClass(self, response, user_host):
        # 图片
        photos_from_user = response.xpath("//article[contains(@class, 'photo not-page')]")
        # 图片组
        photosets_from_user = response.xpath("//article[contains(@class, 'photoset not-page')]")
        # 视频
        videos_from_user = response.xpath("//article[contains(@class, 'video not-page')]")
        # 图片（转发）
        photos_from_other = response.xpath("//article[contains(@class, 'photo reblogged not-page')]")
        # 图片组（转发）
        photosets_from_other = response.xpath("//article[contains(@class, 'photoset reblogged not-page')]")
        # 视频（转发）
        videos_from_other = response.xpath("//article[contains(@class, 'reblogged video not-page')]")

        # 不为空则存在该类型数据
        if photos_from_user:
            for photo_from_user in photos_from_user:
                pic_url = photo_from_user.xpath(".//img[@class!='post-avatar-image']/@src").extract_first()
                pic_helper = TumblrPicHelper()
                isUrlExists = pic_helper.isPicExist(pic_url)
                if isUrlExists:
                    pic_helper.updatePicUser(pic_url, user_host)
                else:
                    pic_helper.insertPicWithUser(pic_url, user_host)

        if photosets_from_user:
            for photoset_from_user in photosets_from_user:
                pic_urls = photoset_from_user.xpath(".//img[@class!='post-avatar-image']/@src").extract()
                pic_helper = TumblrPicHelper()
                for i in range(len(pic_urls)):
                    isFirstUrlExists = pic_helper.isPicExist(pic_urls[i])
                    if isFirstUrlExists:
                        pic_helper.updatePicUser(pic_urls[i],user_host)
                        pic_id = pic_helper.getPicId(pic_urls[0])
                        pic_helper.updatePicGroupId(pic_urls[i], pic_id)
                    else:
                        pic_helper.insertPicWithUser(pic_urls[i], user_host)
                        pic_id = pic_helper.getPicId(pic_urls[0])
                        pic_helper.updatePicGroupId(pic_urls[i], pic_id)

        if videos_from_user:
            for video_from_user in videos_from_user:
                # pic_url = photo_from_user.xpath(".//img/@src").extract_first()
                # 储存url
                pass

        if photos_from_other:
            for photo_from_other in photos_from_other:
                pic_url = photo_from_other.xpath(".//img[@class!='post-avatar-image']/@src").extract_first()
                pic_helper = TumblrPicHelper()
                isUrlExists = pic_helper.isPicExist(pic_url)
                if not isUrlExists:
                    pic_helper.insertPicWithoutUser(pic_url)

        if photosets_from_other:
            # 获得所有转发的article
            for photoset_from_other in photosets_from_other:
                pic_urls = photoset_from_other.xpath(".//img[@class!='post-avatar-image']/@src").extract()
                pic_helper = TumblrPicHelper()
                # 遍历article内的图片
                for i in range(len(pic_urls)):
                    isFirstUrlExists = pic_helper.isPicExist(pic_urls[i])
                    if not isFirstUrlExists:
                        pic_helper.insertPicWithoutUser(pic_urls[i])
                        # 第一张做group_id 索引
                        pic_id = pic_helper.getPicId(pic_urls[0])
                        pic_helper.updatePicGroupId(pic_urls[i], pic_id)

        if videos_from_other:
            for video_from_other in videos_from_other:
                # pic_url = photo_from_user.xpath(".//img/@src").extract_first()
                # 储存url
                pass

    ############################### 以下内容暂时没用  ###############################

    def request_question(self,request):
        return scrapy.Request(request.url,meta={'cookiejar':response.meta['cookiejar']},headers = self.headers,callback=self.parse_question)

    def parse_question(self,response):
        item = zhihuItem()
        item['qestionTitle'] = response.xpath("//div[@id='zh-question-title']//h2/text()").extract_first()
        item['image_urls'] = response.xpath("//img[@class='origin_image zh-lightbox-thumb lazy']/@data-original").extract()
        return item

    # 登陆后第一个
    def parse(self, response):
        print("---------------------- parse ----------------------")
        pics = response.xpath("//a[@class='post_info_link']/@href").extract()
        for pic in pics:
            print(pic.split('/')[4])
        # for url in next_url:
        #     print("next url:" + url)
        test_url = "https://cn1688.tumblr.com/video_file/t:ER35ae7pfjScOgPwcvtF5w/162929507984/tumblr_nuxokqj7bz1udqctx"
        yield scrapy.Request(test_url, callback=self.parse_suburl)

    # 重定向后的视频真实url
    def parse_suburl(self, response):
        print("---------------------- parse video url ----------------------")
        pass
