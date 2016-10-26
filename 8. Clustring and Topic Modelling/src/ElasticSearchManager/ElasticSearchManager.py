##########################################################################################################
# This class:
# Creates Index, Maps index with a document type, Index documents
# Perform GET for _search (Score in each doc), _count (DF) and _termvector (TF) methods
##########################################################################################################

import sys
from elasticsearch import Elasticsearch
from decimal import Decimal

sys.path.append('C:\Users\\vikas\Dropbox\CS6200_V_Sangwan\HW8\src\Resource')
sys.path.append('C:\Users\\vikas\Dropbox\CS6200_V_Sangwan\HW8\src\Enum')

import Resource
##########################################################################################################

class ElasticSearchManager():

    ##########################  Constructor  ######################################
    def __init__(self,indexName, typeName, type):
        self.client = Elasticsearch()
        self._indexName = indexName
        self._typeName = typeName

        self._uniqeTermInCorpus = 0
        self._totalNoOfDocsInCorpus = 0
        self._avgDocumentLength = 0
        self._lengthOfAllDocuments = 0

        if type == 1:
            print type
            self.__CreateIndex__()
            self.__SetMappingForIndex__()

    ##########################  CREATES INDEX  ######################################
    def __CreateIndex__(self):
        # DELETE index if already exists
        if self.client.indices.exists(self._indexName):
            print("deleting '%s' index..." % (self._indexName))
            res = self.client.indices.delete(index =  self._indexName)
            print " response: '%s'" % (res), '\n'

         # CREATE a new index
        print("creating '%s' index..." % (self._indexName))
        res = self.client.indices.create(index = self._indexName,body = Resource.INDEX_REQUEST_BODY)
        print(" response: '%s'" % (res), '\n')

    ########################### SETS MAPPING FOR INDEX  ##############################
    def __SetMappingForIndex__(self):
        # PUT_MAPPING - Registers specific mapping definition for a specific type.
        print("creating '%s' mapping for..." % (self._typeName))
        res2 = self.client.indices.put_mapping(doc_type = self._typeName,
                                               index =  self._indexName,
                                               body=Resource.MAPPING_BODY)
        print(" response: '%s'" % (res2))

    ########################### GENERATE LOGICAL DOC TO BE INDEXED   #################
    def __ConsituteDocument__(self,documentId, documentText):
        doc = {
            "docno": documentId,
            "text": documentText
        }
        return doc

    ##########################  PERFORMS INDEXING   ######################################
    def __UploadDocumentToIndex__(self,docCounterForTesting,documentId, documentText):
        doc = self.__ConsituteDocument__(documentId, documentText)
        res = self.client.index(index=self._indexName,doc_type=self._typeName,id=documentId,body=doc)

    def __CurrentIndexStats__(self):
        res = self.client.count(index=self._indexName, doc_type=self._typeName)
        return res

    ######################################################################################################
    # RETRIEVE
    ######################################################################################################
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

    ################################################################################################################
    def __GetDocumentText__(self, docId):
        # {u'_source': {u'text': u"  fatalities have increased an estimated 31 percent o}}
        res = self.client.get_source(index=self._indexName, doc_type=self._typeName, id = docId)
        return res['text']

    #####################################################################################################
    def __GetHitsForAllDocuments__(self):
        print "Fetching hits for text for all documents from ElasticSearch ..."
        requestBody = Resource.REQUEST_BODY_FIND_TEXT_FOR_ALLDOCS
        res = self.client.search(index=self._indexName, doc_type=self._typeName, body = requestBody)
        return res['hits']['hits']

################################################################################################################

##########################################################################################################
# END
##########################################################################################################
