import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import BaaderItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class ArchivSpider(scrapy.Spider):
    name = 'archiv'
    page = 1
    start_urls = [f'https://www.baaderbank.de/Investor-Relations/Presseinformationen-Archiv-232?page={page}']
    ITEM_PIPELINES = {
        'archiv.pipelines.BaaderPipeline': 300,

    }

    def parse(self, response):
        post_links = response.xpath('//div[@class="event-title"]//a[@target="_self"]/@href').getall()
        yield from response.follow_all(post_links, self.parse_post)

        next_page = 'https://www.baaderbank.de/Investor-Relations/Presseinformationen-Archiv-232?page={}'
        if not len(post_links) < 20:
            self.page += 1
            yield response.follow(next_page.format(self.page), self.parse)

    def parse_post(self, response):
        date = response.xpath('//span[@class="news_top_date"]/text()').get().split(' / ')[0]
        title = response.xpath('(//h2)[2]/text()').get()
        content = response.xpath('//div[@class="break-word news_main"]//text()').getall()
        content = [p.strip() for p in content if p.strip()]
        content = re.sub(pattern, "", ' '.join(content))

        item = ItemLoader(item=BaaderItem(), response=response)
        item.default_output_processor = TakeFirst()

        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('date', date)

        yield item.load_item()

