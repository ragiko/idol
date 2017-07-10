import re
import lxml.html
from pymongo import MongoClient
import readability
import MySQLdb
import json

def get_content(html):
    """
    HTMLの文字列から (タイトル, 本文) のタプルを取得する。
    """
    document = readability.Document(html)
    content_html = document.summary()
    # HTMLタグを除去して本文のテキストのみを取得する。
    content_text = lxml.html.fromstring(content_html).text_content().strip()
    return content_text

def normalize_spaces(s):
    """
    連続する空白を1つのスペースに置き換え、前後の空白を削除した新しい文字列を取得する。
    """
    return re.sub(r'\s+', ' ', s).strip()

def scrape(url):
    """
    ワーカーで実行するタスク。
    """
    client = MongoClient('localhost', 27017)  # ローカルホストのMongoDBに接続する。
    html_collection = client.book.items # scrapingデータベースのebook_htmlsコレクションを得る。
    
    page_html = html_collection.find_one({'url': url})  # MongoDBからurlに該当するデータを探す。
    html = page_html['html']
    root = lxml.html.fromstring(html)

    # MySQLサーバーに接続し、コネクションを取得する。
    # ユーザー名とパスワードを指定してscrapingデータベースを使用する。接続に使用する文字コードはutf8mb4とする。
    conn = MySQLdb.connect(db='scraping', user='root', passwd='', charset='utf8mb4')
    
    c = conn.cursor()  # カーソルを取得する。
    # execute()メソッドでSQL文を実行する。
    c.execute('''
    CREATE TABLE IF NOT EXISTS page (
        id int AUTO_INCREMENT,
        url text,
        title text,
        img text,
        time datetime,
        meta json DEFAULT NULL,
        PRIMARY KEY (`id`)
    )
    ''')
        
    meta_json =  json.dumps({
        'content_text': get_content(html), # 記事の本文
        'imgs': [img.get('src') for img in root.cssselect('.box-main > article img')], # 記事内の画像
        'name': root.cssselect('p.name > a')[0].text
    })

    # パラメーターが辞書の場合、プレースホルダーは %(名前)s で指定する。
    c.execute('''
    INSERT INTO page (url, title, img, time, meta) VALUES 
    (
        %(url)s,
        %(title)s,
        %(img)s,
        %(time)s,
        %(meta)s
    )
    ''',
        {
            'url': url,  # URL
            'title': normalize_spaces(root.cssselect('.box-ttl > h3')[0].text_content()),  # タイトル
            'img': root.cssselect('meta[property="og:image"]')[0].get('content'),
            'time': normalize_spaces(root.cssselect('.box-bottom li')[0].text) + ":00",
            'meta': meta_json,
        }
    )
    
    conn.commit()  # 変更をコミット（保存）する。
    conn.close()  # コネクションを閉じる。

if __name__ == "__main__":
    scrape('http://www.keyakizaka46.com/s/k46o/diary/detail/10657?ima=0000&cd=member')
