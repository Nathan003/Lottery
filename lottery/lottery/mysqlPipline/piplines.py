import pymysql
import re
import datetime

from pymysql import Error
from twisted.enterprise import adbapi  # twisted的enterprise中有一个模块adbapi,可以将我们的mysql操作变成异步的操作


class MySQLTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DB_NAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWORD'],
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor
        )  # 参数名称是固定的的写法

        dbpool = adbapi.ConnectionPool('pymysql', **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)  # 处理异常
        return item

    def handle_error(self, failure):  # 处理异步插入的异常
        print(failure)

    def water_judge(self, water):
        if water <= 0.75:
            return '超低水'
        if 0.75 < water <= 0.85:
            return '低水'
        if 0.86 <= water <= 0.90:
            return '中低水'
        if 0.91 <= water <= 0.95:
            return '中水'
        if 0.96 <= water <= 1.00:
            return '中高水'
        if 1.00 < water <= 1.08:
            return '高水'
        if water > 1.08:
            return '超高水'

    def do_insert(self, cursor, item):  # 执行具体的插入
        dict = {'三球': -3, '两球半/三球': -2.75, '两球半': -2.5, '两球/两球半': -2.25, '两球': -2, '球半/两球': -1.75,
                '球半': -1.5, '一球/球半': -1.25, '一球': -1, '半球/一球': -0.75, '半球': -0.5, '平手/半球': -0.25, '平手': 0,
                '受让三球': 3, '受让两球半/三球': 2.75, '受让两球半': 2.5, '受让两球/两球半': 2.25, '受让两球': 2, '受让球半/两球': 1.75,
                '受让球半': 1.5, '受让一球/球半': 1.25, '受让一球': 1, '受让半球/一球': 0.75, '受让半球': 0.5, '受让平手/半球': 0.25}
        sql = 'INSERT INTO lottery (match_id,jingcai_id,type,title,change_time,handicap,' \
              'handicap_cn,water,water_cn,result) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'
        match_id = item['id']
        result = item['result']
        jingcai_id = item['info'].split('  ')[0]
        type = item['info'].split('  ')[1]
        title = item['info'].split('  ')[2]
        for index in range(len(item['tendency']['handicap'])):
            change_time = item['tendency']['time'][index]
            tidy_time = str(datetime.datetime(datetime.datetime.now().year,
                                              int(re.split(r'[- :]', change_time)[0]),
                                              int(re.split(r'[- :]', change_time)[1]),
                                              int(re.split(r'[- :]', change_time)[2]),
                                              int(re.split(r'[- :]', change_time)[3]),
                                              0))
            update_sql = " update lottery set result = '" + result + "' where match_id = '" + match_id + "' and change_time = '" + tidy_time + "'; "
            handicap = dict[item['tendency']['handicap'][index] + '']
            handicap_cn = item['tendency']['handicap'][index]
            water = item['tendency']['water'][index]
            water_cn = self.water_judge(float(water))
            values = (match_id, jingcai_id, type, title, tidy_time,
                      handicap, handicap_cn, water, water_cn, result)
            try:
                cursor.execute(sql, values)
            except Error as e:
                print(e)
                cursor.execute(update_sql)
                print('update完成~')
