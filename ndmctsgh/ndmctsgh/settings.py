# -*- coding: utf-8 -*-

# Scrapy settings for ndmctsgh project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'ndmctsgh'

SPIDER_MODULES = ['ndmctsgh.spiders']
NEWSPIDER_MODULE = 'ndmctsgh.spiders'

USER_AGENT = "Safari/537.1"
DOWNLOAD_DELAY = 0.25
CONCURRENT_REQUESTS=8
#LOG_FILE = 'log.txt'

FEED_URI = 'export.json'
FEED_FORMAT = 'json'
FEED_EXPORTERS = {
   'json': 'ndmctsgh.pipelines.UnicodeJsonItemExporter'
      }
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'ndmctsgh (+http://www.yourdomain.com)'
