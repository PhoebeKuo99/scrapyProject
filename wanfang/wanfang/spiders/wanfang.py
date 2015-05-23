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
from ..items import wanfangItem
from selenium import webdriver
import urllib
baseLink = "http://www.wanfang.gov.tw/"

#def process_value(value) :
#    print value
#    return baseLink + value

class wanfang(CrawlSpider):
    name = "wanfang"
    allowed_domains = ["gov.tw"]
    def __init__(self,hospitalUrl=None,*args,**kwargs):
        super(wanfang, self).__init__(*args,**kwargs)
        if hospitalUrl:
                self.start_urls = ['%s' % hospitalUrl]
        else:
                self.start_urls = [
        		"http://www.wanfang.gov.tw/p3_register_e2.aspx?depttype=M",
			"http://www.wanfang.gov.tw/p3_register_e2.aspx?depttype=S",
			"http://www.wanfang.gov.tw/p3_register_e2.aspx?depttype=O",
			"http://www.wanfang.gov.tw/p3_register_e2.aspx?depttype=T",
			"http://www.wanfang.gov.tw/p3_register_e2.aspx?depttype=A"
                ]
        self.driver=webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs')
        #self.driver=webdriver.Firefox()

    def parse(self, response):
	self.driver.get(response.url)
	deptList = self.driver.find_elements_by_xpath('//div[@class="p3_tab_top"]//a')
	deptLen = len(deptList)
	items = []
	deptLinks = []
	for i in range(deptLen):
	#for i in range(1):
		deptList[i].click()
		deptLinks.append(self.driver.current_url)
		self.driver.get(response.url)
		deptList = self.driver.find_elements_by_xpath('//div[@class="p3_tab_top"]//a')
	for i in range(len(deptLinks)):
	#for i in range(3,4,1):
		self.driver.get(deptLinks[i])
		time.sleep(5)
		dept = self.driver.find_elements_by_xpath('//div[@class="p3_time_title"]/span')
		info = re.split('/',dept[0].text)
		dept = info[0]
		outpatient = info[1]
		nameList = self.driver.find_elements_by_xpath('//span[@class="p3_time_line"]')
		dateList = self.driver.find_elements_by_xpath('//div[@class="p3_time_date"]')
		pageList = self.driver.find_elements_by_xpath('//span[@id="ContentPlaceHolder1_dp_Result"]//input') 
		for j in range(1,len(pageList)-2,1):
		#for j in range(1):
			if i != 2: # if j==2, it's the first page, do not click
				pageList[j].click()
				nameList = self.driver.find_elements_by_xpath('//span[@class="p3_time_line"]')
				dateList = self.driver.find_elements_by_xpath('//div[@class="p3_time_date"]')
				pageList = self.driver.find_elements_by_xpath('//span[@id="ContentPlaceHolder1_dp_Result"]//input') 
			for iname in range(len(nameList)):
				try:

					infos = nameList[iname].text	
					infoList = infos.split('\n')
					for info in range(len(infoList)):
						#print infoList[info]
						if re.search("\([0-9]+\)",infoList[info]):
							try :	
								full = infoList[info+1]
							except Exception as e:
								full = u'可掛號'
							if re.match(r"^\s*$",full):
								full = u'可掛號'
							item = wanfangItem()
							item['full']=full
							item['name'] = re.sub("\(.*\)",'',infoList[info])
							item['dept']=dept
							item['outpatient']=outpatient
							item['link']='NA'
							item['hospital']='wanfang'
							item['crawlTime'] = unicode(datetime.now().strftime("%Y%m%d %H:%M"))
							if iname%3 == 0:
								item['time'] = 'morning'
							elif iname%3 == 1:
								item['time'] = 'afternoon'
							else:
								item['time'] = 'night'
							date = dateList[iname/3].text
							m = re.match(u"(.*)年(.*)月(.*)日.*",re.sub('\n','',date))
							if m :
								year = str(int(m.group(1))+1911)
								mon = m.group(2)
								day = m.group(3)
								item['date'] = year + mon + day
							items.append(item)
							#print "dept : " + item['dept'] + " date : " + item['date'] + ' time : ' + item['time'] + ' outpatient : ' + item['outpatient'] + ' full : ' + item['full'] + ' name : ' + item['name'] + ' link : ' + item['link']
				except Exception as e:
					pass
	self.driver.quit()				
	return items

 
