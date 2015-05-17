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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from scrapy.contrib.linkextractors import LinkExtractor
from ..items import vgthksItem
from ..outpatientMap import outpatientMap

#def process_value(value) :
  #m = re.search(".*ns_Z7_CMRPOKG10GEA60INIP7A8O04T1_selectClinic\(('[^ ]*'),\s*('[^ ]*'),\s*('[^ ]*'),\s*('[^ ]*')\).*", value)
  #if m :
  #  aa = 'http://webreg.vghks.gov.tw/wps/portal/web/onlinereg/!ut/p/b1/04_SjzQytDCzBEH9CP2ovMSyzPTEksz8vMQcED_KLN7ZNyjA39vd0MDd1dHMwNPPM8Dc0cLfwCTEAKggEo8CH3NC-r30o9Jz8pOAVoXrR-FVDDILrMAAB3A00PfzyM9N1c-NyrHIzjJRBAAqP0Sv/dl4/d5/L0lDU0lKSmdrS0NsRUpDZ3BSQ1NBL29Ob2dBRUlRaGpFS0lRQUJHY1p3aklDa3FTaFNOQkFOYUEhIS80RzNhRDJnanZ5aENreUZNTlFpa3lGUDFTaklVUVEhIS9aN19DTVJQT0tHMTBHRUE2MElOSVA3QThPMDRUMS8wL2libS5pbnYvMjg3OTcwNjUwMTQ0L3NlbGVjdENsaW5pYw!!/' + '?dtlid=' + m.group(1) + '&ptitle=' +  m.group(2) + '&dtletitl=' + m.group(3) + '&dtltitle=' +  m.group(4)

  #  return aa

dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"]=("Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0")
class vgthks(scrapy.Spider):
    name = "vgthks"
    allowed_domains = ["gov.tw"]
    start_urls = [
	"http://webreg.vghks.gov.tw/wps/portal/web/onlinereg"
    ]
    #rules =(
	#Rule(LinkExtractor(restrict_xpaths=('//ul[@id="s_divisions"]/li/a',), attrs=('onclick',), process_value=process_value), callback='parse_table', follow= True),
    #)
    def __init__(self,**kwargs):
    #def __init__(self, **kwargs):
    #	super(vgthks, self).__init__(self, **kwargs)
	#self.driver=webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs')
	self.driver=webdriver.Firefox()

    def parse(self, response):
        self.driver.get(response.url)
	deptList = self.driver.find_elements_by_xpath('//a[contains(@onclick,"changeClass")]')
	btnList = self.driver.find_elements_by_xpath('//a[@id="selectClinicBtn"]')
	btnNum = len(btnList)
	#main_window=self.driver.current_window_handle
	#for btn in range(btnNum):
	for btn in range(btnNum):
                #self.driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')
        	self.driver.get(response.url)
		btnList = self.driver.find_elements_by_xpath('//a[@id="selectClinicBtn"]')
		deptList = self.driver.find_elements_by_xpath('//a[contains(@onclick,"changeClass")]')
		clinic = btnList[btn].text
		dept = deptList[0].text 
		while clinic =='':
			for dep in range(len(deptList)):
				#deptList[dep].extract()
				dept = deptList[dep].text 
				deptList[dep].click()
				clinic = btnList[btn].text
				if clinic != '':
					break
					
		#print clinic
		#if clinic in outpatientMap:
		btnList[btn].click()
		oriUrl = self.driver.current_url
		for i in range(0,2,1):
			if i == 1:
				self.driver.get(oriUrl)
				nextWeek = self.driver.find_elements_by_xpath("//div[@class='f_center week']//a")
				nextWeek[0].click()
				time.sleep(5)
			request = Request(self.driver.current_url,callback=self.parse_table)
			request.meta['btn'] = btn
			request.meta['btnNum'] = btnNum
			request.meta['dept'] = dept
			yield request
		#self.driver.back()
		#yield Request("http://webreg.vghks.gov.tw/wps/portal/web/onlinereg")
		#self.driver.execute_script("window.close('');")
		#self.driver.switch_to_window(main_window)
        	#self.driver.get("http://webreg.vghks.gov.tw/wps/portal/web/onlinereg")
		#btnList = self.driver.find_elements_by_xpath('//a[@id="selectClinicBtn"]')
	self.driver.close()

    def parse_table(self, response):
	sel = Selector(response)
	dept = response.meta['dept']
        #self.driver2.get("http://webreg.vghks.gov.tw/wps/portal/web/onlinereg")
	#time.sleep(5)
	btn = response.meta['btn']
	btnLen = response.meta['btnNum'] - 1
	#self.driver2.find_elements_by_xpath('//a[@id="selectClinicBtn"]')[btn].click()
	#time.sleep(5)
        items = []
	outpatient = sel.xpath('//div[@class="mb5"]/div[1]/h1/text()').extract()
        #xx = driver.find_elements_by_xpath('//table[@id="report"]/tr/th/text()')
	outpatient = re.sub(r'[\t\n\r]','',outpatient[0])

        tables = sel.xpath('//table[@id="report"]')
	dateList = sel.xpath('//table[@id="report"]/tr/th/text()').extract()
	for t in range(len(tables)):
            #print "table = " + str(t)
            ##每個table看有幾個row
            tableRow = tables[t].xpath('.//ul[1]/li')
	    tableRow2 = ''
	    period = len(tables[t].xpath('//div[@class="position_r"]'))
	    #print "period = " + str(period)
	    if period ==0:
		#print "-I- No schedule available for " + dept
		continue
            tableColumn = (len(tables[t].xpath('.//td')) - period*2)/period
	    if period == 2:
            	tableRow2 = tables[t].xpath('.//ul')[tableColumn].xpath('.//li')
            	#print "tableRow2 = " + str(len(tableRow2))
            #print "tableRow = " + str(len(tableRow))
            #print "tableColumn = " + str(tableColumn)
            for n in range(len(tableRow)):
                for j in range(tableColumn):
			#print "row:" + str(n) + " col:" + str(j)
			lineNum = 0
			try:
		    		data = tables[t].xpath(".//ul")[j].xpath(".//li")[n].xpath(".//text()").extract()
			except Exception as e:
				data =[]
			if data == []:
			   continue
			for index in range(len(data)):
			   data[index] = re.sub(r'[\t\n\r]','',data[index])
			   #print str(index) + data[index]
			   if re.match("^\s*$",data[index]):
				continue
			   else:
			   	lineNum = lineNum + 1
			   #print "row : " + str(n) + " col = " + str(j) + " lineNum : " + str(lineNum) + " data = " + data[index]
			   if lineNum == 2 or lineNum ==3:
				if lineNum==2:
            		   		item = vgthksItem()
    					item['hospital'] = 'vgthks'
                           		item['crawlTime'] = unicode(datetime.now().strftime("%Y%m%d %H:%M"))
                           		item['dept'] = dept
                           		item['outpatient'] = outpatient
					item['time'] = 'morning'
					mon = re.match(r"(\d*)/([\d]*)",dateList[j]).group(1)
					day = re.match(r"(\d*)/([\d]*)",dateList[j]).group(2)
					item['date'] = unicode(datetime.now().strftime("%Y")) + mon + day
					item['name'] = data[index]
					item['name'] = re.sub("\(.*",'',item['name'])
					#print item['name']
					#print item['time']
					#print item['outpatient']
					#print item['date']
				elif lineNum==3:
					#print "-" + data[index] + "-"
					#if data[index] == u'　':
					if re.match("^\s*$",data[index],re.UNICODE):
						item['full'] = u'可掛號'
					else:	
						item['full'] = data[index]
					item['link']=response.url
					#jth = j + 1
					#nth = n + 1
					#xpath = "(//table[@id='report']//ul)[%d]//li[%d]//div[@id=\"goFillInfoBtn\"]" % (jth,nth)
					#print xpath
					#nth = n*tableColumn + j
					#print self.driver2.page_source
					#print nth
					#try :
						#element = WebDriverWait(self.driver2,10).until(EC.presence_of_element_located((By.XPATH,xpath)))
					#	element=self.driver2.find_element_by_xpath(xpath)
						#element=self.driver2.find_elements_by_id('goFillInfoBtn')[nth]
					#	element.click()
					#	time.sleep(5)
					#	item['link'] = self.driver2.current_url
					#	self.driver2.back()
					#	time.sleep(5)
						#element.click()
					#	element = WebDriverWait(self.driver2,10).until(EC.presence_of_element_located((By.XPATH,xpath)))
					#except Exception as e:
						#element=self.driver2.find_elements_by_xpath('//div[@onclick="ns_Z7_CMRPOKG10GEA60INIP7A8O04T1_reload()"]')
						#element[nth].click()
					#	item['link'] = "尚未開放預約掛號"
						#self.driver2.back()
					#	pass
					#item['link'] = self.driver2.current_url
					items.append(item)
					#print item['link']
					#print item['full']
	    #print "---------------"
            for n in range(len(tableRow2)):
                for j in range(tableColumn , 2*tableColumn):
			#print "row:" + str(n) + " col:" + str(j)
			lineNum = 0
		    	try:
				data = tables[t].xpath(".//ul")[j].xpath(".//li")[n].xpath(".//text()").extract()
			except Exception as e:
				data=[]
			if data == []:
			   continue
			for index in range(len(data)):
			   data[index] = re.sub(r'[\t\n\r]','',data[index])
			   #print str(index) + data[index]
			   if re.match("^\s*$",data[index]):
				continue
			   else:
			   	lineNum = lineNum + 1
			   #print "row : " + str(n) + " col = " + str(j) + " index : " + str(index) + " data = " + data[index]
			   if lineNum == 2 or lineNum ==3:
				if lineNum==2:
            		   		item = vgthksItem()
    					item['hospital'] = 'vgthks'
                           		item['crawlTime'] = unicode(datetime.now().strftime("%Y%m%d %H:%M"))
                           		item['dept'] = dept
                           		item['outpatient'] = outpatient
					item['time'] = 'afternoon'
					mon = re.match(r"(\d*)/([\d]*)",dateList[j-7]).group(1)
					day = re.match(r"(\d*)/([\d]*)",dateList[j-7]).group(2)
					item['date'] = unicode(datetime.now().strftime("%Y")) + mon + day
					item['name'] = data[index]
					item['name'] = re.sub("\(.*",'',item['name'])
					#print item['name']
					#print item['time']
					#print item['outpatient']
				elif lineNum==3:
					#print data[index]
					#if data[index] == u'　':
					if re.match("^\s*$",data[index],re.UNICODE):
						item['full'] = u'可掛號'
					else:	
						item['full'] = data[index]
					#if not re.match(u'額滿',item['full']):
					#	item['full'] = u'可掛號'
					item['link']=response.url
					#jth = j + 1
					#nth = n + 1
					#xpath = '(//table[@id="report"]//ul)[%d]//li[%d]//div[@id="goFillInfoBtn"]' % (jth,nth)
					#try :
					#	element=self.driver2.find_element_by_xpath(xpath)
					#	element.click()
					#	time.sleep(5)
					#	item['link'] = self.driver2.current_url
					#	self.driver2.back()
					#except Exception as e:
					#	item['link'] = "尚未開放預約掛號"
					#	pass
					items.append(item)
					#print item['link']
					#print item['full']
	return items
	if btnLen == btn :
		self.driver.close()



