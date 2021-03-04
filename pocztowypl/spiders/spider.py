import scrapy

from scrapy.loader import ItemLoader
from ..items import PocztowyplItem
from itemloaders.processors import TakeFirst


class PocztowyplSpider(scrapy.Spider):
	name = 'pocztowypl'
	start_urls = ['https://www.pocztowy.pl/indywidualni/aktualnosci/']

	def parse(self, response):
		post_links = response.xpath('//div[@class="news p"]')
		for post in post_links:
			url = post.xpath('./div[@class="news-content-box"]/a/@href').get()
			date = post.xpath('./div[@class="news-date-box"]//text()').getall()
			date = [p.strip() for p in date]
			date = ' '.join(date).strip()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		next_page = response.xpath('//div[@class="right-page-checker-arrow"]/a/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//div[@class="wrapper"]/div[@class="headline"]//text()').getall()
		title = [p.strip() for p in title]
		title = ' '.join(title).strip()
		description = response.xpath('//div[@class="container text-block"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=PocztowyplItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
