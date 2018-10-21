"""
created on October 14, 2018
@author: Ehsan Mirzaei
"""

# queries Elasticsearch to calculate the percentage of job postings for Data Engineer and Data Scientist in which the set of skills are mentioned and plots bar charts

import numpy as np
import matplotlib.pyplot as plt
from elasticsearch import Elasticsearch


es = Elasticsearch('ip-10-0-0-20')
skills = ('MapReduce', 'NoSQL', 'Scala', 'C++', 'Java',
          'Spark', 'Hadoop', 'SQL', 'ML', 'Python')

percentage_list_DE = []
percentage_list_DS = []

DE_total = es.search(index='jobs_map', doc_type='posting_doc', body={'query': {
                     'match_phrase': {'job_title': {'query': 'data engineer', 'slop': 2}}}})['hits']['total']
DS_total = es.search(index='jobs_map', doc_type='posting_doc', body={'query': {
                     'match_phrase': {'job_title': {'query': 'data scientist', 'slop': 2}}}})['hits']['total']

for skill in skills:
    DE_skill = es.search(index='jobs_map', doc_type='posting_doc', body={'query': {'bool': {'must': [{'match_phrase': {
                         'job_title': {'query': 'data engineer', 'slop': 2}}}, {'match_phrase': {'description': {'query': skill}}}]}}})['hits']['total']
    DS_skill = es.search(index='jobs_map', doc_type='posting_doc', body={'query': {'bool': {'must': [{'match_phrase': {'job_title': {
                         'query': 'data scientist', 'slop': 2}}}, {'match_phrase': {'description': {'query': skill}}}]}}})['hits']['total']
    DE_percentage = 100*DE_skill/DE_total
    DS_percentage = 100*DS_skill/DS_total
    percentage_list_DE.append(DE_percentage)
    percentage_list_DS.append(DS_percentage)


y_pos = np.arange(len(skills))
plt.barh(y_pos, percentage_list_DE, align='center', alpha=0.9, color='r')
plt.yticks(y_pos, skills)
plt.xticks(np.arange(0, 100, step=25))
plt.rcParams.update({'font.size': 18})
plt.xlabel('Percentage of Job Postings (%)')
plt.title('Data Engineer Skill Sets')
plt.show()
