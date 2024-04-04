# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class UnivspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class UniversityItem(scrapy.Item):
    id = scrapy.Field()
    university_name = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()