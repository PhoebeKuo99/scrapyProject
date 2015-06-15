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
from ..items import kmuhItem
from selenium.common.exceptions import NoAlertPresentException
from selenium import webdriver
import urllib
js = """
window.alert = function(message) {
lastAlert = message;
}
"""
class kmuh(CrawlSpider):
    name = "kmuh-cijin"
    start_urls = [
	"http://www.kmch.org.tw/Pages/P02Register/NetReg/ShowNetRegDept.aspx"
    ]
    def __init__(self,**kwargs):
        #self.driver=webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs')
	self.driver=webdriver.Firefox()

    def parse(self, response):
	self.driver.get(response.url)
	items = []
        try:
        	#self.driver.execute_script("%s" % js)
                self.driver.switch_to.alert.accept()
        except NoAlertPresentException:
                pass
        try:
        	#self.driver.execute_script("%s" % js)
                self.driver.switch_to.alert.accept()
        except NoAlertPresentException:
                pass
	#deptList = self.driver.find_elements_by_xpath('//a[contains(@id,"UC_NetRegDept1")]')
	deptList = self.driver.find_elements_by_xpath('//a[@class="treea"]')
	for i in range(len(deptList)):
		dept = deptList[i].text
		#print dept
		deptList[i].click()
        	try:
                	self.driver.switch_to.alert.accept()
        	except NoAlertPresentException:
                	pass
		urlList = self.driver.find_elements_by_xpath('//a[contains(@href,"noonType")]')
		for j in range(len(urlList)):
			#print urlList[j].get_attribute('href')
			try :
				self.driver.get(urlList[j].get_attribute('href'))
				tableList = self.driver.find_elements_by_xpath('(//table[@class="text"]//table[@class="text"])')
				#print 'here-----------'
				for z in range(len(tableList)):
					outpatientList = self.driver.find_elements_by_xpath('(//table[@class="text"]//table[@class="text"])[%d]//preceding::td/font' %(z+1))
					outpatient = (outpatientList[-1].text)
					outpatient = re.sub("\n",'',outpatient)
					outpatient = re.sub(u".診.*",'',outpatient)
					outpatient = re.sub(u"[0-9]*",'',outpatient)
					outpatient = re.sub(u"\(.*",'',outpatient)
					#print outpatient
					tdList = tableList[z].find_elements_by_xpath('.//tr//td')
					for k in range(len(tdList)):
						try :
							name = (tdList[k].find_element_by_xpath('./a')).text
							name = re.sub(u"代診",'',name)
							name = re.sub(u"[ \t\n\r]*\(.*",'',name)
							if tableList[z].find_elements_by_xpath('(.//tr//td)[%d][@background="images/bg_regfull.jpg"]' %(k+1)) != [] :
								full = u"預約額滿"
							else:
								full = u'尚可掛號'
							date = re.sub("[ \t\r\n].*",'',tdList[k].text)
							date = re.sub(u"今日",'',date)
                                                        year = re.match(r"(\d*)/(\d*)/(\d*)",date).group(1)
                                                        mon = re.match(r"(\d*)/(\d*)/(\d*)",date).group(2)
							if len(mon)!=2: mon = '0'+mon
                                                        day = re.match(r"(\d*)/(\d*)/(\d*)",date).group(3)
							if len(day)!=2: day = '0'+day
                                                        date = year + mon + day
							if j==0:
								itime = 'morning'
							elif j==1:
								itime ='afternoon'
							else:
								itime = 'night'
							#print name
	                        			item= kmuhItem()
	                        			item['hospital']='kmuh - 旗津'
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
						except:
							pass
			except:
				pass	
			urlList = self.driver.find_elements_by_xpath('//a[contains(@href,"noonType")]')
		self.driver.get("http://www.kmch.org.tw/Pages/P02Register/NetReg/ShowNetRegDept.aspx")
      		try:
                	self.driver.switch_to.alert.accept()
        	except NoAlertPresentException:
                	pass
		time.sleep(5)
		#deptList = self.driver.find_elements_by_xpath('//a[contains(@id,"UC_NetRegDept1")]')
		deptList = self.driver.find_elements_by_xpath('//a[@class="treea"]')
	self.driver.quit()
	return items
