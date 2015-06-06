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
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from scrapy.contrib.linkextractors import LinkExtractor
from ..items import cghItem

class cgh(scrapy.Spider):
    name = "cgh"
    allowed_domains = ["org.tw"]
    start_urls = [
	"http://www.cgh.org.tw/tw/reg/main_01.jsp"
    ]
    def __init__(self,**kwargs):
	#self.driver=webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs')
	self.driver=webdriver.Firefox()

    def parse(self, response):
        self.driver.get(response.url)
	items=[]
	### hospital list
	hospitalList = self.driver.find_elements_by_xpath('//td/a[contains(@title,"掛號")]')
	for ihospital in range(0,len(hospitalList),1):
		hospital = hospitalList[ihospital].get_attribute("title")
		hospital = re.sub(u"國泰綜合醫院(.*)(國泰)?掛號",r'cgh-\1',hospital)
		if not re.search(u"(新竹|總院|汐止)",hospital):
			continue
		#print str(ihospital)
		hospitalList[ihospital].click()
		#print hospital
		for idep in range(1,20,4):
		#for idep in range(1,2,1):
			try : 
				dept = self.driver.find_element_by_xpath("//tr[%d]/td[@class='Table-title-03']" %(idep))
				dept = dept.text
				#print dept
				outpatientList = self.driver.find_elements_by_xpath("//tr[%d+2]/td[2]/table/tbody//td[@class='Dep-list']//a" %(idep))
				for ioutpatient in range(0,len(outpatientList),1):
				#for ioutpatient in range(0,1,1):
					outpatient = outpatientList[ioutpatient].text
					if outpatient == u'放射腫瘤科' or (hospital != u'cgh-總院' and outpatient == u'牙科'):
						continue
					#print str(ioutpatient) + " : "+ outpatient
					outpatientList[ioutpatient].click() 
					nameList =  self.driver.find_elements_by_xpath("//tr[@class='Content-text' or @class='Table-title-02']//a")
					if len(nameList) >= 1 :
						for iname in range(0,len(nameList),1):
						#for iname in range(0,2,1):
							name = nameList[iname].text
							#print str(iname) + " : " + name
							nameList[iname].click()
							try:
							        self.driver.switch_to.alert.accept()
							except NoAlertPresentException:
							        pass
							itime = self.driver.find_element_by_xpath("(//td[@class='Table-title-04'])[1]").text
							infoList =self.driver.find_elements_by_xpath("//tr[@class='Content-text' or @class='Table-title-02']")
							
							if re.search(u"上午",itime): 
								itime = 'morning'
							elif re.search(u"下午",itime): 
								itime = 'afternoon'
							else :
								itime = 'evening'
							for info in range(1,len(infoList)+1,1):
								#print info
								item=cghItem()
								full =self.driver.find_element_by_xpath("(//tr[@class='Content-text' or @class='Table-title-02'])[%d]/td[4]" % (info)).text
								if re.match(r"^\s*$",full,re.UNICODE):
									full = u'可掛號'
								date =self.driver.find_element_by_xpath("(//tr[@class='Content-text' or @class='Table-title-02'])[%d]//td[2]" % (info)).text
								year = int(re.match(r"(\d*)\.(\d*)\.(\d*)",date).group(1)) + 1911
								mon = re.match(r"(\d*)\.(\d*)\.(\d*)",date).group(2)
								day = re.match(r"(\d*)\.(\d*)\.(\d*)",date).group(3)
								date = str(year) + mon + day
								#print "hospital : " + hospital + " dept : " +  dept + " outpatient : " + outpatient + " Name : " + name + " date : " + date + " time : " + itime + " full : " + full
								item['hospital']=hospital			
								item['dept']=dept			
								item['outpatient']=outpatient			
								item['name']=name			
								item['date']=date		
								item['time']=itime			
								item['full']=full			
								item['link']='NA'
								item['crawlTime']=unicode(datetime.now().strftime("%Y%m%d %H:%M"))	
								items.append(item)			
							self.driver.back()
							nameList =  self.driver.find_elements_by_xpath("//tr[@class='Content-text' or @class='Table-title-02']//a")
					self.driver.back()
					outpatientList = self.driver.find_elements_by_xpath("//tr[%d+2]/td[2]/table/tbody//td[@class='Dep-list']//a" %(idep))
				#self.driver.back()
			except Exception as e:
				continue
		self.driver.back()
		hospitalList = self.driver.find_elements_by_xpath('//td/a[contains(@title,"掛號")]')
	self.driver.quit()
	return items

