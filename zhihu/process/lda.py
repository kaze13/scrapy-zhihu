__author__ = 'fc'
import logging,gensim,pymongo,jieba
from operator import itemgetter
# from collections import Counter

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO )

DICT_FILE = "zhihuDict.txt"
CORPUS_FILE = 'zhihuCorpus.mm'
STOP_FILE = 'stoplist.txt'
LDA_FILE = 'lda.mm'

def checkWord(word):
        if word.replace('.','',1).isdigit():
            return False
        return True

def cleanString(word):
    return word.replace('\t',' ').replace('\n',' ').replace('\r',' ')

def toTokens(attr, stoplist):
    seglist = jieba.cut(cleanString(attr))
    return [seg.lower() for seg in seglist if seg not in stoplist and checkWord(seg)]

class PreProcess:

    def __init__(self, stoplistPath, dictPath, corpusPath):
        self.__stoplistPath = stoplistPath
        self.__dictPath = dictPath
        self.__corpusPath = corpusPath

    def loadStopList(self):
        stoplist = set([])
        with open(self.__stoplistPath, 'r') as f:
            for line in f.readlines():
                stoplist.add(line.replace('\n','').decode('utf-8'))
        return stoplist

    def __buildDictionary(self, collection, stoplist, dictPath):
        wordset = []
        for item in collection.find():
            # seglist = jieba.cut(cleanString(item['title']))
            # tokens = [seg.lower() for seg in seglist if seg not in stoplist and checkWord(seg)]
            tokens = toTokens(item['title'], stoplist)
            wordset.append(tokens)
        # TODO think about how to remove td=1 token in memory
        # count = Counter(all_tokens = sum(wordset, []))
        # token_once = set(word[0] for word in count.items() if word[1] == 1)
        # corpus = [[word for word in text if word not in token_once] for text in wordset]
        # dictionary = gensim.corpora.Dictionary(corpus)

        dict = gensim.corpora.Dictionary(wordset)
        dict.save_as_text(dictPath)
        # remove td=1 token in text file
        wordset = None
        # dictset = []
        # with open(dictPath, 'r') as f:
        #     for line in f.readlines():
        #         if(int(line.split('\t')[-1].replace('\n','')) > 1):
        #             dictset.append(line)
        #
        # with open(dictPath, 'w') as f:
        #     for line in dictset:
        #         f.write(line)

    def __buildCorpus(self, collection, stoplist, corpusPath, dictPath):
        documents = []
        dict = gensim.corpora.Dictionary.load_from_text(dictPath)
        for item in collection.find():
            # seglist = jieba.cut(cleanString(item['title']))
            # tokens = [seg.lower() for seg in seglist if seg not in stoplist and checkWord(seg)]
            tokens = toTokens(item['title'], stoplist)
            segment = dict.doc2bow(tokens)
            documents.append(segment)
        gensim.corpora.MmCorpus.serialize(corpusPath, documents)

    def loadCorpus(self):
        return gensim.corpora.MmCorpus(self.__corpusPath)

    def loadDictionary(self):
        return gensim.corpora.Dictionary.load_from_text(self.__dictPath)

    # def loadAll(self):
    #     self.loadCorpus()
    #     self.loadStopList()
    #     self.loadDictionary()

    def preprocess(self, collections):
        stoplist = self.loadStopList()
        self.__buildDictionary(collections,stoplist, self.__dictPath)
        self.__buildCorpus(collections,stoplist, self.__corpusPath, self.__dictPath)

class LDAWrapper:
    def __init__(self, preprocess):
        self.preprocess = preprocess

    def train(self):
        self.lda = gensim.models.LdaModel(corpus=self.preprocess.loadCorpus(), id2word=self.preprocess.loadDictionary(), num_topics=100, update_every=1, chunksize=10000, passes=1, iterations=5)
        self.lda.print_topics(20)

    def loadLDA(self,ldaPath):
        self.lda = gensim.models.LdaModel.load(ldaPath)

    def save(self, ldaPath):
        self.lda.save(ldaPath)

    def inference(self, collection):
        stoplist = self.preprocess.loadStopList()
        dict = self.preprocess.loadDictionary()
        self.lda.print_topics(20)
        for item in collection.find():
            # seglist = jieba.cut(cleanString(item['title']))
            # tokens = [seg.lower() for seg in seglist if seg not in stoplist and checkWord(seg)]
            tokens = toTokens(item['title'], stoplist)
            segment = dict.doc2bow(tokens)
            doc_lda = self.lda[segment]
            # use hard cluster method
            if len(doc_lda) > 0:
                print doc_lda
                topic = max(doc_lda, key=itemgetter(1))[0]
                # store topic
                collection.update({'_id':item['_id']},{"$set" : {"topic" : topic, "topics" : doc_lda}})


def run():
    connection = pymongo.Connection('rey', 27017)
    if connection != None:
        collection = connection['zhihu']['zh_ask']
        preprocess = PreProcess(STOP_FILE, DICT_FILE, CORPUS_FILE)
        preprocess.preprocess(collection)

        lda = LDAWrapper(preprocess)
        lda.loadLDA(LDA_FILE)
        lda.train()
        lda.inference(collection)
        # nns = NNS()
        # nns.search(collection)
        connection.close()

def revert():
    connection = pymongo.Connection('rey', 27017)
    if connection != None:
        collection = connection['zhihu']['zh_ask']
        for item in collection.find():
            if item['_id'] != item['url']:
                collection.update({'_id': item['_id']}, {"$set" : {"_id" : item['url']}})
        connection.close()

run()


