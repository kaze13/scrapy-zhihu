__author__ = 'fc'
import logging,gensim,pymongo,jieba
from operator import itemgetter
# from collections import Counter

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO )

# documents = ["Human machine interface for lab abc computer applications",
#              "A survey of user opinion of computer system response time",
#              "The EPS user interface management system",
#              "System and human system engineering testing of EPS",
#              "Relation of user perceived response time to error measurement",
#              "The generation of random binary unordered trees",
#              "The intersection graph of paths in trees",
#              "Graph minors IV Widths of trees and well quasi ordering",
#              "Graph minors A survey"]
#
# stoplist = set('for a of the and to in'.split())
# texts = [[word for word in document.lower().split() if word not in stoplist] for document in documents]
#
# all_tokens = sum(texts, [])
# tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
# texts = [[word for word in texts if word not in tokens_once] for text in texts]
#
# dictionary = corpora.Dictionary(texts)
#
# print dictionary.token2id
# new_doc = "Human computer interaction"
# new_vec = dictionary.doc2bow(new_doc.lower().split())
# print(new_vec)
#
# corpus = [dictionary.doc2bow(text) for text in texts]
# corpora.MmCorpus.serialize('deerwester.mm', corpus)
# print(corpus)

DICT_FILE = "zhihuDict.txt"
CORPUS_FILE = 'zhihuCorpus.mm'
STOP_FILE = 'stoplist.txt'
LDA_FILE = 'lda.mm'

def loadStopList(stopPath):
    stoplist = set([])
    with open(stopPath, 'r') as f:
        for line in f.readlines():
            stoplist.add(line.replace('\n','').decode('utf-8'))
    return stoplist

def checkWord(word):
    if word.replace('.','',1).isdigit():
        return False
    return True

def cleanString(word):
    return word.replace('\t',' ').replace('\n',' ').replace('\r',' ')


def buildDictionary(collection, stoplist, dictPath):
    wordset = []
    i = 0
    for item in collection.find():
        i += 1
        if i % 1000 == 0:
            print i
        seglist = jieba.cut(cleanString(item['title']))
        before = [seg.lower() for seg in seglist]
        tokens = [seg.lower() for seg in before if seg not in stoplist and checkWord(seg)]
        wordset.append(tokens)
    # TODO think about how to remove td=1 token in memory
    # count = Counter(all_tokens = sum(wordset, []))
    # token_once = set(word[0] for word in count.items() if word[1] == 1)
    # corpus = [[word for word in text if word not in token_once] for text in wordset]
    # dictionary = gensim.corpora.Dictionary(corpus)


    dictionary = gensim.corpora.Dictionary(wordset)
    dictionary.save_as_text(dictPath)
    # remove td=1 token in text file
    wordset = None
    dictset = []
    with open(dictPath, 'r') as f:
        for line in f.readlines():
            if(int(line.split('\t')[-1].replace('\n','')) > 1):
                dictset.append(line)

    with open(dictPath, 'w') as f:
        for line in dictset:
            f.write(line)

def buildCorpus(collection, stoplist, corpusPath, dictPath):
    documents = []
    dict = gensim.corpora.Dictionary.load_from_text(dictPath)
    i = 0
    for item in collection.find():
        i += 1
        seglist = jieba.cut(cleanString(item['title']))
        tokens = [seg.lower() for seg in seglist if seg not in stoplist and checkWord(seg)]
        segment = dict.doc2bow(tokens)
        documents.append(segment)
        if i % 1000 == 0:
            print i
    print 'save corpus'
    gensim.corpora.MmCorpus.serialize(corpusPath, documents)

def loadCorpus(path):
    return gensim.corpora.MmCorpus(path)

def loadDictionary(path):
    return gensim.corpora.Dictionary.load_from_text(path)

def preprocess():
    connection = pymongo.Connection('rey', 27017)
    stoplist = loadStopList(STOP_FILE)
    print 'start build dictionary'
    buildDictionary(connection['zhihu']['zh_ask'],stoplist,DICT_FILE)
    print 'start build corpus'
    buildCorpus(connection['zhihu']['zh_ask'],stoplist,CORPUS_FILE,DICT_FILE)
    if connection != None:
        connection.close()

def lda(corpusPath, dictPath, ldaPath):
    dict = gensim.corpora.Dictionary.load_from_text(dictPath)
    print dict
    mm = gensim.corpora.MmCorpus(corpusPath)
    print mm
    lda = gensim.models.LdaModel(corpus=mm, id2word=dict, num_topics=100, update_every=1, chunksize=10000, passes=1)
    lda.print_topics(20)
    lda.save(ldaPath)

def inference(dictPath,ldaPath):
    stoplist = loadStopList(STOP_FILE)
    lda = gensim.models.LdaModel.load(ldaPath)
    dict = gensim.corpora.Dictionary.load_from_text(dictPath)
    lda.print_topics(20)
    connection = pymongo.Connection('rey', 27017)
    collection = connection['zhihu']['zh_ask']
    i = 0
    for item in collection.find():
        i = i + 1
        if i % 1000 == 0:
            print i
        seglist = jieba.cut(cleanString(item['title']))
        tokens = [seg.lower() for seg in seglist if seg not in stoplist and checkWord(seg)]
        segment = dict.doc2bow(tokens)
        doc_lda = lda[segment]
        # use hard cluster method
        if len(doc_lda) > 0:
            topic = max(doc_lda, key=itemgetter(1))[0]
        # store topic
        collection.update({'_id':item['_id']},{"$set" : {"topic" : topic}})
    if connection != None:
        connection.close()

# preprocess()
# lda(CORPUS_FILE, DICT_FILE,LDA_FILE)

inference(DICT_FILE,LDA_FILE)
# print loadStopList(STOP_FILE)
