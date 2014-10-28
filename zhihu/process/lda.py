__author__ = 'fc'
import logging,gensim,pymongo,jieba

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
    return word.replace('\t',' ').replace('\n',' ')


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

    #corpus = set(word for word in wordset if wordset.count(word) > 1)
    dictionary = gensim.corpora.Dictionary(wordset)
    dictionary.save_as_text(dictPath)

def buildCorpus(collection, stoplist, corpusPath, dictPath):
    documents = []
    dict = gensim.corpora.Dictionary.load_from_text(dictPath)
    i = 0
    for item in collection.find():
        i += 1
        seglist = jieba.cut(item['title'].strip())
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

def lda(corpusPath, dictPath):
    dict = gensim.corpora.Dictionary.load_from_text(dictPath)
    print dict
    mm = gensim.corpora.MmCorpus(corpusPath)
    print mm
    lda = gensim.models.LdaModel(corpus=mm, id2word=dict, num_topics=100, update_every=1, chunksize=10000, passes=1)
    lda.print_topics(20)

preprocess()
lda(CORPUS_FILE, DICT_FILE)
# print loadStopList(STOP_FILE)
