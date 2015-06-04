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
from ..items import vghtpeItem
from selenium.common.exceptions import NoAlertPresentException
from selenium import webdriver
import urllib
js = """
window.alert = function(message) {
lastAlert = message;
}
"""
class vghtpe(CrawlSpider):
    name = "vghtpe"
    allowed_domains = ["gov.tw"]
    start_urls = [
	"https://www6.vghtpe.gov.tw/opd/opd_inter/vgh_opda.htm"
	
    ]
    def __init__(self,**kwargs):
        self.driver=webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs')
	#self.driver=webdriver.Firefox()

    def parse(self, response):
	self.driver.get(response.url)
	items = []
	outpatientList = self.driver.find_elements_by_xpath('(//input[@name="pdsect"])')
	hospital = 'vghtpe'
	dept = ''
	idept = 1
	iout = 1
	for i in range(len(outpatientList)):
	#for i in range(46,100,1):
		if dept == '' :
			dept = (self.driver.find_element_by_xpath('((//input[@name="pdsect"])[%d]//parent::td//center/B)[1]' %(i+1))).text
		elif dept != (self.driver.find_element_by_xpath('((//input[@name="pdsect"])[%d]//parent::td//center/B)[1]' %(i+1))).text:
			dept = (self.driver.find_element_by_xpath('((//input[@name="pdsect"])[%d]//parent::td//center/B)[1]' %(i+1))).text
			idept = idept + 1
			iout = 1
		else :
			dept = (self.driver.find_element_by_xpath('((//input[@name="pdsect"])[%d]//parent::td//center/B)[1]' %(i+1))).text
			iout = iout + 1
		outpatientName = self.driver.find_element_by_xpath('((//input[@name="pdsect"])//parent::td)[%d]' %(idept))
		outpatient = (re.split("\s*",re.sub("\(.*\)",'',outpatientName.text)))[iout]
		if re.search(u"請掛",outpatient):
			iout = iout + 1
			outpatient = (re.split("\s*",re.sub("\(.*\)",'',outpatientName.text)))[iout]
		elif re.search(u"\(",outpatient):
			iout = iout + 2
			outpatient = (re.split("\s*",re.sub("\(.*\)",'',outpatientName.text)))[iout]
		outpatientList[i].click()

		### week click
		weekList = self.driver.find_elements_by_xpath('//input[@type="button" and contains(@name,"Bnweek")]')
		for j in range(len(weekList)):				
			outpatientList = self.driver.find_elements_by_xpath('(//input[@name="pdsect"])')
			outpatientList[i].click()
			weekList[j].click()
	                try:
				self.driver.execute_script("%s" % js)
                		#self.driver.switch_to.alert.accept()
                	except NoAlertPresentException:
                        	pass		
			tableList = self.driver.find_elements_by_xpath('//form[@name="oregForm"]//caption//parent::table')
			for t in range(len(tableList)):			
				tableRow = self.driver.find_elements_by_xpath('(//form[@name="oregForm"]//caption//parent::table)[%d]//tr' % (t+1))
				itime = tableRow[len(tableRow)-1].text
				if re.search(u"上午",itime):
					itime = 'morning'
				elif re.search(u"下午",itime):
					itime = 'afternoon'
				else :
					itime = 'night'

				for r in range(len(tableRow)):	
					if r == 0 :
						dateList = tableRow[r].find_elements_by_xpath('.//td')	
						#print dateList		
					else :
						nameList = self.driver.find_elements_by_xpath('(//form[@name="oregForm"]//caption//parent::table)[%d]//tr[%d]/td' % (t+1,r+1))
						#print nameList
						for n in range(len(nameList)):
							if n ==0 or nameList[n].text == "": continue
							item = vghtpeItem()
							info = self.driver.find_element_by_xpath('((//form[@name="oregForm"]//caption//parent::table)[%d]//tr[%d]/td)[%d]' % (t+1,r+1,n+1))
							name = (re.split('[[\s]*',info.text))[0]
							full = (re.split('[\s]*',info.text))[-1]
							if name == full : 
								full = u"可掛號"
							name = re.sub(u"\s*教學診",'',name)
							date=unicode(datetime.now().strftime("%Y")) + re.sub("[^0-9]",'',dateList[n].text)
							item['crawlTime'] = unicode(datetime.now().strftime("%Y%m%d %H:%M"))
							item['dept']=dept
							item['outpatient']=outpatient
							item['name']=name
							item['link']='NA'
							item['hospital']=hospital
							item['date']=date
							item['time']=itime
							item['full']=full
							items.append(item)
							#print "hospital : "+ hospital + " dept : " + dept + " outpatient : " + outpatient +  " name : " + name + " full : " + full + " date : " + date + " time : " + itime 
				#print "end of the table"
			
						#print "dept : " + item['dept'] + " date : " + item['date'] + ' time : ' + item['time'] + ' outpatient : ' + item['outpatient'] + ' full : ' + item['full'] + ' name : ' + item['name'] + ' link : ' + item['link']
			aLink = self.driver.find_elements_by_xpath('.//a')
			aLen = len(aLink)
			aLink[aLen-1].click()
			weekList = self.driver.find_elements_by_xpath('//input[@type="button" and contains(@name,"Bnweek")]')
		outpatientList = self.driver.find_elements_by_xpath('(//input[@name="pdsect"])')
	self.driver.quit()
	return items
 
