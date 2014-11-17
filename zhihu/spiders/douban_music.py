__author__ = 'fc'
# -*- coding: utf-8 -*-
import scrapy
from zhihu.douban_items import DoubanmusicItem,DoubanReviewItem
from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor

class MusicSpider(CrawlSpider):
    name = "music"
    allowed_domains = ["douban.com"]
    start_urls = [
        # "http://music.douban.com/subject/1411645/",
        "http://music.douban.com/",
        "http://music.douban.com/musician/103939/"
        # "http://music.douban.com/subject/26067993/"
        #'http://music.douban.com/',
    ]

    rules = [
       Rule(LinkExtractor(allow=('subject/\d+/reviews?sort=time$')), callback='parseReview', follow=True),
       Rule(LinkExtractor(allow=('subject/\d+/$',)), callback='parseCD', follow=True),
    ]

    # def parse(self, response):
    def parseCD(self, response):
        selector = Selector(response)
        item = DoubanmusicItem()
        item['url'] = response.url
        item['songname'] = (''.join(selector.xpath("//div[@id='wrapper']/h1/span/text()").extract())).strip()
        item['actor'] = (' '.join(selector.xpath("//div[@id='info']/span/span/a/text()").extract())).strip()
        item['basic'] = (' '.join(selector.xpath("//div[@id='info']/text()").extract())).strip().replace('\n','').replace('\r','');
        item['attr'] = (' '.join(selector.xpath("//div[@id='info']/span[@class='pl']/text()").extract())).strip();
        # idx = 0
        # for record in selector.xpath("//div[@id='info']/text()"):
        #     str = (''.join(record.extract())).strip()
        #     if len(str) > 0:
        #         if idx == 0:
        #             item['songanothername'] = str
        #         elif idx == 1:
        #             item['genre'] = str
        #         elif idx == 2:
        #             item['type'] = str
        #         elif idx == 3:
        #             item['media'] = str
        #         elif idx == 4:
        #             item['releasedate'] = str
        #         idx += 1
        #         # print str

        item['abstract'] = (''.join(selector.xpath("//div[@id='link-report']/span/text()").extract())).strip()
        item['songs'] = (' '.join(selector.xpath("//div[@class='related_info']/div/div[@class='indent']/div/text()").extract())).strip()
        if len(item['songs']) == 0:
            item['songs'] = (' '.join(selector.xpath("//ul[@class='song-items']/li[@class='song-item']//div[@class='col song-name-short']/span/text()").extract())).strip()
        item['rate'] = (''.join(selector.xpath("//div[@id='interest_sectl']/div/p/strong/text()").extract())).strip()
        item['ratenum'] = (''.join(selector.xpath("//div[@id='interest_sectl']/div/p/a/span/text()").extract())).strip()
        item['star5'] = (''.join(selector.xpath("//div[@id='interest_sectl']/div/text()[5]").extract())).strip()
        item['star4'] = (''.join(selector.xpath("//div[@id='interest_sectl']/div/text()[8]").extract())).strip()
        item['star3'] = (''.join(selector.xpath("//div[@id='interest_sectl']/div/text()[11]").extract())).strip()
        item['star2'] = (''.join(selector.xpath("//div[@id='interest_sectl']/div/text()[14]").extract())).strip()
        item['star1'] = (''.join(selector.xpath("//div[@id='interest_sectl']/div/text()[17]").extract())).strip()
        return item

    def parseReview(self, response):
    # def parse(self, response):
        selector = Selector(response)
        for record in selector.xpath("//ul[@class='tlst clearfix']"):
            review = DoubanReviewItem()
            review['url'] = response.url
            review['description'] = (''.join(record.xpath("li[@class='clst report-link']/div[@class='review-short']/text()").extract())).strip()
            review['date'] = (''.join(record.xpath("li[@class='clst report-link']/div[@class='review-short']/div[@class='pl clearfix']/span/text()").extract())).strip()
            review['name'] = (''.join(record.xpath("li[@class='clst report-link']/span[@class='pl ll obss']/span[@class='starb']/a/text()").extract())).strip()
            review['title'] = (''.join(record.xpath("li[@class='nlst']/h3/a/text()").extract())).strip()
            yield review
        pass