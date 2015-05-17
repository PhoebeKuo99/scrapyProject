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
from ..items import skhItem
import urllib
baseLink = "https://regis.skh.org.tw/regisn/"
def filter_links(self, links):
	filteredLinks = []
        for link in links:
            if re.match("https://regis.skh.org.tw/regisn/registdetail.aspx",link.url):
                filteredLinks.append(link)
        	return filteredLinks

class skh(CrawlSpider):
    name = "skh"
    allowed_domains = ["org.tw"]
    start_urls = [
	"https://regis.skh.org.tw/regisn/WebForm1.aspx"
    ]
    rules =(
	#Rule(LinkExtractor(restrict_xpaths='//a[contains(@href,"doct.aspx")]'),callback='parse_dep',follow=True,),
	#Rule(LinkExtractor(restrict_xpaths='(//table//table)[3]//a'),cb_kwargs={'dept':u'內科'},callback='parse_dep',follow=True,),
	#Rule(LinkExtractor(restrict_xpaths='(//table//table)[5]//a'),cb_kwargs={'dept':u'外科'},callback='parse_dep',follow=True,),
	Rule(LinkExtractor(restrict_xpaths='(//table//table)[7]//a'),cb_kwargs={'dept':u'牙科'},callback='parse_dep',follow=True,),
	#Rule(LinkExtractor(restrict_xpaths='(//table//table)[9]//a'),cb_kwargs={'dept':u'其他專科'},callback='parse_dep',follow=True,),
	#Rule(LinkExtractor(restrict_xpaths='(//table[10])//a'),cb_kwargs={'dept':10}, callback='parse_table',follow=True,process_links="filter_links",),
    )

    def parse_dep(self, response,**kwargs):
	sel = Selector(response)
	print "deptUrl : " + response.url
	nameList = sel.xpath("//table//a/@href").extract()
	for i in range(len(nameList)):
		if re.match("registdetail.aspx",nameList[i]):
			nameLink = baseLink + nameList[i]	
			request = Request(nameLink,callback=self.parse_table)
			request.meta['dept'] = kwargs.get('dept')
			yield request
    def parse_table(self, response):
	items = []
	#print "------" + response.url
	dept = response.meta['dept']
	#if kwargs.get('dept') == 4 :
	#	dept = u'內科'
	#elif kwargs.get('dept') == 6 :
	#	dept = u'外科'
	#elif kwargs.get('dept') == 8 :
	#	dept = u'牙科'
	#elif kwargs.get('dept') == 10 :
	#	dept = u'其他專科'
	
	sel = Selector(response)
	rows = sel.xpath('//table[@id="Table1"]//tr')
	rowLen = len(rows) + 1
	#print rowLen
	for t in range(2,rowLen,1):
		item = skhItem()
		item['link'] = 'NA'
		item['hospital'] = 'skh'
		item['dept'] = dept 
		item['date'] = sel.xpath('(//table[@id="Table1"]//tr)[%d]/td[1]//text()' % (t)).extract()[0]
		print "t : " + str(t) + " " + item['date']
		year = int(re.match(r"(\d*)(\d\d)(\d\d)",item['date']).group(1)) + 1911
		mon = re.match(r"(\d*)(\d\d)(\d\d)",item['date']).group(2)
		day = re.match(r"(\d*)(\d\d)(\d\d)",item['date']).group(3)
		item['date'] = str(year) + mon + day
		item['time'] = sel.xpath('(//table[@id="Table1"]//tr)[%d]/td[2]//text()' % (t)).extract()[0]
		if item['time'] == u'上午':
			item['time'] = 'morning'
		elif item['time'] == u'下午':
			item['time'] = 'afternoon'
		else:
			item['time'] = 'night'
		if dept == u'牙科':
			item['outpatient'] = sel.xpath('(//table[@id="Table1"]//tr)[%d]//td[4]//text()' % (t)).extract()[0]
		else :
			item['outpatient'] = sel.xpath('(//table[@id="Table1"]//tr)[%d]//td[3]//text()' % (t)).extract()[0]
		item['full'] = sel.xpath('(//table[@id="Table1"]//tr)[%d]/td[6]//text()' % (t)).extract()[0]
		item['name'] = sel.xpath('(//table[@id="Table1"]//tr)[%d]/td[7]//text()' % (t)).extract()[0]
		item['crawlTime'] = unicode(datetime.now().strftime("%Y%m%d %H:%M"))
		if re.match("^\s*$",item['full']):
				item['full'] = u'可掛號'
		else:
			if re.match("^\d*$",item['full']):
				item['link'] = baseLink + sel.xpath('(//table[@id="Table1"]//tr)[%d]/td[1]/a/@href' % (t)).extract()[0]
			elif re.match(u'額滿',item['full']):
				item['full'] = u'預約額滿'
		print "dept : " + dept + " date : " + item['date'] + ' time : ' + item['time'] + ' outpatient : ' + item['outpatient'] + ' full : ' + item['full'] + ' name : ' + item['name'] + ' full : ' + item['full'] + ' link : ' + item['link']
		items.append(item)
	return items
