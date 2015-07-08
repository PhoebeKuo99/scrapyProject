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
from ..items import cshItem
from selenium import webdriver
import urllib


class csh(CrawlSpider):
    name = "csh"
    allowed_domains = ["org.tw"]
    start_urls = [
        "http://www.csh.org.tw/register/Register.aspx"

    ]
    def __init__(self,**kwargs):
        self.driver=webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs')
        #self.driver=webdriver.Firefox()

    def parse(self, response):
	self.driver.get(response.url)
	items = []
	hospitalList = self.driver.find_elements_by_xpath('//tr//td//input[contains(@id,"_ContentPlaceHolder1_rblZone_")]')
	hospitalLen = len(hospitalList)
	for i in range(hospitalLen):
		hospitalList[i].click()
		time.sleep(5)
		deptList = self.driver.find_elements_by_xpath('//a[contains(@id,"_ContentPlaceHolder1_DataList")]')
		deptLen = len(deptList)
		for j in range(deptLen):
			dept = deptList[j].text
			#print dept
			deptList[j].click()
			time.sleep(5)
			outpatientList = self.driver.find_elements_by_xpath('//a[contains(@id,"_ContentPlaceHolder1_DataList")]')
			outpatientListLen = len(outpatientList)
			for k in range(outpatientListLen):
			#for k in range(1):
				outpatient = outpatientList[k].text
				outpatientList[k].click()
				time.sleep(5)
				weekList = self.driver.find_elements_by_xpath('//a[contains(@id,"ctl00_ContentPlaceHolder1_lbWeek")]')
				for w in range(len(weekList)):
					weekList[w].click()
					time.sleep(5)
					trList = self.driver.find_elements_by_xpath('(//table[@class="schedule"])')
					if len(self.driver.find_elements_by_xpath('(//table[@class="schedule"])//table')) == 0 :
						break
					for tr in range(1,len(trList),1):
						tdList = trList[tr].find_elements_by_xpath('.//table')
						for td in range(len(tdList)):
							nameList = tdList[td].find_elements_by_xpath('.//a')
							for z in range(len(nameList)):
								#print nameList[z].text
								if re.search(u"額滿",nameList[z].text):
									full = u"預約額滿"
								else:
									full = u"尚可掛號"
								date = self.driver.find_element_by_xpath('(//table[@class="schedule"])[%d]//th' %(tr+1))
								if td == 0:
									itime = 'morning'
								elif td == 1:
									itime = 'afternoon'
								else:
									itime = 'night'
										
								item = cshItem()
								item['full']=full
								item['name']= re.sub("[([ \n].*",'',nameList[z].text)
								item['dept']=dept
								item['outpatient']=outpatient
								item['link']='NA'
								if i == 0 :
									item['hospital']='csh-大慶'
								else :
									item['hospital']='csh-中興'
								item['crawlTime'] = unicode(datetime.now().strftime("%Y%m%d %H:%M"))
								idate = re.sub("/",'',date.text)
								item['date'] = re.sub("\(.*",'',idate)
								item['time'] = itime
								items.append(item)
								#print "name-ori" + nameList[z].text + " td" + str(td) + " tr : " + str(tr) + " dept : " + item['dept'] + " date : " + item['date'] + ' time : ' + item['time'] + ' outpatient : ' + item['outpatient'] + ' full : ' + item['full'] + ' name : ' + item['name'] + ' link : ' + item['link']
					weekList = self.driver.find_elements_by_xpath('//a[contains(@id,"ctl00_ContentPlaceHolder1_lbWeek")]')
				home = self.driver.find_element_by_xpath('//a[@id="ctl00_HyperLink1"]')
				home.click()
				time.sleep(5)
				hospitalList = self.driver.find_elements_by_xpath('//tr//td//input[contains(@id,"ctl00_ContentPlaceHolder1_rblZone_")]')
				deptList = self.driver.find_elements_by_xpath('//a[contains(@id,"ctl00_ContentPlaceHolder1_DataList")]')
				#print str(k)
				#print outpatientListLen
				if i != 0  :
					hospitalList[i].click()
					time.sleep(5)
					deptList = self.driver.find_elements_by_xpath('//a[contains(@id,"ctl00_ContentPlaceHolder1_DataList")]')
				if k+1 < outpatientListLen :
					deptList[j].click()
					time.sleep(5)
				#else:
				#	pre = self.driver.find_element_by_xpath('//a[@id="ctl00_ContentPlaceHolder1_lbPrev1"]')
				#	pre.click()
				#	time.sleep(5)
				outpatientList = self.driver.find_elements_by_xpath('//a[contains(@id,"_ContentPlaceHolder1_DataList")]')	
			deptList = self.driver.find_elements_by_xpath('//a[contains(@id,"ctl00_ContentPlaceHolder1_DataList")]')
		hospitalList = self.driver.find_elements_by_xpath('//tr//td//input[contains(@id,"_ContentPlaceHolder1_rblZone_")]')
	self.driver.quit()				
	return items

 
