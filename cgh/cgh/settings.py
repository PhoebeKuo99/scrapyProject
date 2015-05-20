# -*- coding: utf-8 -*-

# Scrapy settings for tzuchi project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'cgh'

SPIDER_MODULES = ['cgh.spiders']
NEWSPIDER_MODULE = 'cgh.spiders'
USER_AGENT = "Safari/537.1"
DOWNLOAD_DELAY = 0.25
#LOG_FILE = 'log.txt'

FEED_URI = 'export.json'
FEED_FORMAT = 'json'
FEED_EXPORTERS = {
   'json': 'cgh.pipelines.UnicodeJsonItemExporter'
   }

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'tzuchi (+http://www.yourdomain.com)'