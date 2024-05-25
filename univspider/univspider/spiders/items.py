import scrapy

class UniversityItem(scrapy.Item):
    url = scrapy.Field()
    content = scrapy.Field()