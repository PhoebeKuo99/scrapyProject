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
    name = "kmuh"
    start_urls = [
	"http://www.kmuh.org.tw/KMUHWeb/Pages/P02Register/NetReg/NetRegFirst.aspx"
	
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
	field = self.driver.find_element_by_xpath('//input[@name = "ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolder2$UC_NetRegFirst1$TextBox_ChartOrID"]')
	send = self.driver.find_element_by_xpath('//input[@name = "ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolder2$UC_NetRegFirst1$Button_Submit"]')
	field.send_keys("E235656562")
	send.click()
        try:
        	#self.driver.execute_script("%s" % js)
                self.driver.switch_to.alert.accept()
        except NoAlertPresentException:
                pass
	deptList = self.driver.find_elements_by_xpath('//a[contains(@id,"ContentPlaceHolder1")]')
	for i in range(len(deptList)):
		dept = deptList[i].get_attribute('title')
		#print dept
		deptList[i].click()
		urlList = self.driver.find_elements_by_xpath('//a[contains(@href,"noonType")]')
		for j in range(len(urlList)):
			#print urlList[j].get_attribute('href')
			self.driver.get(urlList[j].get_attribute('href'))
			tableList = self.driver.find_elements_by_xpath('(//table[@class="text"]//table[@class="text"])')
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
						if re.search(u"額滿",tdList[k].text):
							full = u"預約額滿"
						else:
							full = u'尚可掛號'
						date = re.sub("[ \t\r\n].*",'',tdList[k].text)
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
                        			item['hospital']='kmuh - 中和本院'
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
			urlList = self.driver.find_elements_by_xpath('//a[contains(@href,"noonType")]')
		self.driver.get("http://www.kmuh.org.tw/KMUHWeb/Pages/P02Register/NetReg/ShowNetRegDept.aspx")
		deptList = self.driver.find_elements_by_xpath('//a[contains(@id,"ContentPlaceHolder1")]')
	self.driver.quit()
	return items
