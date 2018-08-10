import scrapy
from ..items import LotteryItem


class LotterySpider(scrapy.Spider):
    # 这里是将爬虫定义为scrapy.Spider这个类下的一个实例。
    # Spider这个类定义了爬虫的很多基本功能，我们直接实例化就好，
    # 省却了很多重写方法的麻烦。
    name = 'lottery'
    # 这是爬虫的名字，这个非常重要。
    start_urls = ['http://a.haocai138.com/info/match/Jingcai.aspx']

    # 这是爬虫开始干活的地址，必须是一个可迭代对象。

    def parse(self, response):
        # 爬虫收到上面的地址后，就会发送requests请求，在收到服务器返回的内容后，就将内容传递给parse函数。在这里我们重写函数，达到我们想要的功能。
        ids = response.xpath("//tr[@gamename]/@id").extract()
        items = []
        for id in ids:
            item = LotteryItem()
            type = response.xpath("//*[@id='" + id + "']/td[2]/a/text()").extract()
            mainTeam = response.xpath("//*[@id='" + id + "']/td[5]/a/text()").extract()
            lottery = response.xpath("//*[@id='" + id + "']/td[5]/font/b/text()").extract()
            guestTeam = response.xpath("//*[@id='" + id + "']/td[7]/a[1]/text()").extract()
            item['info'] = type[0] + "  " + mainTeam[0] + "(" + lottery[0] + ") vs " + guestTeam[0]
            items.append(item)
        return items
