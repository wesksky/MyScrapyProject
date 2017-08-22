import pymysql
import pymysql.cursors

class TumblrUserHelper:

    def __init__(self):
        self.config = {
            'host' : '104.128.91.88',
            'port' : 3306,
            'user' : 'root',
            'passwd' : '911220',
            'db' : 'tumblr',
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
    def isUserExist(self, user_host):
        # sql
        sql = "select * from user where user_host=%s;"
        cur = self.connection.cursor()
        cur.execute(sql,(user_host,))
        data = cur.fetchone()

        self.connection.close()

        if data:
            return True
        else:
            return False

    # 检测是否需要绑定
    def insertUser(self, user_name, user_avatar, user_description, user_host):
        self.connectDB()
        # 清除desc中多余空格
        if user_description:
            user_description = user_description.strip()
        # 插入Tumblr User
        sql = "replace into user(username, avatar, description, url, user_host) values(%s, %s, %s, %s, %s) "
        cur = self.connection.cursor()
        cur.execute(sql, (user_name, user_avatar, user_description, "https://" + user_host + ".tumblr.com/", user_host))

        self.connection.commit()
        self.connection.close()

    # 检测是否需要绑定
    def isPicExist(self, title, url):
        self.connectDB()
        # sql
        sql = "replace into huoying(title, url) values(%s, %s) "
        cur = self.connection.cursor()
        cur.execute(sql,(title, url))

        self.connection.commit()
        self.connection.close()
