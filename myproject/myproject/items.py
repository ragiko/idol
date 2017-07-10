# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MyprojectItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class Headline(scrapy.Item): 
    """
    ニュースのヘッドラインを表すItem。 
    """
    url = scrapy.Field() 
    html = scrapy.Field()

    def __repr__(self):
        """
        ログへの出力時に長くなり過ぎないよう、contentを省略する。
        """

        p = Headline(self)  # このPageを複製したPageを得る。
        if len(p['html']) > 50:
            p['html'] = p['html'][:50] + '...'  # 100文字より長い場合は省略する。

        return super(Headline, p).__repr__()  # 複製したPageの文字列表現を返す。
