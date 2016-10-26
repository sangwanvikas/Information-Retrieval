#############################################################
#START
#############################################################
import os, sys, datetime, time
# import requests
# from requests.auth import HTTPProxyAuth
# from Queue import Queue, PriorityQueue
import urlparse
print "Resource"
outputDirPath = "C:\\vikas\\CS6200\\HW33\output"

# proxyDict = {
#     'http': 'http://amec.zscaler.philips.com:9480',
#     'https': 'http://amec.zscaler.philips.com:9480'
# }
# auth = HTTPProxyAuth('310230279', 'April@2016')

# print requests.get("https://www.google.com", proxies=proxyDict, auth=auth)
# print requests

# office laptop
tempelatePath = "C:\\vikas\\CS6200\\HW3\Template\\AP89Template.txt"
KeyTermFilePath = "C:\\vikas\\CS6200\\HW3\Key_Terms.txt"
IgnoreWordsFilePath = "C:\\vikas\\CS6200\\HW3\IgnoreWords.txt"
OutlinkPath = 'C:\\vikas\\CS6200\\HW3\outlinks.txt'

# Personal laaptop
tempelatePath = "C:\\vikas\\CS6200\\HW3\Template\\AP89Template.txt"
KeyTermFilePath = "C:\\vikas\\CS6200\\HW3\Key_Terms.txt"
IgnoreWordsFilePath = "C:\\vikas\\CS6200\\HW3\IgnoreWords.txt"
OutlinkPath = 'C:\\vikas\\CS6200\\HW3\outlinks.txt'

InlinksFilePath = "C:/vikas/CS6200/HW3/InlinksFile.txt"

FinalInlinksFilePath = "C:/vikas/CS6200/HW3/Inout/InlinksFile.txt"

#############################################################################

KeyTerms = []
with open(KeyTermFilePath,"r") as handle:
    for line in handle:
        KeyTerms.append(line.strip("\n"))
    handle.close()

IgnoreWords = []
with open(IgnoreWordsFilePath, "r") as handle:
    for line in handle:
        IgnoreWords.append(line.strip("\n"))
    handle.close()


##############################################################################
INDEX_NAME ="finalphase"
TYPE_NAME ="document"

############################################################################

INDEX_REQUEST_BODY= {
    "settings": {
    "index": {
    "max_result_window" : "85000",
    "store": {
        "type": "default"
    },
    "number_of_shards": 1,
    "number_of_replicas": 1
    },
    "analysis": {
        "analyzer": {
            "my_english": {
                "type": "english",
                "stopwords_path": "stoplist.txt",
            }
        }
    }
    }
 }

################################################################

GetByUrl_Request_Body = {
    "query": {
        "match":{
            "_id" : ""
        }
    }
}

################################################################

Update_Request_Body = {
    "doc": {
        "in_links": "",
        "author": ""
    }
}

################################################################

MAPPING_BODY={
    "properties": {
      "docno": {
        "type": "string",
        "store": "true",
        "index": "not_analyzed",
        # "term_vector": "with_positions_offsets_payloads"
      },
      "HTTPheader": {
            "type": "string",
            "store": "true",
            "index": "not_analyzed"
        },
      "title":{
        "type": "string",
        "store": "true",
        "index": "analyzed",
        "term_vector": "with_positions_offsets_payloads"
      },
      "text": {
        "type": "string",
        "store": "true",
        "index": "analyzed",
        "term_vector": "with_positions_offsets_payloads",
        "analyzer": "my_english"
      },
         "html_Source": {
        "type": "string",
        "store": "true",
        "index": "no"
        },
       "in_links": {
            "type": "string",
            "store": "true",
            "index": "no"
        },
        "out_links": {
            "type": "string",
            "store": "true",
            "index": "no"
        },
       "author": {
            "type": "string",
            "store": "true",
            "index": "analyzed"
        },
       "depth": {
        "type": "integer",
        "store": "true",
        "index": "not_analyzed"
      },
    }
}
################################################################

SEARCH_REQUEST_BODY = {
    "fields": [
        "_none"
    ],
    "query": {
        "query_string": {
            "query": "INPUT_TERM"
        }
    },
    "explain": "false"
}
################################################################

COUNT_REQUEST_BODY = {
    "query": {
        "query_string": {
            "query": "INPUT_TERM"
        }
    }
}
################################################################

TF_REQUEST_BODY = {
   "fields": ["_none"],
   "query": {
      "function_score": {
          "query": {
         "match": {
            "text": "INPUT_TERM"
         }
      },
      "functions" : [
          {
          "script_score":{
              "lang":"groovy",
              "script_file":"getTF",
              "params":{
                  "field":"text",
                  "term":"INPUT_TERM"
              }
          }
          }
          ]
          ,
          "boost_mode":"replace"
      }
   },
   "explain": "false",
   "size": "84679"
}
################################################################

SEARCHALL_REQUEST_BODY = {
    "query" : {
        "match_all" : {}
    },
    "fields": [],
    "size": 84678
}
#################################################################

UNIQUE_TERM_REQUEST_BODY = {
    "aggs":{
        "unique_terms":{
            "cardinality":{
                "field":"text"
                }
    }
}
}

query =  {
         "query": {
           "filtered": {
             "query": {
               "match": {
                   "author" : "vikas"
               }
             },
             "filter": {
               "bool": {
                 "must": [{
                   "missing": {
                     "field": "in_links"
                   }
                 }]
               }
             }
           }
         },
           "size":10000
        }



#############################################################
#END
#############################################################
