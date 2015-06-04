# -*- coding: utf-8 -*-
import sys
import re
import scrapy
import time
from scrapy.spider import Spider
from scrapy.contrib.spiders import CrawlSpider, Rule
from datetime import datetime
from scrapy.http import Request, FormRequest, TextResponse
from scrapy.selector import Selector
from scrapy import log
from scrapy.contrib.linkextractors import LinkExtractor
from ..items import mmhItem
import urllib
baseLink = "https://hcreg.mmh.org.tw/"
def process_value(value) :
    return baseLink + value

class mmh(CrawlSpider):
    name = "mmh-hc"
    allowed_domains = ["org.tw"]
    start_urls = [
	"https://hcreg.mmh.org.tw/"
    ]
    rules =(
	Rule(LinkExtractor(restrict_xpaths='(//table[@id="tblDepts"]//tr//a)'), callback='parse_name',follow=True),
    )

    def parse_name(self, response):
	sel = Selector(response)
	nameList = sel.xpath('//table[@id="tblSch"]//a/@href').extract()
	for i in range(len(nameList)):
		nameUrl = baseLink + nameList[i]
		request = Request(nameUrl, callback = self.parse_table)
                yield request
    def parse_table(self, response):
	sel = Selector(response)
        items = []
	hospital = 'mmh - ' + (sel.xpath('//span[@id="TOP1_lblHospName"]//text()').extract())[0]
	dept = re.sub("\(.*",'',(sel.xpath('//tr[@class="title"]//span[@id="lblSch"]//text()').extract())[0])
	name = re.sub(".*\)(.+)\(.*",r'\1',(sel.xpath('//tr[@class="title"]//span[@id="lblSch"]//text()').extract())[0])
	outpatient = dept
	tableRow = sel.xpath('//table[@id="tblSch"]//tr')
	for t in range(3,len(tableRow),1):
		tableCol = tableRow[t].xpath('.//td')
		for c in range(len(tableCol)):
			info = tableCol[c].xpath('.//text()').extract()
			if info != []:
				item= mmhItem()
				date = info[0]
				m = re.match("([0-9]*)/([0-9]*)",date)
                                if len(m.group(1)) == 1 :
                                        mon = '0' + m.group(1)
                                else:
                                        mon = m.group(1)
                                if len(m.group(2)) == 1 :
                                        day = '0' + m.group(2)
                                else:
                                        day = m.group(2)
                                date = unicode(datetime.now().strftime("%Y")) + mon + day
				try :
					full=info[1]
					if full == u"滿號":
						full = u"預約額滿 - 初診可掛"
					elif full == u"停診":
						full = u"停診"
					else :
						full = u"可掛號"
				except Exception as e:
					full = u"可掛號"
				if c%3 == 1:
					itime = 'morning'
				elif c%3 == 2:
					itime = 'afternoon'
				else:
					itime = 'night'
                                item['hospital']=hospital
                                item['dept']=dept
                                item['outpatient']=outpatient
                                item['name']=name
                                item['full']=full
                                item['time']=itime
                                item['date']=date
                                item['link']='NA'
                                item['crawlTime'] = unicode(datetime.now().strftime("%Y%m%d %H:%M"))
				items.append(item)
				#print "Col : " + str(c) + " Row : " + str(t) + " hospital : " + hospital + " dept : " + dept + " outpatient : " + outpatient +  " name : " + name + " full : " + full + " date : " + date + " time : " + itime
	return items
