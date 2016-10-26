
SEARCHALL_REQUEST_BODY2 = {
    "query" : {
        "match_all" : {}
    }
}





ResultDirPath = "C:/vikas/CS6200/HW4/Results/"


W2GInlinksFileCompletePath = "C:/vikas/CS6200/HW4/wt2g_inlinks.txt/wt2g_inlinks.txt"
W2GOutlinksFileCompletePath= "C:/vikas/CS6200/HW4/ProcessedData/Resource/wt2g_outlinks.txt"
W2GSinksCompletePath = "C:/vikas/CS6200/HW4/ProcessedData/Resource/wt2g_sinks.txt"
W2GSinksCompletePath = "C:/vikas/CS6200/HW4/ProcessedData/Resource/wt2g_sinks.txt"

W2GResultCompletePath =  ResultDirPath+ "w2gResult.txt"

MergedProcessedDataDir = "C:/vikas/CS6200/HW4/ProcessedData/Merged/"
MergedInlinksFileCompleteFilePath = MergedProcessedDataDir + "merged_inlinks.txt"
MergedOutlinksFileCompleteFilePath = MergedProcessedDataDir + "merged_outlinks.txt"
MergedSinkFileCompleteFilePath = MergedProcessedDataDir + "merged_sinks.txt"
MergedAllUrlsCompleteFilePath = MergedProcessedDataDir + "allUrls.txt"
MergedResultCompletePath = ResultDirPath + "MergedResult.txt"

HitDirectoryPath = "C:/vikas/CS6200/HW4/Hits/"
Top1000Urls = HitDirectoryPath + "top1000url.txt"
Top1000OutlinksMappaing = HitDirectoryPath + "top1000OutlinksMapping.txt"
Top1000InlinksMappaing = HitDirectoryPath + "top1000InlinksMapping.txt"


HitBaseSetDirectoryPath = "C:/vikas/CS6200/HW4/Hits/BaseSet/"
BaseSetCompleteFilePath = HitBaseSetDirectoryPath + "baseSet.txt"
BaseSetInlinksMappingPath = HitBaseSetDirectoryPath + "baseSetInlinksMapping.txt"
BaseSetOutlinksMappingPath = HitBaseSetDirectoryPath + "baseSetOutlinksMapping.txt"

HitsAuthResultFilePath = ResultDirPath + "/hits_auth.txt"
HitsHubResultFilePath = ResultDirPath + "/hits_hub.txt"



#################################################################################
INDEX_NAME ="finalphase"
TYPE_NAME ="document"

############################################################################

RequestAll_Body =   {
    "query": {
       "missing": {"field": "in_links"}
    }
    }




################################################################

GetByUrl_Request_Body = {
    "query": {
        "match":{
            "_id" : ""
        }
    },
    "size":"100"
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
  "profile": "true",
  "query" : { "filtered": {
     "query": {"match_all": {}},
     "filter": {}
  }
}
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

#############################################
Top100RootSet = {"fields": [
      "out_links",
      "in_links"
   ],
  "query": {
    "bool": {
      "should": [
        {
          "match": {
            "title": "cold war"
          }
        }
      ]
    }
  }
}

###########################################
GetAllMapping = {
        "query" : {
        "match_all" : {}
        },
        "fields": ["in_links","out_links", "author"],
        }

