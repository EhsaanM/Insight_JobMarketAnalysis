"""
created on September 30, 2018
@author: Ehsan Mirzaei
"""

# crawls for jobs starting with 'letter'

from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
import re
import time
from random import randint
import sys
import json
import datetime
import geocoder
from geopy.geocoders import ArcGIS
from http.client import IncompleteRead


class JobCrawler:
    def __init__(self, letter):
        self.start_letter = letter
        self.url = 'https://www.indeed.com/find-jobs.jsp?title=' + letter

    def get_job_titles(self):
        self.url_list = []
#    extra_titles = ['Data-Scientist','Machine-Learning','Data-Engineer']
        try:
            html = urlopen(self.url)
        except HTTPError as e:
            return None
        try:
            bs = BeautifulSoup(html.read(), 'html.parser')
            jobtitle = bs.find_all('a', {'class': 'jobTitle'})
            for link in jobtitle:
                if 'href' in link.attrs:
                    self.url_list.append(
                        'https://www.indeed.com'+link.attrs['href'])
#        for i in range(len(extra_titles)):
#                url_list.append('https://www.indeed.com/q-'+extra_titles[i]+'-jobs.html')
        except AttributeError as e:
            return None
        return(self.url_list)

    def crawl(self):
        posting_urls = set()
        for u in self.get_job_titles():
            job_title = u.split('-')
            job_title = job_title[1:-1]
            posting_urls = self.get_job_posting_links(job_title)
            self.get_job_posting_data(posting_urls)

    def get_job_posting_links(self, job_title):
        posting_urls = set()
        for i in range(100):
            u = 'https://www.indeed.com/jobs?q=' + \
                '+'.join(job_title) + '&start=' + str(i*10)
            tries = False
            while tries is False:
                try:
                    html = urlopen(u)
                    tries = True
                except HTTPError as e:
                    print('HTTPError!')
                    time.sleep(3)
                except URLError as e:
                    print('URLError!')
                    time.sleep(3)
            try:
                bs = BeautifulSoup(html.read(), 'html.parser')
            except IncompleteRead:
                print('Incomplete read ...')
                continue
            try:
                jobtitle_links = bs.find_all('a', {'rel': 'noopener nofollow'})
            except:
                print('job posting links not found!')
                continue
            for j, link in enumerate(jobtitle_links):
                if 'href' in link.attrs and 'https://www.indeed.com'+link.attrs['href'] not in posting_urls:
                    posting_urls.add(
                        'https://www.indeed.com'+link.attrs['href'])
        return posting_urls

    def get_job_posting_data(self, posting_urls):
        l = ArcGIS()
        posting_data = dict()
        geo_dict = dict()
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        file_name = 'job_postings_%s_%s.json' % (
            self.start_letter, current_date)
        for i, url in enumerate(posting_urls):
            tries = False
            while tries is False:
                try:
                    html = urlopen(url)
                    tries = True
                except HTTPError as e:
                    print('HTTPError!')
                    time.sleep(3)
                except URLError as e:
                    print('URLError!')
                    time.sleep(3)
            try:
                bs = BeautifulSoup(html.read(), 'html.parser')
            except IncompleteRead:
                print('Incomplete read ...')
                continue
            try:
                if len(bs.find_all('span', {'class': 'indeed-apply-widget'})) == 0:
                    company = bs.find('h4', {'class': 'jobsearch-CompanyReview--heading'}).get_text(
                    ).replace('\n', ' ').replace('"', ' ').strip()
                else:
                    company = bs.find_all('span', {'class': 'indeed-apply-widget'})[
                        0]['data-indeed-apply-jobcompanyname'].replace('\n', ' ').replace('"', ' ').strip()
                job_title = bs.find('h3', {'class': 'icl-u-xs-mb--xs icl-u-xs-mt--none jobsearch-JobInfoHeader-title'}
                                    ).get_text().replace('\n', ' ').replace('"', ' ').strip()
                job_title = job_title.replace('#', ' ').replace('\\', ' ')
                city = bs.find('title').get_text().split(
                    '-')[-2].replace('\n', ' ').replace('"', ' ').replace('#', ' ').replace('\\', ' ').strip()
                if city not in geo_dict.keys():
                    try:
                        ll = l.geocode(city, timeout=10)
                        geo_location = [ll.latitude, ll.longitude]
                        geo_dict[city] = geo_location
                    except:
                        geo_location = [0, 0]
                else:
                    geo_location = geo_dict[city]
                job_description = bs.find('div', {'class': re.compile(
                    '\s*jobsearch-JobComponent-description\s*')}).get_text().replace('"', ' ').replace('\n', ' ').strip()
                job_description = job_description.replace(
                    '\\', ' ').replace('#', ' ')
                posting_data[url] = [job_title, company, city, ','.join(
                    str(e) for e in geo_location), job_description, current_date]
            except:
                print(url)
                continue
            if i % 1000 == 0:
                self.write_to_file(posting_data, file_name)
                posting_data = {}
        self.write_to_file(posting_data, file_name)

    def write_to_file(self, posting_data, file_name):
        with open(file_name, 'a') as f:
            for key, val in posting_data.items():
                if len(val) == 6:
                    f.write('{"url": "%s", "job_title": "%s", "company": "%s","city": "%s","location": "%s","description": "%s","date": "%s"}\n' % (
                        key, val[0], val[1], val[2], val[3], val[4], val[5]))
