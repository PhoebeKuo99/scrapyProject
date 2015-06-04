# -*- coding: utf-8 -*-

# Scrapy settings for mmh project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'mmh'

SPIDER_MODULES = ['mmh.spiders']
NEWSPIDER_MODULE = 'mmh.spiders'

USER_AGENT = "Safari/537.1"
DOWNLOAD_DELAY = 0.25
CONCURRENT_REQUESTS=8
#LOG_FILE = 'log.txt'

FEED_URI = 'export.json'
FEED_FORMAT = 'json'
FEED_EXPORTERS = {
   'json': 'mmh.pipelines.UnicodeJsonItemExporter'
      }
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'mmh (+http://www.yourdomain.com)'
