import sys
from elasticsearch import Elasticsearch, helpers
import json
from pprint import pprint
import subprocess
import time


#subprocess.call("./elasticsearch-6.2.4/bin/elasticsearch")
#time.sleep(60)

def main():
    input_file = sys.argv[1]
    es = Elasticsearch()
    
    body = json.loads("""{
        "mappings": {
          "posting_doc":{
            "properties":{
                "url":{"type":"string"},
                "company": {"type":"string"},
                "title":{"type":"string"},
                "location":{"type":"string"},
                "Description": {"type":"string"}
            }
          }
        }
    }""")
    es.indices.create(index = "job_postings",ignore=400, body = body)
    actions = []
    for line in open(input_file):
        try:
            posting = json.loads(line)
        except:
#            import pdb; pdb.set_trace()
            continue
        actions.append({
            "_index": "job_postings",
            "_type": "posting_doc",
            "_source": {
                "url": posting['url'],
                "Company": posting['Company'],
                "title": posting['title'],
                "location": posting['location'],
                "Description": posting['Description']
            }
        })

#    pprint(actions)
    helpers.bulk(es, actions)


if __name__ == "__main__":
    main()
