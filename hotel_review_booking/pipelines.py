# -*- coding: utf-8 -*-

from data.hotel_review_booking.hotel_review_booking.hotel_review_booking.items import HotelReviewBookingItem
import codecs
import pandas as pd
import os


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class HotelReviewBookingPipeline(object):
    def __init__(self):
        # replace data dir with your owns.
        self.base_data_path = r'/data/hotel_review_booking/datas/'

        self.file_name = r'hotels.csv'
        self.pd_file = pd.DataFrame(
            columns={"target", "city_name", "date", 'score', 'overall_comment', 'positive_comment', 'negative_comment'})

    # def create_pd(self,name_pd):



    def process_item(self, item, spider):
        
        str_city_name = item['city_name']

        str_target = item['target']
        str_date = item['date']
        str_score = item['score']
        str_overall_comment = item['overall_comment']
        str_positive_comment = item['positive_comment']
        str_negative_comment = item['negative_comment']
        
        new_record = {"target": str_target,
                      "date": str_date,
                      "city_name": str_city_name,
                      "score": str_score,
                      "overall_comment": str_overall_comment,
                      "positive_comment": str_positive_comment,
                      "negative_comment": str_negative_comment}
        self.pd_file = self.pd_file.append(new_record, ignore_index=True)

        return item

    def close_spider(self, spider):
        print(len(self.pd_file))
        self.pd_file = self.pd_file.reset_index(drop=True)
        self.pd_file.to_csv(self.base_data_path + self.file_name, sep="\t", index=False, header=True, encoding="utf-8")
