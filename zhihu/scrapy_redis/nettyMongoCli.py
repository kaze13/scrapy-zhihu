DELIMITER = '\r\n'
__author__ = 'fc'

import telnetlib
import random
import threading

'''
HOST = 'localhost'
PORT = 10086
commands = ["http://123.123","GET"]
'''
class NettyMongo(object):
    def __init__(self, host, port):
        self.tn = telnetlib.Telnet(host, port)
        self.lock = threading.Lock()

    def push(self, string):
        self.lock.acquire()
        try:
            self.tn.write(string + DELIMITER)
            res = self.tn.read_until(DELIMITER)[:-2]
        finally:
            self.lock.release()

    def pop(self):
        self.lock.acquire()
        try:
            self.tn.write('GET' + DELIMITER)
            res = self.tn.read_until(DELIMITER)[:-2]
            if len(res) > 0:
                return res
            else:
                return None
        finally:
            self.lock.release()

    def close(self):
        self.tn.close()

    def length(self):
        self.lock.acquire()
        try:
            self.tn.write('LEN' + DELIMITER)
            res = self.tn.read_until(DELIMITER)[:-2]
            print 'len: %s' % (res)
            return int(res)
        finally:
            self.lock.release()

if __name__ == '__main__':
    nm = NettyMongo('localhost',10086)
    for i in range(0,1000):
        j = random.randint(0,3)
        if j == 0:
            # nm.push("http://123.123/" + str(random.randint(0,10000)))
            pass
        elif j == 1:
            nm.pop()
        elif j == 2:
            nm.length()

    nm.close()



