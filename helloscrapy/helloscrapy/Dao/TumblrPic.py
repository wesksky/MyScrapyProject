import pymysql
import pymysql.cursors

class TumblrPicHelper:

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

    # 检测图片是否已经存在
    def isPicExist(self, url):
        self.connectDB()
        # sql
        sql = "select * from pic where url = %s "
        cur = self.connection.cursor()
        cur.execute(sql, (url,))
        data = cur.fetchone()
        self.connection.close()

        if data:
            return True
        else:
            return False

    # 设置图片的所属用户
    def updatePicUser(self, url, user_host):
        self.connectDB()

        sql = "update pic set user_host = %s where url = %s "
        cur = self.connection.cursor()
        cur.execute(sql, (user_host, url))

        self.connection.commit()
        self.connection.close()

    # 插入一张无用户图片，常用于转发
    def insertPicWithoutUser(self, url):
        self.connectDB()
        # sql
        sql = "insert into pic(url) values (%s) "
        cur = self.connection.cursor()
        cur.execute(sql, (url,))

        self.connection.commit()
        self.connection.close()

    def insertPicWithUser(self, url, user_host):
        self.connectDB()
        # sql
        sql = "insert into pic(url, user_host) values (%s, %s) "
        cur = self.connection.cursor()
        cur.execute(sql, (url, user_host))

        self.connection.commit()
        self.connection.close()

    def getPicId(self, url):
        self.connectDB()
        # sql
        sql = "select id from pic where url = %s "
        cur = self.connection.cursor()
        cur.execute(sql, (url,))
        data = cur.fetchone()

        self.connection.close()

        return data['id']

    def updatePicGroupId(self, url, group_id):
        self.connectDB()
        # sql
        sql = "update pic set group_id = %s where url = %s"
        cur = self.connection.cursor()
        cur.execute(sql, (group_id,url))

        self.connection.commit()
        self.connection.close()
