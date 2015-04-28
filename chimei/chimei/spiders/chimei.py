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
from ..items import chimeiItem
import urllib
baseLink = 'http://www.chimei.org.tw/opdschedule/'

def process_value(value) :
    #print value
    return baseLink + value

class chimei(CrawlSpider):
    name = "chimei"
    allowed_domains = ["org.tw"]
    start_urls = [
	"http://www.chimei.org.tw/opdschedule/top.aspx?ihosp=10&lang=CH"
	#"http://www.chimei.org.tw/opdschedule/register.aspx?idept=731&ihosp=10&lang=CH&ndept=%E4%B8%80%E8%88%AC%E5%85%A7%E7%A7%91"
	#"http://www.chimei.org.tw/opdschedule/register.aspx?ihosp=10&lang=CH&idept=767&ndept=%E7%9D%A1%E7%9C%A0%E4%B8%AD%E5%BF%83"
	#"http://www.chimei.org.tw/opdschedule/register.aspx?ihosp=10&lang=CH&idept=773&ndept=%25E7%2589%2599%25E7%25A7%2591"
	#"http://www.chimei.org.tw/opdschedule/register.aspx?ihosp=10&lang=CH&idept=777&ndept=%E7%9A%AE%E8%86%9A%E7%A7%91"
    ]
    rules =(
	Rule(LinkExtractor(restrict_xpaths='//a[@target="main_s"]'), callback='parse_table',follow=True),
    )

    def parse_table(self, response):
    #def parse(self, response):
	sel = Selector(response)
        items = []
	text = unicode("上午",'utf-8')
	xpath = "//table[.//*[contains(.,'%s')]]" % (text)
        tables = sel.xpath(xpath)
	tableNum = len(tables)
	text = unicode("班別",'utf-8')
	xpath =  "//table[.//*[contains(.,'%s')]][1]//td//span[contains(@id,'lb_w')]" % (text)
	dateList = sel.xpath(xpath)
	dateNum = len(dateList)
	tableRow = 3
	tableColumn = 7
	#print "tableNum:" + str(tableNum) + "/" + "dateNum" + str(dateNum) 
	for t in range(tableNum):
            #print "table = " + str(t)
            for r in range(tableRow):
		period = ''
		table = t + 1
		#print "row:" + str(r)
		tt = unicode("上午",'utf-8')
		if r == 0:
			time = 'morning'
			period = unicode("上午",'utf-8')
		elif r ==1:
			time = 'afternoon'
			period = unicode("下午",'utf-8')
		else :
			time = 'night'
			period = unicode("夜間",'utf-8')
		xpath = "((//table[.//*[contains(.,'%s')]])[%d]//tr[contains(.,'%s')]//tr)//td" % (tt , table,period)
		#print xpath
		#xpath = "(((//table[.//*[contains(.,'%s')]])[%d]//tr[contains(.,'%s')]//tr)//td//a[@target='_parent'])" % (tt , table,period)
		#xpath = "(((//table[.//*[contains(.,'%s')]])[%d]//tr[1])[%d]//td//a[@target='_parent'])[%d]//text()" % (tt , table,row,col)
		data = sel.xpath(xpath)
		#full = u'可掛號'
		deptOutpatient = (sel.xpath("//span[@id='lbl_ndept']//text()").extract())[0]
		outpatient = re.sub(".*-\s*",'',deptOutpatient)
		dept = re.sub("-\s*.*",'',deptOutpatient)
		#print outpatient
		try:
			outpatient=outpatient.encode('ASCII')
			outpatient=urllib.unquote(outpatient).decode('utf8')
                except Exception as e:
			pass
		#print period
		#print str(len(data))
		if data != []:
			for d in range(len(data)):
				idata = d + 1
				# get detailed outpatient
				rth = d/8 + 1
				temp = "((//table[.//*[contains(.,'%s')]])[%d]//tr[contains(.,'%s')]//tr/td[1])[%d]" % (tt , table,period,rth)
				#print d
				#print rth
				#print temp
				detailedOutpatient = (sel.xpath(temp).xpath('.//text()').extract())[0]
				detailedOutpatient = re.sub(".*\s",'',detailedOutpatient)
				#print temp
				#print detailedOutpatient
				ss = unicode("班別",'utf-8')
				day = (d%7) + 2
				xpath = "(//table[.//*[contains(.,'%s')]][%d])//td[%d]//text()" % (ss,table,day)
				date = (sel.xpath(xpath).extract())[0]
				#print date
				name = ''
				textLine =  data[d].xpath(".//a//text()").extract()
				textLineNum = len(textLine)
				#print textLineNum
				#print textLine
				item=chimeiItem()
				item['name'] = ''
				for l in range(textLineNum):
					if l == 0:
						#print textLine[l]
						if re.match("^\s*$",textLine[l],re.UNICODE):
							break
						else:
							title = data[d].xpath(".//a[@target='_parent']/@title").extract()
							if title != [] :
								m = re.search(u"現已掛到(.*)號",title[0])
								if m:
									item['full']= m.group(1)
									item['link'] = baseLink + '/' + (data[d].xpath(".//a[@target='_parent']/@href").extract())[0]
								else:	
									if re.search(u"尚未開放掛號",title[0]):
										item['full']  = title[0]
									else:
										if re.search(u"已超過當診掛號時間",title[0]):
											item['full'] = u'已過掛號時間'
										else:
											item['full'] = 'NA'
									#else:	
									#	item['full'] = title[0]
									item['link']='NA'
							else:
								item['full'] = 'NA'
								item['link']='NA'
							item['hospital'] = 'chimei-' + dept 
							item['dept'] = outpatient
							item['outpatient'] = detailedOutpatient 
							item['name'] = textLine[l]
							item['time'] = time
							m = re.search(r"(.*)/(.*)/(.*)",date)
							if m:
								year = m.group(1)
								mon = m.group(2)
								day = m.group(3)
								if len(m.group(2)) <2:
									mon = '0' + m.group(2)
								if len(m.group(3)) <2:
									day = '0' + m.group(3)
								item['date'] = year + mon + day
							item['crawlTime'] = unicode(datetime.now().strftime("%Y%m%d %H:%M"))
					else:
					#elif l==1:
						#print textLine[l]
						textLine[l]=re.sub("^\s*\(.*\)\s*",'',textLine[l])
						if item['full'] == 'NA':
							#	item['full'] = u'可掛號'
							if re.search(u"預約(.*)額滿",textLine[l]):
								item['full']  = u'名額已滿'
							else:
								item['full']  = textLine[l]	
						else:
							#if not re.match("^\s*\(.*",textLine[l]):
							if not re.match("^\s*$",textLine[l]):
								item['full']=item['full'] + "/" + textLine[l]
					#else:
					#	print "warning"
				if item['name']!='':
					#print item['name']
					items.append(item)
	return items
