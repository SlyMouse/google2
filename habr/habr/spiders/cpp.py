# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from habr.items import HabrItem

class CppSpider(CrawlSpider):
    name = 'cpp'
    allowed_domains = ['habr.com']
    start_urls = ['https://habr.com/ru/hub/cpp']
    limit = 10
    scraped_count = 0

    rules = (Rule(LinkExtractor(allow=(), restrict_xpaths=('//*[@id="next_page"]',)), callback="parse_item",
                  follow=True, process_request="proc_req"),)

    def parse_item(self, response):
        item_links = response.css('article > h2 > a::attr(href)').extract()
        for item_link in item_links:
            yield scrapy.Request(item_link, callback=self.parse_detail_page)

    def parse_detail_page(self, response):
        title = response.css('h1 > span::text').extract()[0].strip()

        article_text = ""

        article_texts = response.css('div.post__body.post__body_full > div::text').extract()
        for block in article_texts:
            if block != '\r\n':
                article_text += block

        if article_text == "":
            article_texts = response.css('div.post__body.post__body_full > div > p::text').extract()
            for block in article_texts:
                if block != '\r\n':
                    article_text += block

        item = HabrItem()
        item['title'] = title
        item['article_text'] = article_text
        item['url'] = response.url
        yield item

    def proc_req(self, request):
        if self.scraped_count < self.limit:
            self.scraped_count += 1
            return request
