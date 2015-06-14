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
from ..items import vghtcItem
import urllib
weekNum = 0

class vghtc(CrawlSpider):
    name = "vghtc"
    allowed_domains = ["gov.tw"]
    start_urls = [
	"http://register.vghtc.gov.tw/register/listSection.jsp"
    ]
    rules =(
	Rule(LinkExtractor(restrict_xpaths='(//a)'), callback='parse_table',follow=True),
    )
    def parse_table(self, response):
	sel = Selector(response)
        items = []
	hospital = 'vghtc'
	outpatient = sel.xpath('//div//b/text()').extract()
	if outpatient != [] :
		outpatient = outpatient[0]
	else:
		#print "Error in this url : " + response.url
		return
	outpatient = re.sub(" -.*",'',outpatient)
	dept =outpatient
	tableNum = sel.xpath('//table')
	for t in range(1,len(tableNum),1):
		name = ''
		tableRow = tableNum[t].xpath('.//tr')
		try : 
			name = (tableNum[t].xpath('.//tr[1]//td[1]//b/text()').extract())[0].strip(' \t\n\r')
		except :
			next
		if not re.search(u"醫師",name): next
		name = re.sub(u"醫師",'',name)
		for r in range(2,len(tableRow),1):
			if len(tableRow[r].xpath('.//td')) != 7 : 
				#print "Skip : " + str(r) + " outpatient : " + outpatient
				break
			date = (tableRow[r].xpath('.//td[2]/text()').extract())[0]
			date = re.sub('[.]','',date)	
			itime = (tableRow[r].xpath('.//td[4]/text()').extract())[0]
                        if itime == u'上午':
                        	itime = 'morning'
                        elif itime == u'下午':
                                itime = 'afternoon'
                        elif itime == u'夜間':
                                itime = 'night'
			full = (tableRow[r].xpath('.//td[6]/text()').extract())[0]
			note = (tableRow[r].xpath('.//td[7]/font/text()').extract())[0].strip(' \t\n\r')
			full = note + full
			item= vghtcItem()
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
			#print "note : " + note + " hospital : " + hospital + " dept : " + dept + " outpatient : " + outpatient +  " name : " + name + " full : " + full + " date : " + date + " time : " + itime
	return items
