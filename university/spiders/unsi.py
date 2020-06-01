# -*- coding: utf-8 -*-
import scrapy
from university.items import UniversityItem


class UnsiSpider(scrapy.Spider):
    name = 'unsi'
    allowed_domains = ['www.usnews.com']
    start_urls = ['https://www.usnews.com/education/best-global-universities/rankings']

    # 请求start_urls，得到的结果进行解析
    def parse(self, response):
        # 获取国家的名字和每个大学对应的链接
        urls = response.xpath('//div[@class="sep"]/div[@class="block unwrap"]/h2/a/@href').extract()
        countrys = response.xpath('//div[@class="t-taut"]/span[1]/text()').extract()

        # 通过循环，提取出本页所有的大学链接，国家
        for i in range(len(countrys)):
            # 通过循环，把链接和国家名称，传递到解析详情页的部分
            meta={
                'country':countrys[i],
            }

            yield scrapy.Request(url=urls[i],callback=self.parse_each,meta=meta)
        # 请求大学列表的下一页
        # 经过查看网页，一共有151页
        for num in range(2,152):
            next_url = 'https://www.usnews.com/education/best-global-universities/rankings?page='+str(num)
            yield scrapy.Request(url=next_url,callback=self.parse_next_page)

    # 解析2-151页列表
    def parse_next_page(self,response):
        # 与上面的功能相同
        urls = response.xpath('//div[@class="sep"]/div[@class="block unwrap"]/h2/a/@href').extract()
        countrys = response.xpath('//div[@class="t-taut"]/span[1]/text()').extract()

        for i in range(len(countrys)):
            meta = {
                'country': countrys[i],
            }

            yield scrapy.Request(url=urls[i], callback=self.parse_each, meta=meta)

    # 解析每一个学校的详情页，提取出信息
    def parse_each(self,response):
        # 创建item对象
        item = UniversityItem()
        print('parse_each')

        # 在详情页中，获取提取需要解析的信息
        country = response.xpath('//div[@class="directory-data"][1]/div[last()]/text()').extract_first().strip()
        loc = response.xpath('//div[@class="directory-data"][1]/div[last()-1]/text()').extract_first().strip()
        name = response.xpath('//h1[@class="h-biggest"]/text()').extract_first()
        score = response.xpath('//div[@id="directoryPageSection-indicator-rankings"]/div[@class="t-slack sep"][1]/div[@class="right t-strong"]/text()').extract_first().replace(' ','').replace('\n','')
        Global_research_reputation = response.xpath('//div[@id="directoryPageSection-indicator-rankings"]/div[@class="t-slack sep"][2]/div[@class="right t-strong"]/span/span/text()').extract_first().replace(' ','').replace('#','')

        # 把信息存储到item对象中
        item['country'] = country
        item['loc'] = loc
        item['name'] = name
        item['Global_score'] = score
        item['Global_research_reputation'] = Global_research_reputation
        # 把item对象返回给引擎，继续后续的存储操作
        yield item
