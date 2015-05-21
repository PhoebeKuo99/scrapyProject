# -*- coding: utf-8 -*-

# Scrapy settings for tzuchi project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'tzuchi'

SPIDER_MODULES = ['tzuchi.spiders']
NEWSPIDER_MODULE = 'tzuchi.spiders'
USER_AGENT = "Safari/537.1"
DOWNLOAD_DELAY = 0.25
SCHEDULER_ORDER = 'BFO'
#LOG_FILE = 'log.txt'
CONCURRENT_REQUESTS = 32
FEED_URI = 'export.json'
FEED_FORMAT = 'json'
FEED_EXPORTERS = {
   'json': 'tzuchi.pipelines.UnicodeJsonItemExporter'
   }

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'tzuchi (+http://www.yourdomain.com)'
