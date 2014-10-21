# -*- coding:utf-8 -*-

from scrapy.selector import Selector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http import Request,FormRequest
from zhihu.items import ZhihuUserItem, ZhihuAskItem, ZhihuAnswerItem

import json
from urllib import urlencode
from datetime import datetime

import sys

reload(sys)
sys.setdefaultencoding('utf-8') #dirty hack;  remove it later

host='http://www.zhihu.com'

class ZhihuLoginSpider(CrawlSpider):
    name = 'zhihu_user'
    allowed_domains = ['zhihu.com']

    start_urls = [
        "http://www.zhihu.com/lookup/people",
        ]

    #使用rule时候，不要定义parse方法
    rules = (
        Rule(SgmlLinkExtractor(allow=("/lookup/class/[^/]+/?$", )), follow=True,callback='parse_item'),
        Rule(SgmlLinkExtractor(allow=("/lookup/class/$", )), follow=True,callback='parse_item'),
        Rule(SgmlLinkExtractor(allow=("/lookup/people", )),  callback='parse_item'),
        Rule(SgmlLinkExtractor(allow=("/people/[^/]+/?$", )),  callback='parse_user'),
        Rule(SgmlLinkExtractor(allow=("/people/$", )),  callback='parse_user')
    )

    def __init__(self,  *a,  **kwargs):
        super(ZhihuLoginSpider, self).__init__(*a, **kwargs)
        self.user_names = []


    def start_requests(self):
        return [FormRequest(
            "http://www.zhihu.com/login",
            formdata = {'email':'cml_hawke0@163.com',
                        'password':'56121353'
            },
            callback = self.after_login
        )]

    def after_login(self, response):
        for url in self.start_urls:
            yield self.make_requests_from_url(url)

    def parse_item(self, response):
        print 'parsing url: %s' % response.url
        selector = Selector(response)
        for link in selector.xpath('//div[@id="suggest-list-wrap"]/ul/li/div/a/@href').extract():
            #link  ===> /people/javachen
            yield Request(host+link+"/about", callback=self.parse_user)

    def parse_user(self, response):
        print 'parsing url: %s' % response.url
        selector = Selector(response)
        user = ZhihuUserItem()
        user['_id']=user['username']=response.url.split('/')[-1]
        user['url']= response.url
        user['nickname'] = ''.join(selector.xpath("//div[@class='title-section ellipsis']/a[@class='name']/text()").extract())
        user['location'] = ''.join(selector.xpath("//span[@class='location item']/@title").extract())
        user['industry'] = ''.join(selector.xpath("//span[@class='business item']/@title").extract())
        user['sex'] = ''.join(selector.xpath('//div[@class="item editable-group"]/span/span[@class="item"]/i/@class').extract()).replace("zg-icon gender ","")
        user['description'] = ''.join(selector.xpath("//span[@class='description unfold-item']/span/text()").extract()).strip().replace("\n",'')
        user['view_num'] = ''.join(selector.xpath("//span[@class='zg-gray-normal']/strong/text()").extract())
        user['update_time'] = str(datetime.now())

        user['jobs'] = []
        job_nodes = selector.xpath('//div[@class="zm-profile-module zg-clear"][1]/div/ul[@class="zm-profile-details-items"]/li')
        for node in job_nodes:
            company = ''.join(node.xpath('@data-title').extract())
            title = ''.join(node.xpath('@data-sub-title').extract())
            user['jobs'].append({'company': company, 'title':title})

        user['educations'] = []
        edu_nodes = selector.xpath('//div[@class="zm-profile-module zg-clear"][3]/div/ul[@class="zm-profile-details-items"]/li')
        for node in edu_nodes:
            school = ''.join(node.xpath('@data-title').extract())
            major = ''.join(node.xpath('@data-sub-title').extract())
            user['educations'].append({'school':school, 'major':major})

        user['sinaweibo']=''
        user['tencentweibo']=''
        for node in selector.xpath("//a[@class='zm-profile-header-user-weibo']/@href").extract():
            if node.startswith('http://weibo.com'):
                user['sinaweibo'] = node
            elif node.startswith('http://t.qq.com'):
                user['tencentweibo'] = node

        statistics = selector.xpath("//a[@class='item']/strong/text()").extract()
        followee_num =user['followee_num'] = statistics[0]
        follower_num = user['follower_num']= statistics[1]

        statistics = selector.xpath("//div[@class='zm-profile-module-desc']/span/strong/text()").extract()
        if len(statistics) ==4:
            user['agree_num'] = statistics[0]
            user['thank_num'] = statistics[1]
            user['fav_num'] = statistics[2]
            user['share_num'] = statistics[3]

        statistics = selector.xpath("//div[@class='profile-navbar clearfix']/a/span/text()").extract()
        if len(statistics) ==6:
            user['ask_num'] = statistics[1]
            user['answer_num'] = statistics[2]
            user['post_num'] = statistics[3]
            user['collection_num'] = statistics[4]
            user['log_num'] = statistics[5]

        _xsrf = ''.join(selector.xpath('//input[@name="_xsrf"]/@value').extract())
        hash_id = ''.join(selector.xpath('//div[@class="zm-profile-header-op-btns clearfix"]/button/@data-id').extract())

        yield user

        # questions
        num = int(user['ask_num']) if "ask_num" in user.keys() else 0
        page_num = num/20
        page_num += 1 if num%20 else 0
        for i in xrange(page_num):
            url=host+"/people/"+user["username"] + '/asks?page=%d' % (i+1)
            yield Request(url, callback=self.parse_ask)

        # answers
        num = int(user['answer_num']) if "answer_num" in user.keys()  else 0
        page_num = num / 20
        page_num += 1 if num % 20 else 0
        for i in xrange(page_num):
            yield Request(host + "/people/" + user["username"] + '/answers?page=%d' % (i + 1),
                          callback=self.parse_ans)

        self.user_names.append(user['username'])
        print 'NEW:%s' % user['username']

        num = int(followee_num) if followee_num else 0
        page_num = num/20
        page_num += 1 if num%20 else 0
        for i in xrange(page_num):
            params = json.dumps({"hash_id":hash_id,"order_by":"created","offset":i*20})
            payload = {"method":"next", "params": params, "_xsrf":_xsrf}
            yield Request("http://www.zhihu.com/node/ProfileFolloweesListV2?"+urlencode(payload), callback=self.parse_follow_url)

        num = int(follower_num) if follower_num else 0
        page_num = num/20
        page_num += 1 if num%20 else 0
        for i in xrange(page_num):
            params = json.dumps({"hash_id":hash_id,"order_by":"created","offset":i*20})
            payload = {"method":"next", "params": params, "_xsrf":_xsrf}
            yield Request("http://www.zhihu.com/node/ProfileFollowersListV2?"+urlencode(payload), callback=self.parse_follow_url)

    def parse_follow_url(self, response):
        selector = Selector(response)

        for link in selector.xpath('//div[@class="zm-list-content-medium"]/h2/a/@href').extract():
            #link  ===> http://www.zhihu.com/people/peng-leslie-97
            username_tmp = link.split('/')[-1]
            if username_tmp in self.user_names:
                print 'GET:' + '%s' % username_tmp
                continue

            yield Request(link+"/about", callback=self.parse_user)


    def parse_ask(self, response):
        selector = Selector(response)
        username = response.url.split('/')[-2]

        try:
            for record in selector.xpath(r"id('zh-profile-ask-list')/div"):
                view_num = record.xpath(r'span/div[1]/text()')[0].extract()
                title = record.xpath(r"div/h2/a/text()")[0].extract()
                answer_num = record.xpath(r"div/div/span[1]/following-sibling::text()")[0].extract().split(' ')[0].replace('\n','')
                follower_num = record.xpath(r"div/div/span[2]/following-sibling::text()")[0].extract().split(' ')[0].replace('\n','')
                url = host+record.xpath(r"div/h2/a/@href")[0].extract()
                print url
                yield ZhihuAskItem(_id=url,username = username,url = url, view_num = view_num, title = title, answer_num = answer_num, follower_num = follower_num)
        except Exception, e:
            open('error_pages/asks' + response.url.split('/')[-2]+'.html', 'w').write(response.body)
            print '='*10 + str(e)


    def parse_ans(self, response):
        selector = Selector(response)
        print response.url
        username = response.url.split('/')[-2]
        try:
            for record in selector.xpath(r"id('zh-profile-answer-list')/div"):
                ask_title = ''.join(record.xpath(r"h2/a/text()").extract())
                url = host + ''.join(record.xpath("h2/a/@href").extract()) # answer_url
                ask_url = url.split('/answer')[0]

                agree_num = ''.join(record.xpath('div/div[1]/a/text()').extract())
                summary = ''.join(record.xpath(r"div/div[4]/div/text()").extract()).replace("\n","").strip()  #TODO
                content = ''.join(record.xpath(r"div/div[4]/textarea/text()").extract()).replace("\n","").strip()

                comment_num = ''.join(record.xpath(r"div/div[5]/div/a[2]/text()").extract()) #'添加评论'或者'3 条评论'

                comment_num = comment_num.split(' ')[0] #取数字
                if comment_num.startswith(u'\n添加评论'):
                    comment_num = '0'

                yield ZhihuAnswerItem(_id=url,username = username,url = url, ask_title = ask_title, \
                                      ask_url = ask_url, agree_num = agree_num, summary = summary
                                      , content = content, comment_num = comment_num)
        except Exception, e:
            open('error_pages/answers_' + response.url.split('/')[-2]+'.html', 'w').write(response.body)
            print '='*10 + str(e)



