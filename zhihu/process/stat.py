__author__ = 'fc'

'''
This module is for generating status:
    0) General information: # of
    1) The average rating(ask, answer) for one person
    2) The average reponse(answer) for one question
'''

import pymongo

def generalInfo(connection):
    db = connection['zhihu']
    zh_user_col = db["zh_user"]
    zh_ask_col = db["zh_ask"]
    zh_answer_col = db["zh_answer"]
    user_num = zh_user_col.count()
    ask_num = zh_ask_col.count()
    answer_num = zh_answer_col.count()
    return user_num,ask_num,answer_num

connection = pymongo.Connection('rey', 27017)
res = generalInfo(connection)
print res