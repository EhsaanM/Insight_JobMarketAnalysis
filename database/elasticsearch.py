import os
from elasticsearch import Elasticsearch, helpers
import json
from pprint import pprint
import subprocess
import time
import boto3
from smart_open import smart_open
from subprocess import call



# gets the names of the files in s3 bucket to be ingested into elasticsearch
def get_input_files():
    file_names = []
    session = boto3.Session(profile_name='default')
    s3 = session.resource('s3')
    bucket = s3.Bucket('job-market')
    for obj in bucket.objects.filter(Prefix='Not-ingested/'):
        if obj.key == 'Not-ingested/':
            continue
        file_names.append(obj.key)
    return file_names



# creates the mapping for indexing
def mapping():
    body = json.loads("""{
        "mappings": {
          "posting_doc": {
            "properties": {
                "url": {
                  "type": "keyword"
                },
                "job_title": {
                  "type": "text"
                },
                "company": {
                  "type": "text"
                },
                "city": {
                  "type": "text"
                },
                "location": {
                  "type": "geo_point"
                },
                "description": {
                  "type": "text",
                  "analyzer": "english"
                },
                "date": {
                  "type": "date",
                  "format": "yyyy-MM-dd"
                }
            }
          }
        }
    }""")
    return body



# Ingests json files to Elasticsearch
def ingestion():
    es = Elasticsearch('ip-10-0-0-20')
    input_files = get_input_files()
    es.indices.create(index = "jobs_piechart",ignore=400, body = mapping())
    bucket_name = "job-market"
    for file in input_files:
        actions = []
        with smart_open("s3://"+bucket_name+"/"+file, 'r') as f:
            for line in f:
                try:
                    posting = json.loads(line.replace('\\','').replace('#',''))
                except:
#                   import pdb; pdb.set_trace()
                    continue
                actions.append({
                    "_index": "jobs_piechart",
                    "_type": "posting_doc",
                    "_id": posting['url'][:200],
                    "_source": {
                        "url": posting['url'],
                        "job_title": posting['job_title'],
                        "company": posting['company'],
                        "city": posting['city'],
                        "location": posting['location'],
                        "description": posting['description'],
                        "date": posting['date']
                    }
                })
            if len(actions)  % 1000 == 0:
                helpers.bulk(es, actions)
                actions = []
        helpers.bulk(es, actions)
        os.system('aws s3 mv s3://job-market/'+file+' s3://job-market/Ingested/'+file.split('/')[1])



if __name__ == "__main__":
    ingestion()
