__author__ = 'fc'

import scrapy

class DoubanmusicItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    songname = scrapy.Field()
    attr = scrapy.Field()
    basic = scrapy.Field()
    publisher = scrapy.Field()
    actor = scrapy.Field()
    abstract = scrapy.Field()
    songs = scrapy.Field()
    rate = scrapy.Field()
    ratenum = scrapy.Field()
    star5 = scrapy.Field()
    star4 = scrapy.Field()
    star3 = scrapy.Field()
    star2 = scrapy.Field()
    star1 = scrapy.Field()
    pass

class DoubanReviewItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    name = scrapy.Field()
    description = scrapy.Field()
    date = scrapy.Field()