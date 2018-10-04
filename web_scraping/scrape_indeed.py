from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import re
import csv
import time
from random import randint
import sys
import json
import datetime



# Gets the urls for job titles (alphabetic order)
def getJobTitles(url):
    url_list = []
    extra_titles = ['Data-Scientist','Machine-Learning','Data-Engineer']
    try:
        html = urlopen(url)
    except HTTPError as e:
        return None
    try:
        bs = BeautifulSoup(html.read(), 'html.parser')
        jobtitle = bs.find_all('a',{'class':'jobTitle'})
        for link in jobtitle:
            if 'href' in link.attrs:
                url_list.append('https://www.indeed.com'+link.attrs['href'])
        for i in range(len(extra_titles)):
                url_list.append('https://www.indeed.com/q-'+extra_titles[i]+'-jobs.html')
    except AttributeError as e:
        return none
    return(url_list)


# gets urls for each job posting
def get_posting_urls(url):
    posting_url = set()
    posting_data = dict()
    urls = getJobTitles(url)
    for u in urls:
        print(len(posting_url))
        for i in range(0,2):
            itr = 1
            while itr == 1:
                time.sleep(randint(1,2))
                tries = 1
                while tries < 5:
                    try:
                        html = urlopen(u)
                        tries = 6
                    except HTTPError as e:
                        time.sleep(3*tries)
                bs = BeautifulSoup(html.read(), 'html.parser')
                jobtitle_links = bs.find_all('a',{'rel':'noopener nofollow'})
                company_names = bs.find_all('span',{'class':'company'})
                job_locations = bs.find_all(['div','span'],{'class':'location'})
#                j = 0
                for j,link in enumerate(jobtitle_links):
                    if 'href' in link.attrs:
                        if 'https://www.indeed.com'+link.attrs['href'] not in posting_url:
                            posting_url.add('https://www.indeed.com'+link.attrs['href'])
                            job_title = link.attrs['title']
                            try:
                                company_name = company_names[j].get_text().replace('\n',' ')
                                company_name = company_name.replace('"',' ')
                                job_location = job_locations[j].get_text().replace('\n',' ')
                                job_location = job_location.replace('"',' ')
                                posting_data['https://www.indeed.com'+link.attrs['href']] = [job_title,company_name,job_location]
                            except:
                                print(u)
#                    j += 1
                next_page = bs.find_all('a',{'onmousedown':'addPPUrlParam && addPPUrlParam(this);'})
                try:
                    u = 'https://www.indeed.com' + next_page[-1].attrs['href']
                except:
                    print(next_page)
                next_search = bs.find_all('p',{'class':'dupetext'})
                if len(next_search) != 0:
                    u = 'https://www.indeed.com' + next_search[0].find('a').attrs['href']
                    itr = 0
    return posting_data



def get_job_description(url):
    current_date = datetime.datetime.now().strftime('%Y/%m/%d')
    job_data = get_posting_urls(url)
    time.sleep(10)
    for key in job_data:
        tries = 1
        while tries < 5:
            try:
                html = urlopen(key)
                tries = 6
            except HTTPError as e:
                time.sleep(3*tries)
#            w = csv.writer(open("output2.csv", "w"))
#            for key, val in job_data.items():
#                w.writerow([key, val[0],val[1],val[2],val[3]])
#            sys.exit()
        bs = BeautifulSoup(html.read(), 'html.parser')
        if not bs.find('div',{'class':re.compile('\s*jobsearch-JobComponent-description\s*')}):
            continue
        job_description = bs.find('div',{'class':re.compile('\s*jobsearch-JobComponent-description\s*')}).get_text().replace('"',' ')
        job_description = job_description.replace('\n',' ')
#        job_title = bs.find('h3',{'class':re.compile('\s*icl-u-xs-mb--xs icl-u-xs-mt--none jobsearch-JobInfoHeader-title\s*')}).get_text()
#        company_name = bs.find('div',{'class':re.compile('\s*icl-u-lg-mr--sm icl-u-xs-mr--xs\s*')}).get_text()
#        job_location = bs.find('span',{'class':re.compile('\s*icl-JobResult-jobLocation\s*')}).get_text()
        job_data[key].append(job_description)
        bs_string = str(bs).replace('\n',' ')
        bs_string = bs_string.replace('"',' ')
        job_data[key].append(bs_string)
        job_data[key].append(current_date)
#    w = csv.writer(open("output2.csv", "w"))
#    for key, val in job_data.items():
#        w.writerow([key, val[0],val[1],val[2]],val[3])
    with open('output_C2.json', 'w') as f:
        for key,val in job_data.items():
            if len(val) == 6:
                f.write('{"url": "%s", "job_title": "%s", "company": "%s","location": "%s","description": "%s","html": "%s","date": "%s"}\n'%(key,val[0],val[1],val[2],val[3],val[4],val[5]))
#        json.dump(job_data,f)

if __name__ == '__main__':
    get_job_description('https://www.indeed.com/find-jobs.jsp?title=C')
#if title == None:
#    print('Title could not be found')
#else:
#    print(title)
