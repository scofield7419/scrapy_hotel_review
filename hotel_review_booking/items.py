# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HotelReviewBookingItem(scrapy.Item):
    # define the fields for your item here like:
    city_name = scrapy.Field()
    target = scrapy.Field()
    score = scrapy.Field()
    date = scrapy.Field()
    overall_comment = scrapy.Field()
    positive_comment = scrapy.Field()
    negative_comment = scrapy.Field()
