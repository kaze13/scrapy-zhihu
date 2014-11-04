from sklearn.neighbors import NearestNeighbors
import numpy as np
import math,pymongo,heapq

class BruteForce:
    '''
        This is a bruteforce algorithm,
        Although it is slow, but it may works since it doesn't need so much ram.
    '''
    def __init__(self):
        pass

    def __temp_save_to_file(self, collection, topicNum):
        with open('temp_topic.txt','w') as f:
            for item in collection.find():
                if item.get('topics') is not None:
                    topicsI = [0] * topicNum
                    for tuple in item['topics']:
                        topicsI[tuple[0]] = tuple[1]
                    f.write(item['url'] + '\t' + '\t'.join([str(topic) for topic in topicsI]) + '\n')



    '''
        This can be done, but it takes a lot of time
    '''
    def __learn(self, collection, topicNum, n):
        with open('temp_topic.txt','r') as f:
            idx = 0
            for line in f.readlines():
                idx += 1
                print idx
                seps = line.split('\t')
                url = seps[0]
                topicI = [float(seps[i]) for i in range(1,len(seps))]
                dist = []
                for itemJ in collection.find():
                    if itemJ.get('topics') != None and itemJ.get('url') != url:
                        topicsJ = [0] * topicNum
                        for tuple in itemJ['topics']:
                            topicsJ[tuple[0]] = tuple[1]
                        sim = sum([topicI[i] * topicsJ[i] for i in range(0,100)]) / math.sqrt(sum([x * x for x in topicI])) * math.sqrt(sum([x * x for x in topicsJ]))
                        dist.append((itemJ['url'], sim))
                # nn = sorted(dist, key= lambda ele : -ele[1])
                nn = heapq.nlargest(n, dist, key = lambda ele : ele[1])
                collection.update({'url': url}, {"$set": {"neighbour": nn}})

    def __learn2(self, collection, topicNum, n):
        topicId = []
        topicArray = []
        print 'start collect'
        for item in collection.find():
            topicId.append(item['url'])
            topics = [0] * int(topicNum)
            if item.get('topics') is not None:
                for tuple in item['topics']:
                    topics[tuple[0]] = tuple[1]
                topicArray.append(topics)
        nbrs = NearestNeighbors(n_neighbors=1, algorithm='ball_tree').fit(topicArray)
        print 'finish collect'
        idx = 0
        with open('temp_topic.txt','r') as f:
            for line in f.readlines():
                idx += 1
                if idx % 1000 == 0:
                    print idx
                seps = line.split('\t')
                url = seps[0]
                topicI = [float(seps[i]) for i in range(1,len(seps))]
                nnset = nbrs.kneighbors(topicI, 10, return_distance=False)[0]
                collection.update({'url': url},{"$set" : {"rec" : [topicId[key] for key in nnset]}})

    def search(self, collection, topicNum = 100, n = 10):
        print 'temp save'
        self.__temp_save_to_file(collection, topicNum)
        print 'learn'
        self.__learn2(collection, topicNum, n)
#         for itemI in collection.find():
#             dist = []
#             for itemJ in collection.find():
#                 distance = self.__calDist(itemI, itemJ, topicNum)
#                 dist.append((itemJ['url'], distance))
#             nn = sorted(dist, key= lambda ele : -ele[1])
#             fetch N
#             collection.update({'url':itemI['url']},{"$set" : {"neighbour" : nn[:10]}})

    def __calDist(self, itemI, itemJ, topicNum):
        if itemI.get('topics') == None or itemJ.get('topics') == None:
            return 0
        topicsI = [0] * topicNum
        topicsJ = [0] * topicNum
        for tuple in itemI['topics']:
            topicsI[tuple[0]] = tuple[1]
        for tuple in itemJ['topics']:
            topicsJ[tuple[0]] = tuple[1]

#       cosine similarity
        return sum([topicsI[i] * topicsJ[i] for i in range(0,100)]) / math.sqrt(sum([x * x for x in topicsI])) * math.sqrt(sum([x * x for x in topicsJ]))


connection = pymongo.Connection('rey', 27017)
if connection != None:
    collection = connection['zhihu']['zh_ask']
    bf = BruteForce()
    bf.search(collection,100,10)
    connection.close()


class NNS:
    '''
       This is the nearest neighbour search algorithm
    '''
    def __init__(self):
        pass

    def search(self, collection, topicNum = 100):
        topicId = []
        topicArray = []
        print 'start collect'
        for item in collection.find():
            topicId.append(item['url'])
            topics = [0] * int(topicNum)
            if item.get('topics') is not None:
                for tuple in item['topics']:
                    topics[tuple[0]] = tuple[1]
                topicArray.append(topics)

        print 'start nns'
        nbrs = NearestNeighbors(n_neighbors=2, algorithm='ball_tree').fit(topicArray)
        print 'judge '
        nnset = [[i for i, doc in enumerate(vector) if doc == 1 ] for vector in nbrs.kneighbors_graph(topicArray).toarray()]
        print 'update'
        for i,recs in enumerate(nnset):
            print i , ':',recs
            collection.update({'url':topicId[i]},{"$set" : {"rec" : [topicId[key] for key in recs]}})

