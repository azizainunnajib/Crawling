import scrapy
import re
from datetime import datetime, timedelta
from Crawling.items import CrawlingItem

class DetikSpider(scrapy.Spider):
    name = 'kompas'
    # allowed_domains = ['indeks.kompas.com']
    url = 'https://indeks.kompas.com/?site=all&date='
    date_start = '2020-06-06'
    date_finish = '2020-06-07'
    day = 0
    dtstart = datetime.strptime(date_start, '%Y-%m-%d')
    dtfinish = datetime.strptime(date_finish, '%Y-%m-%d')
    init_idx = 1
    start_urls = [url + date_start]

    def parse(self, response):
        # Dapatkan semua link yang ada pada halaman tersebut
        # #indeks-container > article:nth-child(1) > div > div.media__text > h3 > a
        links = response.css('.article__link').xpath('./@href').getall()
        links_formated = [s + "?page=all" for s in links]
        # links_formated = []
        # Jika ada link berita (berarti bukan halaman kosong)
        if (len(links_formated) > 0) :
            yield from response.follow_all(links_formated, self.parse_berita)
            # for link in obj:
                # yield{
                #     'a': link.xpath('@href'),
                #     'b': link.xpath('text()')
                # }
                # Buat scrapy.Request baru untuk membuka link berita tersebut
                # Gunakan fungsi parse_berita untuk memproses response
                
                # yield from scrapy.Request(url=link, callback=self.parse_berita)
                # scrapy.Request(url=berita_url, callback=self.parse_berita)
            
            # Cek halaman aktif saat ini
            # current_page = response.css("body > div.container > div.content > div.lf_content.boxlr.w870 > div.center > div > a.selected::text").extract_first()
            # # Buat URL untuk scrapping halaman selanjutnya
            # next_page_url = response.urljoin(self.start_urls[0] + 'all/' + str(int(current_page) + 1) + '?date=' + self.date)
            self.init_idx = self.init_idx + 1
            print('ini adalah print index' + str(self.init_idx))
            next_page_url = self.url + self.date_start + '&page=' + str(self.init_idx)
            print('ini adalah print index' + next_page_url)
            yield scrapy.Request(next_page_url, callback=self.parse)
        
        # Jika tidak ada link berita, maka artinya halaman kosong dan proses crawling selesai
        else:
            # return
            print('ini ada di else if')
            if ((self.dtstart + timedelta(days=self.day)).date() < self.dtfinish.date()):
                print('ini ada di while')
                self.day = self.day + 1
                self.dtsstart = self.dtstart + timedelta(days=self.day)
                print('ok')
                self.date_start = self.dtsstart.strftime('%Y-%m-%d')
                # print('ok1' + next_day)
                start_nextDay = self.url + self.date_start
                self.init_idx = 1
                # print('ok2' + start_nextDay)
                print('ini adalah print start next day' + start_nextDay)
                yield scrapy.Request(start_nextDay, callback=self.parse)
    
    def parse_berita(self, response):
        # Simpan data dari berita yang berhasil dibuka
        title = response.css('.read__title').xpath('text()').extract_first()
        content = ''.join(response.css('.read__content').xpath('.//p//text()').extract())
        tags = response.css('.tag__article__link').xpath('text()').getall()
        dts = re.search('\d{2}/\d{2}/\d{4}, \d{2}:\d{2}', response.css('.read__time').xpath('text()').extract_first()).group()
        # dt = datetime.strptime(dts, '%d/%m/%y %H:%M')
        dt = datetime.strptime(dts, '%d/%m/%Y, %H:%M')
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