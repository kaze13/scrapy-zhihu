__author__ = 'fc'

from scrapy.utils.misc import load_object
from dupefilter import RFPDupeFilter
from scrapy.http import Request, FormRequest
from zhihu.scrapy_redis.nettyMongoCli import NettyMongo

import zhihu.account as account

QUEUE_HOST = 'localhost'
QUEUE_PORT = 10086
SCHEDULER_PERSIST = False
SCHEDULER_QUEUE_CLASS = 'zhihu.scrapy_redis.nqueue.SpiderQueue'

class Scheduler(object):
    login = True # False
    def __init__(self, server, persist, queue_cls):
        self.server = server
        self.persist = persist
        self.queue_cls = queue_cls

    def __len__(self):
        return len(self.queue)

    @classmethod
    def from_settings(cls, settings):
        host = settings.get('QUEUE_HOST', QUEUE_HOST)
        port = settings.get('QUEUE_PORT', QUEUE_PORT)
        persist = settings.get('SCHEDULER_PERSIST', SCHEDULER_PERSIST)
        queue_cls = load_object(settings.get('SCHEDULER_QUEUE_CLASS', SCHEDULER_QUEUE_CLASS))
        server = NettyMongo(host,port)
        return cls(server, persist, queue_cls)

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        cls.stats = crawler.stats
        return cls.from_settings(settings)

    def open(self, spider):
        self.spider = spider
        self.queue = self.queue_cls(self.server, spider)
        if len(self.queue):
            spider.log("Resuming crawl (%d requests scheduled)" % len(self.queue))

    def close(self, reason):
        pass

    def enqueue_request(self, request):
        res = self.queue.push(request)
        if res != 'ERROR':
            self.stats.inc_value('scheduler/enqueued/redis', spider=self.spider)

    def next_request(self):
        if (Scheduler.login == False):
            request = FormRequest(
                "http://www.zhihu.com/login",
                formdata={'email': account.USERNAME,
                          'password': account.PASSWORD
                },
                # callback=self.after_login
            )
            Scheduler.login = True

        else:
            request = self.queue.pop()
            if request:
                self.stats.inc_value('scheduler/dequeued/redis', spider=self.spider)
        return request

    def has_pending_requests(self):
        return len(self) > 0