# -*- coding: utf-8 -*-
"""Scrape jobs from indeed.com.
"""
import datetime
import re
from urlparse import urljoin

from scrapy import Request, Selector
import scrapy

from remotor.items import JobItem


class IndeedSpider(scrapy.Spider):
    """Spider for indeed.com

    This is a simple site with a single page of jobs, with links to the ads.

    """
    name = "indeed"
    root = 'https://www.indeed.com'
    allowed_domains = ["www.indeed.com"]
    start_urls = ['https://www.indeed.com/jobs?q=python&l=Remote']

    job_selector = '.row, .result'

    def parse(self, response):
        """Get the joblinks and hand them off.
        """
        s = Selector(response)
        jobs = s.css(self.job_selector)
        for job in jobs:
            joblink = job.xpath('h2/a/@href').extract_first()
            if not joblink:
                continue
            item = JobItem()
            item['url'] = urljoin(self.root, joblink)
            item['title'] = job.xpath('h2/a/@title').extract_first()
            item['text'] = job.xpath(
                'table//span[@class="summary"]/text()').extract()
            request = Request(
                item['url'],
                callback=self.parse_job,
                meta={'item': item},
                )
            yield request

    def parse_job(self, response):
        """Parse a joblink into a JobItem.
        """
        item = response.meta['item']
        item['site'] = 'Indeed'
        s = Selector(response)
        item['text'].extend(s.xpath('//p/text()').extract())
        item['text'].extend(s.xpath('//ul/text()').extract())
        item['text'].extend(s.xpath('//span/text()').extract())
        try:
            posted = s.xpath('//span[@id="lblJobPostDate"]/text()').extract_first()
            parsed = datetime.datetime.strptime(posted, '%m/%d/%y').isoformat()
            item['date_added'] = parsed
        except Exception as e:
            self.logger.error(e)
        yield item
