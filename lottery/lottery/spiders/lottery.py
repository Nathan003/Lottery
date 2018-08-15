import scrapy
import re
from ..items import LotteryItem


class LotterySpider(scrapy.Spider):
    # 这里是将爬虫定义为scrapy.Spider这个类下的一个实例。
    # Spider这个类定义了爬虫的很多基本功能，我们直接实例化就好，
    # 省却了很多重写方法的麻烦。
    name = 'lottery'
    # 这是爬虫的名字，这个非常重要。//*[@id="odds"]/table/tbody/tr[5]/td[1]
    start_urls = ['http://a.haocai138.com/info/match/Jingcai.aspx']

    # 这是爬虫开始干活的地址，必须是一个可迭代对象。

    def parse(self, response):
        # 爬虫收到上面的地址后，就会发送requests请求，在收到服务器返回的内容后，就将内容传递给parse函数。在这里我们重写函数，达到我们想要的功能。
        ids = response.xpath("//tr[@gamename]/@id").extract()
        for id in ids:
            date = response.xpath("//*[@id='" + id + "']/td[1]/text()").extract()
            type = response.xpath("//*[@id='" + id + "']/td[2]/a/text()").extract()
            mainTeam = response.xpath("//*[@id='" + id + "']/td[5]/a/text()").extract()
            lottery = response.xpath("//*[@id='" + id + "']/td[5]/font/b/text()").extract()
            guestTeam = response.xpath("//*[@id='" + id + "']/td[7]/a[1]/text()").extract()
            teamId = response.xpath("//*[@id='" + id + "']/td[5]/span[starts-with(@id,'HomeOrder_')]/@id").extract()
            matchId = re.search('[1-9]\\d*', teamId[0], re.M | re.I).group()
            result = response.xpath("//*[@id='" + id + "']/td[6]/text()").extract()
            url = "http://vip.win007.com/changeDetail/handicap.aspx?id=" + matchId + "&companyID=1&l=0"
            yield scrapy.Request(url, callback=self.tendency_parse, meta={
                'info': date[0] + "  " + type[0] + "  " + mainTeam[0] + "(" + lottery[0] + ") vs " + guestTeam[0],
                'id': re.search('[1-9]\\d*', id, re.M | re.I).group(), 'result': result[0]})


    def tendency_parse(self, response):
        item = LotteryItem()
        time = response.xpath("//table[@align='center']/tr/td/span[@id='odds']/table/tr/td[3]/table/tr/td[@bgcolor='red']/../../../../td[1]/text()").extract()
        handicap = response.xpath("//table[@align='center']/tr/td/span[@id='odds']/table/tr/td[3]/table/tr/td[@bgcolor='red']/../../../../td[2]/text()").extract()
        water = response.xpath("//table[@align='center']/tr/td/span[@id='odds']/table/tr/td[3]/table/tr/td[@bgcolor='red']/../../../../td[3]/text()").extract()
        water_new = []
        for i in water:
            water_deal = "".join(i.split())
            water_new.append(water_deal)
        item['result'] = response.meta['result']
        item['id'] = response.meta['id']
        item['info'] = response.meta['info']
        item['tendency'] = {'time': time, 'handicap': handicap, 'water': water_new}
        return item
