__author__ = 'fc'


from scrapy.utils.reqser import request_from_dict, request_to_dict

try:
    import cPickle as pickle
except ImportError:
    import pickle

class Base(object):
    def __init__(self, server, spider):
        self.server = server
        self.spider = spider

    def _encode_request(self, request):
        return pickle.dumps(request_to_dict(request, self.spider), protocol=-1)

    def _decode_request(self, encoded_request):
        return request_from_dict(pickle.loads(encoded_request), self.spider)

    def __len__(self):
        raise NotImplementedError

    def push(self):
        raise NotImplementedError

    def pop(self):
        raise NotImplementedError

    def clear(self):
        self.server.delete(self.key)

class SpiderQueue(Base):

    def __len__(self):
        return self.server.length()

    def push(self, request):
        self.server.push(self._encode_request(request))

    def pop(self):
        data = self.server.pop()
        if data:
            return self._decode_request(data)


