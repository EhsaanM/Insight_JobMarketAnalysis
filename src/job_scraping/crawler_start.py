"""
created on October 2, 2018
@author: Ehsan Mirzaei
"""

# starts crawling for jobs starting with job_name_start 

from job_crawler import JobCrawler

job_name_start = 'D'
crawler = JobCrawler(job_name_start)
crawler.crawl()
