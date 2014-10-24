import random

from scrapy import log

from zhihu.misc.proxy import PROXIES
from zhihu.misc.agents import AGENTS
from scrapy.conf import settings

class CustomHttpProxyMiddleware(object):

    def process_request(self, request, spider):
        # TODO implement complex proxy providing algorithm
        if self.use_proxy():
            try:
                request.meta['proxy'] = "http://%s" % settings.get('PROXY')
            except Exception, e:
                log.msg("Exception %s" % e, _level=log.CRITICAL)

    def use_proxy(self):
        # """
        # using direct download for depth <= 2
        # using proxy with probability 0.3
        # """
        # if "depth" in request.meta and int(request.meta['depth']) <= 2:
        #     return False
        # i = random.randint(1, 10)
        # return i <= 2
        if settings.get('PROXY'):
            return True
        else:
            return False


class CustomUserAgentMiddleware(object):
    def process_request(self, request, spider):
        agent = random.choice(AGENTS)
        request.headers['User-Agent'] = agent
