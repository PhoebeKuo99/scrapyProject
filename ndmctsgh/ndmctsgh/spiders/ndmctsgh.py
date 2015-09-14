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
from ..items import ndmctsghItem
from selenium.common.exceptions import NoAlertPresentException
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import urllib
index = 0
jndex = 0
zindex = 0
js = """
window.alert = function(message) {
lastAlert = message;
}
"""
class ndmctsgh(CrawlSpider):
    name = "ndmctsgh"
    allowed_domains = ["edu.tw"]
    start_urls = [
	"https://www2.ndmctsgh.edu.tw/webreg/DpList.aspx"
	
    ]
    def __init__(self,i=None,j=None,z=None,*args,**kwargs):
        super(ndmctsgh, self).__init__(*args,**kwargs)
	global index
	global jndex
	global zindex
	index = int(i)
	jndex = int(j)
	zindex = int(z)
	self.driver=webdriver.Firefox()


    def parse(self, response):
	self.driver.get(response.url)
	global index
	global zindex
	hospitalList = self.driver.find_elements_by_xpath('//a[contains(@onclick ,"goDpList")]')
	items = []
	wait = WebDriverWait(self.driver, 10)
	#for i in range(len(hospitalList)):
	#for i in range(0,1,1):
	#for i in range(1,2,2):
	hospital = "ndmctsgh - " + hospitalList[zindex].text
	hospitalList[zindex].click()
	outpatientList = self.driver.find_elements_by_xpath('//a[@class="styleDpLink"]')
	deptList = self.driver.find_elements_by_xpath('//div[@id="coda-nav-1"]/ul/li/a')
	#for j in range(len(outpatientList)):				
	for j in range(index-1,index,1):				
		#try :
		deptList[jndex].click()
		time.sleep(5)
		outpatient = outpatientList[j].text
		print outpatient
		outpatientList[j].click()
                try:
                        self.driver.switch_to.alert.accept()
                except NoAlertPresentException:
                        pass
		#except Exception as e:
		#	idep = idep + 1
		#	deptList[idep].click()
		#	time.sleep(5)
		#	outpatientList[j].click()
		dateList = self.driver.find_elements_by_xpath('//td[@class="styleDpTd"]')
		nameList = self.driver.find_elements_by_xpath('//table[@class="styleDrTb"]//td[@class="styleDrTd"]')	
		dept = self.driver.find_element_by_xpath('//a[@id="ctl00_ContentPlaceHolder1_HyperLinkDeptGroup"]')
		weekList = self.driver.find_elements_by_xpath('//li[contains(@class,"tab")]/a')
		for z in range(len(nameList)):
			if z == 24 or z == 48 or z ==72 or z == 96 :
				wait.until(EC.element_to_be_clickable((By.XPATH,'//li[contains(@class,"tab")]/a')))
				weekList[z/24].click()
				time.sleep(5)
				#wait = WebDriverWait(self.driver, 10)
				weekList = self.driver.find_elements_by_xpath('//li[contains(@class,"tab")]/a')
				nameList = self.driver.find_elements_by_xpath('//table[@class="styleDrTb"]//td[@class="styleDrTd"]')	
				dateList = self.driver.find_elements_by_xpath('//td[@class="styleDpTd"]')
			if z%8 == 1 :
				itime = nameList[z-1].text
				if re.search(u"上午",itime):
					itime = 'morning'
				elif re.search(u"下午",itime):
					itime = 'afternoon'
				else :
					itime = 'night'
		
			else:
				theNameList = self.driver.find_elements_by_xpath('(//table[@class="styleDrTb"]//td[@class="styleDrTd"])[%d]//a[contains(@onclick,"goDocProfile")]/parent::td' % (z))
				nameLen = len(theNameList)
				print "nameLen: " + str(nameLen) + " z:" + str(z)
				for k in range(nameLen):
					item = ndmctsghItem()
					dateList = self.driver.find_elements_by_xpath('//td[@class="styleDpTd"]')
					dateIndex = (z-1)%8+8*(z/24)
					date = (dateList[dateIndex].text.split('\n'))[1]
					item['name'] = (theNameList[k].text.split('\n'))[0]
					print "k:" + str(k)+ "z:" + str(z) + "name:" + item['name']
					try : 
						wait.until(EC.element_to_be_clickable((By.XPATH,'((//table[@class="styleDrTb"]//td[@class="styleDrTd"])[%d]//a[contains(@onclick,"goDocProfile")]/parent::td)[%d]/a[@class="styleRegLink"]' %(z, (k+1)))))
						fullLink = self.driver.find_element_by_xpath('((//table[@class="styleDrTb"]//td[@class="styleDrTd"])[%d]//a[contains(@onclick,"goDocProfile")]/parent::td)[%d]/a[@class="styleRegLink"]' %(z, (k+1)))
						fullLink.click()
						time.sleep(5)
                                                try:
                                                	self.driver.switch_to.alert.accept()
                                                except NoAlertPresentException:
                                                        pass
						try :
							element = wait.until(EC.element_to_be_clickable((By.ID,'ctl00_ContentPlaceHolder1_LabelNo')))
							item['full']=(self.driver.find_element_by_xpath('//span[@id="ctl00_ContentPlaceHolder1_LabelNo"]')).text
							(self.driver.find_element_by_xpath('//a[@id="ctl00_ContentPlaceHolder1_HyperLinkDept"]')).click()
							time.sleep(5)
                                                     	try:
                                                        	self.driver.switch_to.alert.accept()
                                                        except NoAlertPresentException:
                                                               	pass
                                                except Exception as e:
							(self.driver.find_element_by_xpath('//a[@id="ctl00_ContentPlaceHolder1_HyperLinkDept"]')).click()
							time.sleep(5)
							item['full'] = u'可掛號'
						element = wait.until(EC.element_to_be_clickable((By.ID,'ctl00_ContentPlaceHolder1_HyperLinkDeptGroup')))
						if element:
							dept = self.driver.find_element_by_xpath('//a[@id="ctl00_ContentPlaceHolder1_HyperLinkDeptGroup"]')
					except Exception as e:
						try:
							item['full'] = (theNameList[k].text.split('\n'))[1]
							if re.match(u"教學診",item['full']):
								item['full']=(theNameList[k].text.split('\n'))[2]
						except Exception as e:
							item['full'] = u'可掛號'	
					item['full']=re.sub(u"號",'',item['full'])
                                        m = re.match(u"(.*)(\d{2})(\d{2})",re.sub('\n','',date))
                                        if m :
                                       		year = str(int(m.group(1))+1911)
                                        	mon = m.group(2)
                                       		day = m.group(3)
                                       		item['date'] = year + mon + day
					item['dept'] = dept.text
					item['outpatient']=outpatient
					item['link']='NA'
					item['crawlTime'] = unicode(datetime.now().strftime("%Y%m%d %H:%M"))
					item['time']=itime
					item['hospital']=hospital
					items.append(item)
					print "hospital : " + item['hospital'] + " dept : " + item['dept'] + " date : " + item['date'] + ' time : ' + item['time'] + ' outpatient : ' + item['outpatient'] + ' full : ' + item['full'] + ' name : ' + item['name'] + ' link : ' + item['link']
					theNameList = self.driver.find_elements_by_xpath('(//table[@class="styleDrTb"]//td[@class="styleDrTd"])[%d]//a[contains(@onclick,"goDocProfile")]/parent::td' % (z))
					nameList = self.driver.find_elements_by_xpath('//table[@class="styleDrTb"]//td[@class="styleDrTd"]')	
					weekList = self.driver.find_elements_by_xpath('//li[contains(@class,"tab")]/a')
		print "end of one week"
		wait = WebDriverWait(self.driver, 20)
		element = wait.until(EC.element_to_be_clickable((By.XPATH,'(//a[@href="DpList.aspx"])[2]')))
		element.click()
		time.sleep(5)
                try:
                	self.driver.switch_to.alert.accept()
                except NoAlertPresentException:
                        pass
		outpatientList = self.driver.find_elements_by_xpath('//a[@class="styleDpLink"]')
		deptList = self.driver.find_elements_by_xpath('//div[@id="coda-nav-1"]/ul/li/a')
	hospitalList = self.driver.find_elements_by_xpath('//a[contains(@onclick ,"goDpList")]')
	self.driver.quit()
	return items
 
