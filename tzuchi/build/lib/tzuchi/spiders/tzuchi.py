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
from ..items import tzuchiItem
from selenium import webdriver
from ..outpatientMap import outpatientMap
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
#from scrapy.stats import Stats
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"]=("Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0")
class tzuchi(scrapy.Spider):
    name = "tzuchi"
    allowed_domains = ["com.tw"]
    start_urls = [
	"https://app.tzuchi.com.tw/tchw/OpdReg/SecList_DL.aspx",
    ]
    def __init__(self,**kwargs):
	self.driver=webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs')
	#self.driver=webdriver.Firefox()

    def parse(self, response):
	self.driver.get(response.url)
	hospitalLinkList = []
        hospitalList = self.driver.find_elements_by_xpath('//td[@class="menu"]/select[@id="Select2"]/option[@value!="#"]')
        hospitalSel = self.driver.find_elements_by_xpath('//td[@class="menu"]/select[@id="Select2"]')
	for n in range(len(hospitalList)):
	#for n in range(1):
		hospitalLink=hospitalList[n].get_attribute("value")
	#for n in range(len(hospitalList)):
		self.driver.get(hospitalLink)
		time.sleep(5)
        	hospitalList = self.driver.find_elements_by_xpath('//td[@class="menu"]/select[@id="Select2"]/option[@value!="#"]')
		hospital = hospitalList[n].text
		hospital = re.sub(u"慈濟醫院掛號服務",'',hospital)
        	btnList = self.driver.find_elements_by_xpath('//table[@class="style19"]//input[@type="submit"]')
		btnNum = len(btnList)
		#for btn in range(btnNum):
		for btn in range(1):
			btnList[btn].click()
			time.sleep(5)
        		request = Request(self.driver.current_url, callback = self.parse_table)
			request.meta['hospital'] = hospital
        		yield request
			self.driver.get(response.url)
        		btnList = self.driver.find_elements_by_xpath('//table[@class="style19"]//input[@type="submit"]')
        	hospitalList = self.driver.find_elements_by_xpath('//td[@class="menu"]/select[@id="Select2"]/option[@value!="#"]')
			
	self.driver.close()

    def parse_table(self, response):
        baseLink = "https://app.tzuchi.com.tw/tchw/opdreg/"
        items = []
        sel = Selector(response)
 	hospital = response.meta['hospital']	
	### get the name of the dept
        outpatient = sel.xpath('//table/tr').xpath('.//span').xpath('.//text()').extract()
	outpatient = outpatient[0].split(' ')[1]
	dept = outpatient	
        ##一個頁面有四個table
        tables = sel.xpath('//table[@id="example"]')
        #table1 = sel.xpath('//table[@id="Table1"]/tr')
        #print table1.extract()
        #print 'number of table = '+ str(len(tables))
        #sys.exit(0)
        for t in range(len(tables)):
            #print "table = " + str(t)
            ##每個table看有幾個row
	    tableRow = tables[t].xpath('.//tr[contains(@class,"row")]')
            #tableRow = tables[t].xpath('.//tr')

            for n in range(len(tableRow) -1):
                #print "day = " + str(n)
                ##每個row看有幾行            
                tds = tableRow[n+1].xpath('.//td')
                #print "periods = " + str(len(tds))
		date = tables[t].xpath('.//td')[4*n].xpath('.//text()').extract()
                for period in range(len(tds)):
                    #print "period = " + str(period)
		    item_tmp = tzuchiItem()
                    try:
			if (period == 0):
		 	    continue
			elif(period == 1):
                            item_tmp['time'] = 'morning'
			elif (period == 2):
                            item_tmp['time'] = 'afternoon'
			elif (period == 3):
                            item_tmp['time'] = 'night'
                	allText = tables[t].xpath('.//td')[4*n+period].xpath('.//text()').extract()
                	test = tables[t].xpath('.//td')[4*n+period].xpath('.//a').extract()
                        item_tmp['hospital'] = 'tzuchi-' + hospital
                        item_tmp['outpatient'] = outpatient
                        item_tmp['crawlTime'] = unicode(datetime.now().strftime("%Y%m%d %H:%M"))
                        item_tmp['dept'] = dept
                        item_tmp['date'] = unicode(datetime.now().strftime("%Y")) + date[0].replace(u'月','').replace(u'日','')
		    	regNum = -1
			for nth in range(len(allText)):
				#print allText[nth]
				if re.search(u"第.*診",allText[nth]):
					continue
				if not re.match("^\s*[(]", allText[nth]) and not re.match("^\s*\*", allText[nth]) :
                    			item = tzuchiItem()
		    			regNum = 0
					item['full'] = u'已逾掛號'
					item['link']=baseLink
					for kth in range(len(test)):
						if(test[kth].find(allText[nth]) != -1):
							#print allText[nth]
							tmpStr = test[kth].replace(allText[nth],"")
							link = baseLink + re.sub("\".*","",re.sub("^.*?\"","",tmpStr))
							link = link.replace('&amp;','&')
							item['link']=link
							regNum = 1
							break
					item['hospital'] = item_tmp['hospital']
					item['outpatient'] = item_tmp['outpatient']
					item['crawlTime'] = item_tmp['crawlTime']
					item['dept'] = item_tmp['dept']
					item['time'] = item_tmp['time']
					item['date'] = item_tmp['date']
					item['name'] = allText[nth]
					nth2=nth+1
					try :
						if not re.match("^\s*[(]", allText[nth2]) and not re.match("^\s*\*", allText[nth2]) :
							pass
						else:
							while nth2 < len(allText):
								if not re.search(u"第.*診",allText[nth2]):
									item['full'] = allText[nth2]
								nth2+=1
								if not re.match("^\s*[(]", allText[nth2]) and not re.match("^\s*\*", allText[nth2]) :
									break
							
					except Exception as e:
                        			pass 
                         		#items.append(item)
				#elif re.match(r"額滿", allText[nth].encode('utf-8'),re.UNICODE) :
				#elif allText[nth] == u'(預約額滿)' :
				#else:
				#	m = re.search("^\s*[(](.*)[)]",allText[nth])
				#	if m:
				#		if not re.search(u"第.*診",m.group(1)):
				#			item['full'] = m.group(1)
					if regNum == 1:
						yield Request(item['link'], callback = self.parse_shift, meta = {'item': item})
					elif regNum == 0:
						yield item
                    except Exception as e:
                        pass
                    #print item['name']
			
        #return items
                    

    def parse_shift(self, response):
	item = response.meta['item']
        line = Selector(response).xpath('//span[@id="lblRegNum"]').xpath('.//text()').extract()
	if line!=[]:
		line = re.sub("\D",'',line[0])
		item['full']=line
	#else:
	#	item['full']=u'已逾掛號'
	yield item
##output format

#hospital dept date time name

