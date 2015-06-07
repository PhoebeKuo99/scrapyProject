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
from ..items import ntuhItem
import urllib
weekNum = 0
baseLink = "https://reg.ntuh.gov.tw/webadministration/"
def process_value(value) :
    #print value
    return value

class ntuh(CrawlSpider):
    name = "ntuh"
    allowed_domains = ["gov.tw"]
    start_urls = [
	"https://reg.ntuh.gov.tw/webadministration/ClinicTable.aspx",
	"https://reg.ntuh.gov.tw/webadministration/ClinicTableY0.aspx", ##雲林
	"https://reg.ntuh.gov.tw/webadministration/ClinicTableT4.aspx", ###新竹
	"https://reg.ntuh.gov.tw/WebAdministration/ClinicTableT5.aspx",##竹東
	"https://reg.ntuh.gov.tw/WebAdministration/ClinicTableT2.aspx" ###北護
    ]
    rules =(
	Rule(LinkExtractor(restrict_xpaths='(//table[contains(@id,"DeptTable")]//a[contains(@href,"DoctorTable.aspx")])',process_value=process_value), callback='parse_name',follow=True),
    )
    def parse_name(self, response):
	global weekNum
	sel = Selector(response)
	#week2Url = re.sub("week=1","week=2",response.url)
	#print week2Url
	nameList = sel.xpath('//table[contains(@id,"Table")]//a/@href')
	#weekNum = weekNum + 1
	for i in range(len(nameList)):
		nameUrl = baseLink + nameList[i].extract()
		request = Request(nameUrl, callback = self.parse_table)
                yield request
	#if weekNum <2 :
	#	request = Request(week2Url, callback = self.parse_name)
        #        yield request
    def parse_table(self, response):
	sel = Selector(response)
        items = []
	tableRow = sel.xpath('//table[@id="DataTable"]//tr')
	name = (sel.xpath('//table[@id="Table1"]//text()').extract())[3]
	for t in range(1,len(tableRow),1):
		tableCol = tableRow[t].xpath('.//td')
		fullList = tableCol[1].xpath('.//text()').extract()
		full = ' '.join(fullList)
		note = (tableCol[9].xpath('.//text()').extract())[0]
		note2 = 'NA'
		try : 
			note2 = (tableCol[0].xpath('.//text()').extract())[0]
		except Exception as e:
			pass
		if re.search(u"名額已滿",full):
			full = u"預約額滿"
			if note2 != 'NA':
				full = full + " - " + note2
			if note == u"可":
				full = full + u" - 現場可掛"
		else:
			if note2 != 'NA':
				full = note2
		if re.search(u"[.].*掛號.*[.]",full):
			full = u"可掛號"
		date = (tableCol[2].xpath('.//text()').extract())[0]
                m = re.match("(.*)\.(.*)\.(.*)",date)
                if len(m.group(2)) == 1 :
                	mon = '0' + m.group(2)
                else:
                	mon = m.group(1)
                if len(m.group(3)) == 1 :
                	day = '0' + m.group(3)
                else:
                	day = m.group(3)
                date = m.group(1) + mon + day
		itime = re.sub(u"星期.",'',(tableCol[2].xpath('.//text()').extract())[1])
                if re.search(u'上午',itime):
                        itime = 'morning'
                elif re.search(u'下午',itime):
                        itime = 'afternoon'
                else:
                        itime = 'night'
		hospital = 'ntuh - '+ (tableCol[3].xpath('.//text()').extract())[0]
		dept = (tableCol[5].xpath('.//text()').extract())[0]
		outpatient = (tableCol[6].xpath('.//text()').extract())[0]
		if outpatient == u"普通門診" or outpatient == u"初診" :
			outpatient = dept
		item= ntuhItem()
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
		print " hospital : " + hospital + " dept : " + dept + " outpatient : " + outpatient +  " name : " + name + " full : " + full + " date : " + date + " time : " + itime
	return items
