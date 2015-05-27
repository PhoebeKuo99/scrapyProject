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
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from scrapy.contrib.linkextractors import LinkExtractor
from selenium.common.exceptions import WebDriverException
from ..items import cchItem

ihospital = 0
itimeXpath = ''
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"]=("Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0")
startUrlLen = 0

class cch(scrapy.Spider):
    name = "cch"
    allowed_domains = ["org.tw"]
    def __init__(self,hospitalUrl=None,*args,**kwargs):
	super(cch, self).__init__(*args,**kwargs)
	if hospitalUrl:
		self.start_urls = ['%s' % hospitalUrl]
	else:
    		self.start_urls = [
       		 	#"http://www2.cch.org.tw/20RG/opd/Service-e.aspx",
			"http://www.erhlin.cch.org.tw/opd/opd/Service-e.aspx",
        		"http://www.rc.cch.org.tw/opd/Service-e.aspx",
        		"http://www2.cch.org.tw/rdweb/opd/Service-e.aspx",
        		"http://www.ys.cch.org.tw/opd/Service-e.aspx",
        		"http://www2.cch.org.tw/NYRG/opd/Service-e.aspx",
        		"http://web3.yl.cch.org.tw/opd/Service-e.aspx",
        		"http://www2.cch.org.tw/YMRG/opd/Service-e.aspx",
        		"http://www.cch.org.tw/opd/Service-e.aspx"
    		]
	global startUrlLen
	startUrlLen = len(self.start_urls)
	self.driver=webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs')
	#self.driver=webdriver.Fire

    def parse(self, response):
        self.driver.get(response.url)
	global ihospital
	ihospital = ihospital + 1
	if response.url == 'http://www2.cch.org.tw/20RG/opd/Service-e.aspx':
		hospital = u'cch-二林'
	elif response.url == 'http://www.rc.cch.org.tw/opd/Service-e.aspx':
		hospital = u'cch-鹿基'
	elif response.url == 'http://www2.cch.org.tw/rdweb/opd/Service-e.aspx':
		hospital = u'cch-鹿東'
	elif response.url == 'http://www.ys.cch.org.tw/opd/Service-e.aspx':
		hospital = u'cch-員生'
	elif response.url == 'http://www2.cch.org.tw/NYRG/opd/Service-e.aspx':
		hospital = u'cch-南基'
	elif response.url == 'http://web3.yl.cch.org.tw/opd/Service-e.aspx':
		hospital = u'cch-雲林'
	elif response.url == 'http://www2.cch.org.tw/YMRG/opd/Service-e.aspx':
		hospital = u'cch-佑民'
	else :
		hospital = u'cch'
	items = []
	deptXpath = "(//table[@id='DListSec']//table)"
	deptList = self.driver.find_elements_by_xpath(deptXpath)
	deptNum = len(deptList)
	for d in range(0,deptNum,2):
	#for d in range(1):
		deptIndex = d + 1
		deptXpath2 = "(//table[@id='DListSec']//table)[%d]//td[1]" %(deptIndex)
		deptName = self.driver.find_element_by_xpath(deptXpath2)
		dept = deptName.text
		outpatientXpath = "(//table[@id='DListSec']//table)[%d]//a" %(deptIndex)
		outpatientList = self.driver.find_elements_by_xpath(outpatientXpath)
		for p in range(len(outpatientList)):
		#for p in range(1,2,1):
			outpatient = outpatientList[p].text
			outpatientList[p].click()
			time.sleep(5)
			outpatientList = self.driver.find_elements_by_xpath(outpatientXpath)
			btnList = self.driver.find_elements_by_xpath('//select[@name="OPDate"]//option')
			#btnList = self.driver.find_elements_by_xpath('//select[@name="OPDate"]//option')
			btnNum = len(btnList)
			for btn in range(btnNum):
			#for btn in range(1):
				#print "OPDate : " + str(btn)
				btnList = self.driver.find_elements_by_xpath('//select[@name="OPDate"]//option')	
				if btn !=0:
					element = WebDriverWait(self.driver,10).until(EC.invisibility_of_element_located((By.ID, btnList[btn])))
					if element : 
						btnList[btn].click()
						time.sleep(5)
						btnList = self.driver.find_elements_by_xpath('//select[@name="OPDate"]//option')	
				###
				tableXpath = "((//table[@id='MainDL']//tr//td)/table[not(contains(@id,'Table'))])"
				tableList = self.driver.find_elements_by_xpath(tableXpath)
				tableLen = len(tableList)
				for n in range(tableLen):
				#for n in range(1):
					### tr
					tableIndex = n + 1
					#print "table : " + str(tableIndex)
					trXpath = "((//table[@id='MainDL']//tr//td)/table[not(contains(@id,'Table'))])[%d]/tbody/tr" %(tableIndex)
					trList = self.driver.find_elements_by_xpath(trXpath)
					trLen = len(trList)
					date = ''	
					for k in range(trLen):
						trList = self.driver.find_elements_by_xpath(trXpath)
						name = ''
						itime = ''
						trIndex = k + 1
						#print "tr : " + str(trIndex)
						if trIndex == 1:
							### date
							dateXpath = "((//table[@id='MainDL']//tr//td)/table[not(contains(@id,'Table'))])[%d]/tbody/tr[%d]/td[1]" %(tableIndex,trIndex)
							date =  (self.driver.find_element_by_xpath(dateXpath).text).split('\n')[0]
							m= re.search(u"(.*)月(.*)日",date)
							if m:
								mon = m.group(1)
								day = m.group(2)
								if len(mon) == 1: 
									mon = '0'+mon
								if len(day) == 1: 
									day = '0'+day
								date = unicode(datetime.now().strftime("%Y")) + mon + day
							nameXpath = "(((//table[@id='MainDL']//tr//td)/table[not(contains(@id,'Table'))])[%d]/tbody/tr[%d]/td[3]//td/table)" %(tableIndex,trIndex)
							nameList = self.driver.find_elements_by_xpath(nameXpath)
							time.sleep(5)
							itimeXpath = "(((//table[@id='MainDL']//tr//td)/table[not(contains(@id,'Table'))])[%d]/tbody/tr[%d]/td[2])" %(tableIndex,trIndex)
							itime = self.driver.find_element_by_xpath(itimeXpath).text
						else:
							nameXpath = "(((//table[@id='MainDL']//tr//td)/table[not(contains(@id,'Table'))])[%d]/tbody/tr[%d]/td[2]//td/table)" %(tableIndex,trIndex)
							nameList = self.driver.find_elements_by_xpath(nameXpath)
							itimeXpath = "(((//table[@id='MainDL']//tr//td)/table[not(contains(@id,'Table'))])[%d]/tbody/tr[%d]/td[1])" %(tableIndex,trIndex)
							itime = self.driver.find_element_by_xpath(itimeXpath).text
						nameLen = len(nameList)
						for j in range(nameLen):
							linkIndex = j + 1
							if itime == u'上 午':
								itime = 'morning'
							elif itime ==u'下 午':
								itime = 'afternoon'
							elif itime ==u'晚 上':
								itime = 'evening'
							nameList = self.driver.find_elements_by_xpath(nameXpath)
							#print itime
							#print date
							#print outpatient
							#print nameList[j].text
							name = nameList[j].text.split('\n')[1]
							nameList = self.driver.find_elements_by_xpath(nameXpath)
							full = nameList[j].text.split('\n')[2]
							linkXpath = str('%s//a' %(nameXpath))
							try:
								link = self.driver.find_element_by_xpath(linkXpath).get_attribute('href')
							except Exception as e:
								link = 'NA'
							if full == u'額滿':
								full = u'預約額滿'
							else :
								full = u'可掛號'
							crawlTime = unicode(datetime.now().strftime("%Y%m%d %H:%M"))	
							item = cchItem()
							item['crawlTime'] = crawlTime
    							item['hospital'] = hospital
    							item['dept'] = dept
    							item['date'] = date
   	 						item['time'] = itime
    							item['name'] = name
    							item['full'] = full
    							item['link'] = link
    							item['outpatient'] = outpatient
							items.append(item)	
							#print "hospital : " + hospital + " dept : " +  dept + " outpatient : " + outpatient + " Name : " + name + " date : " + date + " time : " + itime + " full : " + full
	global startUrlLen
	if ihospital == startUrlLen :
		self.driver.quit()
	#print "ihospital: " + ihospital + "startUrlLen: " + startUrlLen
	return items
        

   
