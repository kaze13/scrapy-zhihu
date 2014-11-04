__author__ = 'fc'

import telnetlib

'''
HOST = 'localhost'
PORT = 10086
commands = ["http://123.123","GET"]
'''
class NettyMongo(object):
    def __init__(self, host, port):
        self.tn = telnetlib.Telnet(host, port)

    def push(self, string):
        self.tn.write(string + '\n')
        return self.tn.read_until('\n')

    def pop(self):
        self.tn.write('GET\n')
        return self.tn.read_until('\n')

    def close(self):
        self.tn.close()

    def length(self):
        self.tn.write('LEN\n')
        return self.tn.read_until('\n')
