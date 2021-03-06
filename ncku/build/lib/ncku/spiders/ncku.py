# -*- coding: utf-8 -*-
import sys
import scrapy
import re
import time
from datetime import datetime
from scrapy.http import Request, FormRequest, TextResponse
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy import log
from ..items import nckuItem
from scrapy.contrib.spiders import CrawlSpider, Rule
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
#from scrapy.stats import Stats
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"]=("Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0")
class ncku(scrapy.Spider):
    name = "ncku"
    allowed_domains = ["ncku.edu.tw"]
    start_urls = [
	"http://www.hosp.ncku.edu.tw/Tandem/DeptUI.aspx",
	"http://140.116.220.21/DeptUI.aspx"
    ]
    def __init__(self,**kwargs):
	self.driver=webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs')
	#self.driver=webdriver.Firefox()

    def parse(self, response):
	self.driver.get(response.url)
	if response.url == 'http://www.hosp.ncku.edu.tw/Tandem/DeptUI.aspx':
		hospital = 'ncku'
		regTable = "table[@id='tRegSchedule']"
	else: 
		hospital = 'ncku-斗六'
		regTable = "table[@name='regTable']"
	items=[]
	outpatientList = self.driver.find_elements_by_xpath("//table[@id='tContent']//a")
        #btnList = self.driver.find_elements_by_xpath('//table[@class="style19"]//input[@type="submit"]')
	#for n in range(1):
	for n in range(len(outpatientList)):
		dept = outpatientList[n].text
		outpatientList[n].click()
		time.sleep(5)
		dateList = self.driver.find_elements_by_xpath("//%s//tr" % (regTable))[1]
		#print dateList
		#dateLen = len(dateList) - 2
		timeList = self.driver.find_elements_by_xpath("//%s//tr" % (regTable))[2]
		#dateLen = len(timeList) - 1
		rowList = self.driver.find_elements_by_xpath("//%s//tr" % (regTable))
		rowLen = len(rowList)
		colList = self.driver.find_elements_by_xpath("//%s//tr[3]//td" %(regTable))
		colLen = len(colList)
		ioutpatient = ''
		weekList = self.driver.find_elements_by_xpath('//select[@id="ctl00_MainContent_ddlWeeks"]//option')
		for week in range(len(weekList)):
			nth = week + 1
			if nth > 1 :
				weekList[week].click()
				time.sleep(5)
				weekList = self.driver.find_elements_by_xpath('//select[@id="ctl00_MainContent_ddlWeeks"]//option')
			for row in range(rowLen):
				i = 0
				### get col
				for col in range(colLen):
				#for col in range(1):
					r_index = row + 2
					c_index = col + 2
					xpath = "(//%s//tr)[%d]//td[%d]" % (regTable,r_index,c_index)
					xpath2 = "(//%s//tr)[%d]//td[%d]/a" % (regTable,r_index,c_index)
					doc = self.driver.find_elements_by_xpath(xpath)
					if doc !=[] :	
						item = nckuItem()
						item['hospital'] = hospital
						item['crawlTime'] = unicode(datetime.now().strftime("%Y%m%d %H:%M"))
						if not re.match(r"^\d+$",doc[0].text,re.UNICODE):
							if re.match(r"^\s*$",doc[0].text,re.UNICODE):
								i = i + 1
								continue
							m = re.match(r"\(.*\)(.*)",doc[0].text)
							if m:
								name = m.group(1)
								item['full'] = u'預約額滿'	
								item['link'] = 'NA'
							else :
								name = doc[0].text
								item['full'] = u'可掛號'
								item['link'] = 'NA'
								#item['link'] = self.driver.find_element_by_xpath(xpath2)
							m = re.match(r"(.*)[\n\t\r](.*)",name)
							if m:
								item['name'] = m.group(1)
							else:
								item['name'] = name
							xpath4 = "((//%s//tr)/td[1])[%d]" % (regTable,row)
							outpatient = self.driver.find_element_by_xpath(xpath4)
							#print outpatient.text
							if not re.match(r"^\d+$",outpatient.text,re.UNICODE):
								ioutpatient = outpatient.text
								item['outpatient'] = outpatient.text
							else:
								item['outpatient'] = ioutpatient
							idate = i/3 + 3
							xpath3 = "(//%s//tr)[1]//th[%d]" % (regTable,idate)
							item['date'] =  (self.driver.find_element_by_xpath(xpath3)).text
							itime = i + 2
							i =  i + 1
							xpath3 = "(//%s//tr)[2]//th[%d]" % (regTable,itime)
							item['time'] =  (self.driver.find_element_by_xpath(xpath3)).text
							m = re.search(r".*\((.*)/(.*)\).*",item['date'])
							if m :
								mon = m.group(1)
								day = m.group(2)
								item['date'] = unicode(datetime.now().strftime("%Y")) + mon + day
							item['dept'] = dept
							items.append(item)
							#print "colLen = " + str(colLen) + " row : " + str(row) + " col : " + str(col) + " " + "name : " + item['name'] + "itime : " + str(itime) + " time : " + item['time'] + " date : " + item['date'] + " full : " + item['full'] + " outpatient : " + item['outpatient'] + "link : " + str(item['link'])

		self.driver.get(response.url)
		outpatientList = self.driver.find_elements_by_xpath("//table[@id='tContent']//a")
			
	self.driver.close()
	return items


##output format

#hospital dept date time name

