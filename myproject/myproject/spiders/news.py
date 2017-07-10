# -*- coding: utf-8 -*-
import scrapy
from myproject.items import Headline

class NewsSpider(scrapy.Spider):
    name = 'news'
    allowed_domains = ["www.keyakizaka46.com"]
    # クロールを開始するURLのリスト。
    start_urls = (
        'http://www.keyakizaka46.com/s/k46o/diary/member/list?ima=0000',
    )

    def parse(self, response):
        """
        はてなブックマークの新着エントリーページをパースする。
        """

        # 個別のWebページへのリンクをたどる。
        for url in response.css('article a::attr("href")').extract():
            # parse_page() メソッドをコールバック関数として指定する。
            yield scrapy.Request(response.urljoin(url), callback=self.parse_page)

        # of=の値が2桁である間のみ「次の20件」のリンクをたどる（最大5ページ目まで）。
        url_more = response.css('.pager li:last-child a::attr("href")').extract_first()
        if url_more:
            # url_moreの値は /entrylist で始まる相対URLなので、
            # response.urljoin()メソッドを使って絶対URLに変換する。
            # コールバック関数を指定していないので、レスポンスはデフォルト値である
            # parse()メソッドで処理される。
            yield scrapy.Request(response.urljoin(url_more))

    def parse_page(self, response):
        """
        トピックスのページからタイトルと本文を抜き出す。
        """
        item = Headline()
        item['url'] = response.url
        item['html'] = response.text
        yield item

