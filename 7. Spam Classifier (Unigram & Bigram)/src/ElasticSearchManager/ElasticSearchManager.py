##########################################################################################################
# This class:
# Creates Index, Maps index with a document type, Index documents.
##########################################################################################################
# coding=utf-8
import sys

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from time import sleep

reload(sys)
sys.setdefaultencoding('utf8')

sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW7/src/Resource')

import Resource
##########################################################################################################

class ElasticSearchManager():
    SLOPE =  4
    ##########################  Constructor  ######################################
    def __init__(self,indexName, typeName):
        self.client = Elasticsearch()
        self._indexName = indexName
        self._typeName = typeName

    ##########################  CREATES INDEX  ######################################
    def __CreateIndex__(self):
        # DELETE index if already exists
        if self.client.indices.exists(self._indexName):
            print("deleting '%s' index..." % (self._indexName))
            res = self.client.indices.delete(index =  self._indexName)
            # print " response: '%s'" % (res), '\n'

         # CREATE a new index
        print("creating '%s' index..." % (self._indexName))
        res = self.client.indices.create(index = self._indexName,body = Resource.INDEX_REQUEST_BODY)
        # print(" response: '%s'" % (res), '\n')

    ########################### SETS MAPPING FOR INDEX  ##############################
    def __SetMappingForIndex__(self):
        # PUT_MAPPING - Registers specific mapping definition for a specific type.
        print("creating '%s' mapping for..." % (self._typeName))
        res2 = self.client.indices.put_mapping(doc_type = self._typeName,
                                               index =  self._indexName,
                                               body=Resource.MAPPING_BODY)
        print(" response: '%s'" % (res2))

    def __CurrentIndexStats__(self):
        res = self.client.count(index=self._indexName, doc_type=self._typeName)
        documentsIndexedSoFar = res['count']
        print documentsIndexedSoFar
        return res

    def __IndexBulkDoc__(self, bulkList):
        self.__CreateIndex__()
        self.__SetMappingForIndex__()
        sleep(.5)
        success, _ = bulk(self.client, bulkList)

    ######################################################################################################
    # RETRIEVE
    ######################################################################################################

    ########### Returns a LIST of dictionary [{DocNo: XX, TermFrequency: XX, LengthOfDoc: XX}] and
    # total frequency for a term ####
    def __GetTermDetails__(self, termArg):
        # Set 'termArg' in TF_REQUEST_BODY
        functionScorePath = Resource.NGRAM_FEATURE_BODY["query"]["match_phrase"]
        functionScorePath["text"]["query"] = termArg
        functionScorePath["text"]["slop"] = int(ElasticSearchManager.SLOPE)

        res = self.client.search(index=self._indexName, body=Resource.NGRAM_FEATURE_BODY)

        # [
        #     {'docId':"inmail.12",'label':'spam', 'split':'train', 'score':.0345},
        #     {'docId':"inmail.2222",'label':'ham', 'split':'test', 'score':.0345}
        # ]
        TermDetailForAllDocsList = []

        for hit in res["hits"]["hits"]:
            # Fetch docId, TF (score) for the termArg, document length, total frequency
            docId =  hit["_id"]
            score = hit["_score"]
            label = hit['fields']['label'][0]
            split = hit['fields']['split'][0]

            TermDetails = {'docId':docId,'label':label, 'split':split, 'score':score}
            TermDetailForAllDocsList.append(TermDetails)

        return TermDetailForAllDocsList

    def __GetAllUnigramsAsFeatures__(self):
        requestBody = Resource.REQUEST_BODY_FIND_ALL_FEATURES
        # "aggregations": {
        #     "features": {
        #         "doc_count_error_upper_bound": 0,
        #         "sum_other_doc_count": 0,
        #         "buckets": [
        #             {
        #                 "key": "http",
        #                 "doc_count": 4274
        #             },
        #             {
        #                 "key": "s",
        #                 "doc_count": 3958
        #             }
        #         ]
        #     }
        # }
        res = self.client.search(self._indexName, self._typeName, body = requestBody, search_type = "count")
        return res

    def __GetTermVectorForDoc__(self, docId):
        requestBody = Resource.REQUEST_BODY_TERMVECTOR_FOR_DOC
        requestBody['_id'] = docId
        res = self.client.termvectors(self._indexName, self._typeName, body = requestBody)
        # u'term_vectors': {
        # "text": {
        #      "terms": {
        #         "confirm": {
        #            "term_freq": 1
        #         },
        #         "30": {
        #            "term_freq": 1
        #         },
        #         "approv": {
        #            "term_freq": 1
        #         }
        #      }
        #   },
        # u'split': {u'terms': {u'train': {u'term_freq': 1}}}, u'label': {u'terms': {u'spam': {u'term_freq': 1}}},
        # }
        return res
################################################################################################################
################################################################################################################

##########################################################################################################
# END
##########################################################################################################

# ESMgrObject = ElasticSearchManager(Resource.INDEX_NAME, Resource.TYPE_NAME)
# ESMgrObject.__GetAllUnigramsAsFeatures__()
# ESMgrObject.__GetTermVectorForDoc__('inmail.1')