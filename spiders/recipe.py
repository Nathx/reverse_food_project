# -*- coding: utf-8 -*-
import scrapy
import time
import re
import json
import sys
import pandas as pd
from urlparse import urlparse, parse_qs
from pymongo import MongoClient
from scrapy.conf import settings

from reverse_food_project.items import Recipe


class RecipeSpider(scrapy.Spider):
	name = "recipe"
	allowed_domains = ["food.com"]

	def start_requests(self):
		"""Extract requests from ingredients.json"""

		with open('json/ingredient.json') as jsfile:
			ingredients = [json.loads(ing)['title'] for ing in jsfile.readlines()]

		restart = True

		if restart:

			restart_list = self.fetch_checkpoint('json/recipe.json')
			for ing, pn in restart_list.iteritems():
				url = "http://www.food.com/services/mobile/fdc/search/all?searchTerm=" + ing + "&pn=" + str(pn)
				yield scrapy.Request(url, callback=self.parse)
			ingredients = [ing for ing in set(ingredients) if ing not in restart_list.keys()]
			ingredients.sort()


		for ing in ingredients:
			url = "http://www.food.com/services/mobile/fdc/search/all?searchTerm=" + ing
			yield scrapy.Request(url, callback=self.parse)


	def fetch_checkpoint(self, path):
		"""Get last page number checked for each ingredient.
		"""
		connection = MongoClient(
			settings['MONGODB_SERVER'],
			settings['MONGODB_PORT']
		)
		db = connection[settings['MONGODB_DB']]
		collection = db[settings['MONGODB_COLLECTION']]
		urls = collection.distinct('source')
		checkpoint = {}

		for url in urls:
		    parsed = urlparse(url)
		    params = parse_qs(parsed.query)
		    title = params['searchTerm'][0].replace('%20', ' ')
		    if title.find('%') > -1:
		    	print title
		    try:
		        pn = int(params['pn'][0])
		    except:
		        pn = 1

		    if not (title in checkpoint.keys()):
		        checkpoint[title] = pn
		    elif pn > checkpoint[title]:
		        checkpoint[title] = pn

		return checkpoint


	def parse(self, response):

		recipes = response.xpath('//results[record_type="Recipe"]')

		for rec in recipes:

			item = Recipe()
			item['id'] = rec.xpath('recipe_id/text()').extract()[0]
			item['title'] = rec.xpath('main_title/text()').extract()[0]
			item['score'] = rec.xpath('score/text()').extract()[0]
			item['prep_time'] = rec.xpath('recipe_preptime/text()').extract()[0]
			item['total_time'] = rec.xpath('recipe_totaltime/text()').extract()[0]
			item['url'] = rec.xpath('record_url/text()').extract()[0]
			item['rating'] = rec.xpath('main_rating/text()').extract()[0]
			item['num_ratings'] = rec.xpath('main_num_ratings/text()').extract()[0]
			item['steps'] = rec.xpath('num_steps/text()').extract()[0]
			try:
				item['primary_category'] = rec.xpath('primary_category_name/text()').extract()[0]
			except:
				pass
			item['source'] = response.url

			request = scrapy.Request(item['url'], callback=self.parse_recipe)
			request.meta['item'] = item
			yield request

		total_recipes = int(response.xpath('/fdcSearchResults/response/totalResultsCount/text()').extract()[0])
		offset = int(response.xpath('/fdcSearchResults/response/parameters/offset/text()').extract()[0])
		if offset + 10 < total_recipes:
			parsed = urlparse(response.url)
			params = parse_qs(parsed.query)
			try:
				pn = int(params['pn'][0]) + 1
				url = re.sub('pn=\d{1,6}', 'pn=' + str(pn), response.url)
			except:
				pn = 2
				url = response.url + "&pn=" + str(pn)
			yield scrapy.Request(url, callback=self.parse)

	def parse_recipe(self, response):
		"""Get list of ingredients and tags on recipe page.
		"""
		item = response.meta['item']
		ing_container = response.xpath('//li[@itemprop="ingredients"]')
		ingredients = []
		for ing in ing_container:
			if ing.xpath('a'):
				ingredients.append(ing.xpath('a/@href').extract()[0])
			else:
				ingredients.append(ing.xpath('@data-ingredient').extract()[0])

		item['ingredients'] = ingredients
		item['categories'] = response.xpath('//meta[@name="sailthru.tags"]/@content').extract()[0].split(',')
		yield item
