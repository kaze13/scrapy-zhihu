#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class ZhihuUserItem(Item):
    _id = Field()
    url = Field()
    img = Field()
    username = Field()
    nickname = Field()
    location = Field()
    industry = Field()
    sex = Field()
    jobs = Field()
    educations = Field()
    description = Field()
    sinaweibo = Field()
    tencentweibo = Field()

    followee_num = Field()
    follower_num = Field()

    ask_num = Field()
    answer_num = Field()
    post_num = Field()
    collection_num = Field()
    log_num = Field()

    agree_num = Field()
    thank_num = Field()
    fav_num = Field()
    share_num = Field()

    view_num = Field()
    update_time = Field()


class ZhihuAskItem(Item):
    _id = Field()
    username = Field()
    url = Field()
    view_num = Field()
    title = Field()
    comment_count = Field()
    recent_active_time = Field()
    answer_num = Field()
    follower_num = Field()


class ZhihuAnswerItem(Item):
    _id = Field()
    username = Field()
    url = Field()
    ask_title = Field()
    ask_url = Field()
    agree_num = Field()
    summary = Field()
    content = Field()
    comment_num = Field()
    last_update_time = Field()


class ZhihuFolloweesItem(Item):
    _id = Field()
    username = Field()
    followees = Field()


class ZhihuFollowersItem(Item):
    _id = Field()
    username = Field()
    followers = Field()


