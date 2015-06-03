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
from ..items import femhItem
import urllib
baseLink = "https://hos.femh.org.tw/newfemh/webregs/"
class femh(CrawlSpider):
    name = "femh"
    allowed_domains = ["org.tw"]
    start_urls = [
	"https://hos.femh.org.tw/newfemh/webregs/Sector.aspx"
    ]

    def parse(self, response):
	sel = Selector(response)
	deptList = sel.xpath('//table[@id="ctl00_FunctionContent_gvSecDr"]//tr//td/@onclick').extract()
	for i in range(len(deptList)):
	#for i in range(1):
		m = re.search("javascript:location.href='(.*)';", deptList[i])
		if m :
			deptLink = baseLink + m.group(1)
		request = Request(deptLink,callback=self.parse_dept)
		yield request
    def parse_dept(self, response):
	sel = Selector(response)
	weekList = sel.xpath("//input[@class='btn3']").extract()
	for i in range(len(weekList)):
	#for i in range(1):
		weekUrl = response.url + '&mtypes=' + str(i)
		request = Request(weekUrl,callback=self.parse_table)
		yield request
    def parse_table(self, response):
	items = []
	if re.search("id=040[0-9]",response.url):
		dept = u'心臟血管醫學中心'
	elif re.search("id=02[0,1][0-9]",response.url):
		dept = u'內科'
	elif re.search("id=028[0-9]",response.url):
		dept = u'外科'
	elif re.search("id=02[2,3][0-9]",response.url):
		dept = u'小兒科/婦產科'
	else :
		dept = u'其他專科'
	sel = Selector(response)
	rows = sel.xpath('//table[@id="ctl00_FunctionContent_gvSec"]//tr')
	rowLen = len(rows)
	ptime = ''
	for t in range(rowLen):
		rowStart = t + 2
		dateList = sel.xpath('(//table[@id="ctl00_FunctionContent_gvSec"]//tr)[1]//td')
		nameList = sel.xpath('((//table[@id="ctl00_FunctionContent_gvSec"]//tr)[%d]/td)' % (rowStart))
		for iname in range(2,len(nameList),1):
			#print iname
			infoList = nameList[iname].xpath('.//text()').extract()
			if infoList != [] and len(infoList) != 1 :
				if not re.search(u"停診",infoList[0]) and (not re.search(u"停診",infoList[1])):
					item=femhItem()
					item['dept'] = dept
					item['hospital'] = 'femh'
					try:
						link = nameList[iname].xpath('.//@onclick').extract()[0]
					except Exception as e:
						link = 'NA'
					item['link'] = baseLink + re.sub(r"^.*href='(.*)';",r'\1',link)
					item['name'] = infoList[0]
					if infoList[1] != u"網路掛號" :
						item['full'] = re.sub(r'[^0-9]*([0-9]+).*',r'\1',infoList[4])
						if infoList[5] == u'--預約額滿':
							item['full'] = u'預約額滿' + item['full']
					else :
						item['full'] = re.sub(r'[^0-9]*([0-9]+).*',r'\1',infoList[3])
						if infoList[4] == u'--預約額滿':
							item['full'] = u'預約額滿' + item['full']
					item['outpatient'] = sel.xpath('//span[@id="ctl00_FunctionContent_Label2"]//text()').extract()[1]
					item['date'] = re.sub("[/]",'',dateList[iname].xpath('.//text()').extract()[0])
					item['crawlTime'] = unicode(datetime.now().strftime("%Y%m%d %H:%M"))
					itime = sel.xpath('((//table[@id="ctl00_FunctionContent_gvSec"]//tr)[%d]/td[1]//text())' % (rowStart)).extract()
					if itime[0] == u'早上':
						item['time'] = 'morning'
						ptime = 'morning'
					elif itime[0] == u'下午':
						item['time'] = 'afternoon'
						ptime = 'afternoon'
					elif itime[0] == u'晚上':
						item['time'] = 'night'
						ptime = 'night'
					else:
						item['time'] = ptime
					#print "dept : " + dept + " date : " + item['date'] + ' time : ' + item['time'] + ' outpatient : ' + item['outpatient'] + ' full : ' + item['full'] + ' name : ' + item['name'] + ' link : ' + item['link']
					items.append(item)
	return items
