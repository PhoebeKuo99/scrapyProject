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
from ..items import cgmhItem
import urllib
baseLink = 'https://register.cgmh.org.tw/'

def process_value(value) :
    print value
    return baseLink + value

class cgmh(CrawlSpider):
    name = "cgmh"
    allowed_domains = ["org.tw"]
    start_urls = [
    	"https://register.cgmh.org.tw/Department.aspx?dpt=2",
	"https://register.cgmh.org.tw/Department.aspx?dpt=E",
	"https://register.cgmh.org.tw/Department.aspx?dpt=1",
	"https://register.cgmh.org.tw/Department.aspx?dpt=3",
	"https://register.cgmh.org.tw/Department.aspx?dpt=5",
	"https://register.cgmh.org.tw/Department.aspx?dpt=M",
	"https://register.cgmh.org.tw/Department.aspx?dpt=6",
	"https://register.cgmh.org.tw/Department.aspx?dpt=8",
	"https://register.cgmh.org.tw/Department.aspx?dpt=T"
    ]
    rules =(
	Rule(LinkExtractor(restrict_xpaths='(//div[contains(@id,"ctl00_ContentPlaceHolder1_Pane")]//table[not(contains(@class,"font-department"))]//a[contains(@href,"RMS")])'), callback='parse_table',follow=True),
    )

    def parse_table(self, response):
    #def parse(self, response):
	sel = Selector(response)
        items = []
	tableRow = sel.xpath('//table[@class="fontTimeTb"]//tr')
	for t in range(2,len(tableRow),1):
		tableCol = tableRow[t].xpath('.//td')
		for c in range(len(tableCol)):
			if c == 0 :
				date = (tableCol[c].xpath('.//text()').extract())[0]
				m = re.match(u"([0-9]*)年([0-9]*)月([0-9]*)日",date)
				year = m.group(1)
				if len(m.group(2)) == 1 :
					mon = '0' + m.group(2)
				else:
					mon = m.group(2)
				if len(m.group(3)) == 1 :
					day = '0' + m.group(3)
				else:
					day = m.group(3)
				date = year + mon + day
			else :
				if c == 1 :
					itime = 'morning'
				elif c == 2:
					itime = 'afternoon'
				else :
					itime = 'night'
				nameList = tableCol[c].xpath('.//text()').extract()
				nameList = [elem for elem in nameList if elem != '&nbsp'] 
				nameInfo = ' '.join(nameList)
				#print "$$$ - " +nameInfo + " - $$$"
				nameNum = re.split("[0-9]+",nameInfo)
				for n in range(len(nameNum)):
					if not re.search("[\S]+",nameNum[n]) or nameNum[n]=="":
						continue
					name = re.sub("\(.*",'',nameNum[n]) 
					item= cgmhItem()
					if re.search(u"額滿",nameNum[n]):
						full = u"預約額滿"
					elif re.search(u"停診",nameNum[n]):
						full = u"停診"
					else :
						full = u"可掛號"
					if re.search(u"初診",nameNum[n]):
						full = full + u" - 初診可掛"
					outpatient = (sel.xpath('//table[@class="title"]//text()').extract())[2]
					hospital = (re.split(" ",outpatient))[0]
					dept = (re.split(" ",outpatient))[1]
					outpatient = dept
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
					print "hospital : " + hospital + " dept : " + dept + " outpatient : " + outpatient +  " name : " + name + " full : " + full + " date : " + date + " time : " + itime
	return items
