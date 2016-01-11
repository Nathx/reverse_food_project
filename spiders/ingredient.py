# -*- coding: utf-8 -*-
import scrapy
import json


class IngredientSpider(scrapy.Spider):
	name = "ingredient"
	allowed_domains = ["food.com"]
	start_urls = (
    	'http://www.food.com/about/',
	)

	def parse(self, response):
		ingredients = self.fetch_ingredients(response)
		for food in ingredients:
			yield food
		next_link = response.xpath(
			'/html/head/link[@rel="next"]/@href'
			).extract()
		if next_link:
			yield scrapy.Request(next_link[0], callback=self.parse)

	def fetch_ingredients(self, response):
		
		js_script = response.xpath(
			"//script[not(@src)][contains(text(), 'searchResults')]/text()"
			).extract()[0]
		# extract javascript dictionary and convert
		in_text = "var searchResults = "
		out_text = "};"
		# try:
		bound_up = js_script.find(in_text) + len(in_text)
		len_text = js_script[bound_up:].find(out_text) + 1
		js_dict = json.loads(js_script[bound_up:bound_up+len_text])
		# except:
		# 	raise TypeError("Couldn't find searchResults matching usual pattern on this page.")

		try:
			assert js_dict["response"]["parameters"]["recordType"] == "Ingredient", "This page is not about ingredients."
		except:
			raise AssertionError("This page is not about ingredients.")

		ingredients = js_dict["response"]["results"]
		for ing in ingredients:
			try:
				del ing["description"]
			except:
				pass
		return ingredients