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
from ..items import cmuhItem
from selenium.common.exceptions import NoAlertPresentException
from selenium import webdriver
import urllib
js = """
window.alert = function(message) {
lastAlert = message;
}
"""
class cmuh(CrawlSpider):
    name = "cmuh"
    start_urls = [
	"http://www.cmuh.cmu.edu.tw/web/guest/onlineappointment"
	
    ]
    def __init__(self,**kwargs):
        #self.driver=webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs')
	self.driver=webdriver.Firefox()

    def parse(self, response):
	self.driver.get(response.url)
	btn = self.driver.find_element_by_xpath('//div[@class="fright1 firstD"]')
	btn.click()
	outpatientList = self.driver.find_elements_by_xpath('//div[contains(@class,"dep_")]//a')
	hospital = 'cmuh'
	nameUrl  = []
	outpatient = ''
	dept = ''
	for i in range(len(outpatientList)):
	#for i in range(130,135,1):
	#	print "pa :"
	#	print len(self.driver.window_handles)
		try:
			dept = outpatientList[i].text
			#print dept
			if  re.search(u"健康檢查預約",dept) :
				#print "skip"
				next
			else:
				outpatientList[i].click()
			#time.sleep(5)
			if len(self.driver.window_handles) == 1:
				next
			else:
				#print len(self.driver.window_handles)
			self.driver.switch_to_window(self.driver.window_handles[1])
			time.sleep(5)
			outpatientUrl = self.driver.current_url
			nameUrlList = self.driver.find_elements_by_xpath('.//a')
			if len(nameUrlList) == 0 : 
				self.driver.close()
				self.driver.switch_to_window(self.driver.window_handles[0])	
				time.sleep(5)
				#print outpatientUrl
				#print "no name found"
				next
			outpatient = (self.driver.find_elements_by_xpath('//table[@class="sch"]/caption'))[0].text
			outpatient = re.sub("\(.*",'',outpatient)
			#print outpatient
			for j in range(len(nameUrlList)):
			#for j in range(1):
			#for j in range(40,42,1):
				nameUrlList[j].click()
				#time.sleep(5)
				#print "nameLoop"
				#print len(self.driver.window_handles)
				#if len(self.driver.window_handles) != 3:
				#	print self.driver.current_url
					#self.driver.close()
				time.sleep(5)
				self.driver.switch_to_window(self.driver.window_handles[2])
				self.driver.get(self.driver.current_url)
				try :
					url = self.driver.find_element_by_xpath('//iframe[@id="frameid"]').get_attribute('src')
        				request = Request(url, callback = self.parse_table)
					request.meta['outpatient'] = outpatient
					request.meta['dept'] = dept
        				yield request
                        		#nameUrl.append(url)
					#print "this" + url 
				except Exception as e:	
					#print "Error with this url : "
					#print self.driver.current_url
				self.driver.close()
				self.driver.switch_to_window(self.driver.window_handles[1])
				time.sleep(5)
				nameUrlList = self.driver.find_elements_by_xpath('.//a')
			#print nameUrlList[j].text
			self.driver.close()
			time.sleep(5)
		except Exception as e:
			pass
		self.driver.switch_to_window(self.driver.window_handles[0])	
		time.sleep(5)
		outpatientList = self.driver.find_elements_by_xpath('//div[contains(@class,"dep_")]//a')
	self.driver.quit()
	#for i in range(len(nameUrl)):
        	#request = Request(nameUrl[i], callback = self.parse_table)
		#request.meta['outpatient'] = outpatient
		#request.meta['dept'] = dept
        	#yield request
    def parse_table(self, response):
        items = []
        sel = Selector(response)
	boxList = sel.xpath('(//td[@class="schBox"])')
	outpatient = response.meta['outpatient']
	dept = response.meta['dept']
	for b in range(len(boxList)):
		objList = boxList[b].xpath('./div')
		time = ' '.join((boxList[b].xpath('.//preceding::td[contains(@class,"timeSlot")]'))[-1].xpath('.//text()').extract())
		name = ' '.join((sel.xpath('.//div[@class="step1"]'))[0].xpath('.//text()').extract())
		m = re.search(u"請點選 *(\S+) *.*",name)
		name = m.group(1)
		for o in range(len(objList)):
			info = '  '.join(objList[o].xpath('.//text()').extract())
			m = re.search(u".*([0-9]+).*人",info)
			if m:
				full = m.group(1)
			else:
				if re.search(u"已額滿",info):
					full = u"預約額滿"
				else:
					full = info	
			m = re.search(u"([0-9]*/[0-9]*/[0-9]*)",info)
			if m:
				date = re.sub("/",'',(m.group(1)))
                        if re.search(u"上午",time):
                        	itime = 'morning'
                        elif re.search(u"下午",time):
                                itime = 'afternoon'
                        else:
                                itime = 'night'
			item= cmuhItem()
                        item['hospital']="cmuh"
                        item['dept']=dept
                        item['outpatient']=outpatient
                        item['name']=name
                        item['full']=full
                        item['time']=itime
                        item['date']=date
                        item['link']='NA'
                        item['crawlTime'] = unicode(datetime.now().strftime("%Y%m%d %H:%M"))
                        items.append(item)
                        #print " dept : " + dept + " outpatient : " + outpatient +  " name : " + name + " full : " + full + " date : " + date + " time : " + itime
        return items
