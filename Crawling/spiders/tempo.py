import scrapy
import re
from datetime import datetime, timedelta
from Crawling.items import CrawlingItem
import time
from random import randrange
import locale

class DetikSpider(scrapy.Spider):
    name = 'tempo'
    # allowed_domains = ['indeks.kompas.com']
    url = 'https://www.tempo.co/indeks/'
    date_start = '2003/07/10'
    date_finish = '2003/07/31'
    day = 0
    dtstart = datetime.strptime(date_start, '%Y/%m/%d')
    dtfinish = datetime.strptime(date_finish, '%Y/%m/%d')
    init_idx = 1
    start_urls = [url + date_start]

    def parse(self, response):
        # Dapatkan semua link yang ada pada halaman tersebut
        # #indeks-container > article:nth-child(1) > div > div.media__text > h3 > a
        # links_formated = response.xpath("//div[contains(concat(' ', normalize-space(@class), ' '), ' clearfix ') and contains(concat(' ', normalize-space(@class), ' '), ' wrapper ')]/a[2]/@href").extract()
        links_formated = response.xpath('//*[@id="article"]/div[1]/section/ul/li/div/div/a[2]/@href').extract()
        # links_formated = [s + "?page=all" for s in links]
        # links_formated = []
        # Jika ada link berita (berarti bukan halaman kosong)
        if (len(links_formated) > 0) :
            yield from response.follow_all(links_formated, self.parse_berita)
        if ((self.dtstart + timedelta(days=self.day)).date() < self.dtfinish.date()):
            self.day = self.day + 1
            self.dtsstart = self.dtstart + timedelta(days=self.day)
            self.date_start = self.dtsstart.strftime('%Y/%m/%d')
            # print('ok1' + next_day)
            start_nextDay = self.url + self.date_start
            self.init_idx = 1
            # print('ok2' + start_nextDay)
            print('waiting ' + str(120) + ' second to continue')
            time.sleep(120)
            print('ini adalah print start next day' + start_nextDay)
            yield scrapy.Request(start_nextDay, callback=self.parse)
        
        # Jika tidak ada link berita, maka artinya halaman kosong dan proses crawling selesai
        # else:
        #     # return
        #     if ((self.dtstart + timedelta(days=self.day)).date() < self.dtfinish.date()):
        #         self.day = self.day + 1
        #         self.dtsstart = self.dtstart + timedelta(days=self.day)
        #         self.date_start = self.dtsstart.strftime('%Y/%m/%d')
        #         # print('ok1' + next_day)
        #         start_nextDay = self.url + self.date_start
        #         self.init_idx = 1
        #         # print('ok2' + start_nextDay)
        #         print('ini adalah print start next day' + start_nextDay)
        #         yield scrapy.Request(start_nextDay, callback=self.parse)
    
    def parse_berita(self, response):
        # Simpan data dari berita yang berhasil dibuka
        title = response.xpath('//*[@id="article"]/div[1]/div/article/h1/text()').extract_first()
        content = ''.join(response.xpath('//*[@id="isi"]/p/text()').extract())
        if not content:
          content = ''.join(response.xpath('//*[@id="isi"]//text()').extract())
        tags = response.css('.tags').xpath('li/a/text()').extract()
        dts =  re.search('\d{1,2}?\s\w{3,9}?\s\d{4}? \d{2}:\d{2}', response.xpath('//*[@id="date"]/text()').extract_first()).group()
        # dt = datetime.strptime(dts, '%d/%m/%y %H:%M')
        locale.setlocale(locale.LC_TIME, "id_ID")
        dt = datetime.strptime(dts, '%d %B %Y %H:%M')
        dtms = int(round(dt.timestamp() * 1000))
        item = CrawlingItem()
        item['title'] = title
        item['content'] = content
        item['tags'] = tags
        item['datetime'] = dtms
        yield item
        # {
        #     'title' : title,
        #     'content' : content,
        #     'tags' : tags,
        #     'datetime' : dtms
        #     # 'keywords': response.xpath("/html/head/meta[@name='keywords']/@content").extract_first(),
        #     # 'title': response.css("head > title::text").extract_first(),
        #     # 'createdate': response.xpath("/html/head/meta[@name='createdate']/@content").extract_first(),
        #     # 'publishdate': response.xpath("/html/head/meta[@name='publishdate']/@content").extract_first(),
        #     # 'author': response.xpath("/html/head/meta[@name='author']/@content").extract_first(),
        #     # 'description': response.xpath("/html/head/meta[@property='og:description']/@content").extract_first(),
        #     # 'kota': response.css("#detikdetailtext > b::text").extract_first(),
        #     # 'text': response.css("#detikdetailtext").extract_first()
        # }
    # start_urls = ['http://quotes.toscrape.com/']

    # def parse(self, response):
    #     author_page_links = response.css('.author + a')
    #     yield from response.follow_all(author_page_links, self.parse_author)

    #     pagination_links = response.css('li.next a')
    #     yield from response.follow_all(pagination_links, self.parse)

    # def parse_author(self, response):
    #     def extract_with_css(query):
    #         return response.css(query).get(default='').strip()

    #     yield {
    #         'name': extract_with_css('h3.author-title::text'),
    #         'birthdate': extract_with_css('.author-born-date::text'),
    #         'bio': extract_with_css('.author-description::text'),
    #     }