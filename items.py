# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Recipe(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    score = scrapy.Field()
    prep_time = scrapy.Field()
    total_time = scrapy.Field()
    url = scrapy.Field()
    rating = scrapy.Field()
    num_ratings = scrapy.Field()
    steps = scrapy.Field()
    primary_category = scrapy.Field()
    ingredients = scrapy.Field()
    categories = scrapy.Field()
    source = scrapy.Field()