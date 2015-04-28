# -*- coding: utf-8 -*-

# Scrapy settings for cch project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'cch'

SPIDER_MODULES = ['cch.spiders']
NEWSPIDER_MODULE = 'cch.spiders'

USER_AGENT = "Safari/537.1"
DOWNLOAD_DELAY = 0.25
SCHEDULER_ORDER = 'BFO'
#LOG_FILE = 'log.txt'

FEED_URI = 'export.json'
FEED_FORMAT = 'json'
FEED_EXPORTERS = {
   'json': 'cch.pipelines.UnicodeJsonItemExporter'
      }
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'cch (+http://www.yourdomain.com)'
