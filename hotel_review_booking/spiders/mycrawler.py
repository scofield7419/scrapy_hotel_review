import re
import scrapy
from scrapy.selector import Selector
from scrapy.http import Request
from data.hotel_review_booking.hotel_review_booking.hotel_review_booking.items import HotelReviewBookingItem
import re


class MyCrawler(scrapy.Spider):
    name = 'hotel_review_booking'
    allowd_domain = 'booking.com'
    pure_base_url = 'https://www.booking.com'

    base_url = 'https://www.booking.com/reviews/'
    
    road_map = {
        "beijing":
            {'url': 'cn/city/beijing.zh-cn.html?',
             'pages': 20,
             },
        "shanghai":
            {'url': 'cn/city/shanghai.zh-cn.html?',
             'pages': 27,
             },
        "tokyo":
            {'url': 'jp/city/tokyo.zh-cn.html?',
             'pages': 26,
             },
        "hong-kong":
            {'url': 'hk/city/hong-kong.zh-cn.html?',
             'pages': 10,
             },
        "bangkok":
            {'url': 'th/city/bangkok.zh-cn.html?',
             'pages': 27,
             },
        "seoul":
            {'url': 'kr/city/seoul.zh-cn.html?',
             'pages': 20,
             },
        "osaka":
            {'url': 'jp/city/osaka.zh-cn.html?',
             'pages': 14,
             },
        "melaka":
            {'url': 'my/city/melaka.zh-cn.html?',
             'pages': 6,
             },
        "singapore":
            {'url': 'sg/city/singapore.zh-cn.html?',
             'pages': 16,
             },
        "t-ai-pei":
            {'url': 'tw/city/t-ai-pei.zh-cn.html?',
             'pages': 18,
             },
        "suzhou":
            {'url': 'cn/city/suzhou.zh-cn.html?',
             'pages': 5,
             },
        "kuala-lumpur":
            {'url': 'my/city/kuala-lumpur.zh-cn.html?',
             'pages': 18,
             },
        "paris":
            {'url': 'fr/city/paris.zh-cn.html?',
             'pages': 53,
             },
        "chiang-mai":
            {'url': 'th/city/chiang-mai.zh-cn.html?',
             'pages': 22,
             },
        "london":
            {'url': 'gb/city/london.zh-cn.html?',
             'pages': 33,
             },
        "new-york":
            {'url': 'us/city/new-york.zh-cn.html?',
             'pages': 14,
             },
        "boracay":
            {'url': 'ph/city/boracay.zh-cn.html?',
             'pages': 7,
             },
        "guangzhou":
            {'url': 'cn/city/guangzhou.zh-cn.html?',
             'pages': 19,
             },
        "kyoto":
            {'url': 'jp/city/kyoto.zh-cn.html?',
             'pages': 12,
             },
        "los-angeles":
            {'url': 'us/city/los-angeles.zh-cn.html?',
             'pages': 12,
             }

    }

    hotel_list_offset_str_1 = 'offset='
    hotel_list_offset_str_3 = '&'

    count = 1

    pattern = r'(\d{4})年(\d{1,2})月(\d{1,2})日'
    pattern_compiled = re.compile(pattern)


    def start_requests(self):
        # max_pages = 27  # 20
        for k, v in self.road_map.items():
            city_name = k
            url = self.road_map[city_name]['url']
            pages = self.road_map[city_name]['pages']
            for index in range(0, pages):
                if index == 0:
                    offs = ''
                else:
                    offs = self.hotel_list_offset_str_1 + str(index * 30) + self.hotel_list_offset_str_3
                page_url = self.base_url + url + offs
                yield Request(page_url, callback=self.get_one_hotel_review_lists, meta={'city_name': city_name})

    def get_one_hotel_review_lists(self, response):
        # response.css('li').xpath('@src').extract()
        content_list = response.xpath("//ul[@class='rlp-main-hotels__container']").extract()
        for content_item in content_list:
            content_item = Selector(text=content_item)
            content_list_1 = content_item.xpath("//li[@class='rlp-main-hotel-review__review_link']").extract()
            for one_item in content_list_1:
                content_url = Selector(text=one_item).xpath("//a/@href").extract()
                # print(content_url)
                content_url = self.pure_base_url + content_url[0]
                # print(content_url)
                yield Request(content_url, callback=self.get_one_review_list,
                              meta={'page': "first", 'city_name': response.meta['city_name']})

    def get_one_review_list(self, response):
        content_list = response.xpath("//li[@class='review_item clearfix ']").extract()

        target_hotel = response.xpath(
            "//div[@class='standalone_reviews_hotel_info ']").extract()
        target_hotel = Selector(text=target_hotel[0]).xpath(
            "//a[@class='standalone_header_hotel_link']/text()").extract()
        target_hotel = target_hotel[0]
        # print(target_hotel)

        for content_item in content_list:
            yield self.get_one_review_entity(content_item, target_hotel, response.meta['city_name'])

        next_page_content = response.xpath(
            "//div[@id='review_list_page_container']/div[@class='review_list_pagination']/p[@class='page_link review_next_page']").extract()
        # next_page_content = Selector(text=next_page_content[0]).xpath(
        #     "//div[@id='review_list_page_container'/div[@class='review_list_pagination'/p[@class='page_link review_next_page']]]").extract()
        nextpaer = Selector(text=next_page_content[0]).xpath("//a/@href").extract()
        # print(nextpaer)

        # next = response.meta['page']
        # if next != None:
        #     print(next)

        if len(nextpaer) != 0:
            next_url = nextpaer[0]
            next_url = self.pure_base_url + next_url
            # print(next_url)
            yield Request(next_url, callback=self.get_one_review_list,
                          meta={'page': "next", 'city_name': response.meta['city_name']})

    def get_one_review_entity(self, content_item, target_hotel, city_name):
        # print(content_item)
        content_item = Selector(text=content_item)
        item = HotelReviewBookingItem()

        str_target = target_hotel
        # print(str_target)

        str_date = content_item.xpath("//p[@class='review_item_date']/text()").extract()
        str_date = str_date[0].replace("\n", "").replace("\r\n", "").replace("\r", "").replace("\t", "")
        matched_date = re.search(self.pattern_compiled, str_date)
        str_date = matched_date.group(0)
        # print(date_1)

        str_score = content_item.xpath("//span[@class='review-score-badge']/text()").extract()
        str_score = str_score[0].replace("\n", "").replace("\r\n", "").replace("\r", "").replace("\t", "")
        # print(str_score)

        str_overall_comment = content_item.xpath(
            "//div[@class='review_item_header_content\n']/span[@itemprop='name']/text()").extract()
        if len(str_overall_comment) == 0:
            str_overall_comment = ''
        else:
            str_overall_comment = str_overall_comment[0].replace("\n", "").replace("\r\n", "").replace("\r",
                                                                                                       "").replace("\t",
                                                                                                                   "")
        # print(str_overall_comment)

        str_positive_comment = content_item.xpath(
            "//p[@class='review_pos']/span[@itemprop='reviewBody']/text()").extract()
        if len(str_positive_comment) == 0:
            str_positive_comment = ''
        else:
            str_positive_comment = str_positive_comment[0].replace("\n", "").replace("\r\n", "").replace("\r",
                                                                                                         "").replace(
                "\t", "")
        # print(str_positive_comment)

        str_negative_comment = content_item.xpath(
            "//p[@class='review_neg']/span[@itemprop='reviewBody']/text()").extract()
        if len(str_negative_comment) == 0:
            str_negative_comment = ''
        else:
            str_negative_comment = str_negative_comment[0].replace("\n", "").replace("\r\n", "").replace("\r",
                                                                                                         "").replace(
                "\t", "")
        # print(str_negative_comment)

        print(self.count)
        self.count += 1
        '''
        打印顺序如下：
            . ??
            北京新世界酒店：2016年2月14日9.2房间很大，设备新，泳池舒适，员工友好房间很大，设备新，泳池舒适，员工友好
        这说明，每产生一个item都会及时送入到pipeline被处理。
        '''

        item['target'] = str_target
        item['date'] = str_date
        item['score'] = str_score
        item['city_name'] = city_name
        item['overall_comment'] = str_overall_comment
        item['positive_comment'] = str_positive_comment
        item['negative_comment'] = str_negative_comment

        # line = str_target + str_date + str_score + str_overall_comment + str_positive_comment + str_negative_comment
        # print(line)

        return item
