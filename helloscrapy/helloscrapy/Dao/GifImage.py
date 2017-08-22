import pymysql
import pymysql.cursors

class GifImageHelper:

    def __init__(self):
        self.config = {
            'host' : '104.128.91.88',
            'port' : 3306,
            'user' : 'root',
            'passwd' : '911220',
            'db' : 'test_source',
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

    # 插入一张无用户图片，常用于转发
    def insertOneGif(self, url, title):
        self.connectDB()
        # sql
        sql = "insert into gif_image(url, title) values (%s, %s) "
        cur = self.connection.cursor()
        cur.execute(sql, (url, title))

        self.connection.commit()
        self.connection.close()
