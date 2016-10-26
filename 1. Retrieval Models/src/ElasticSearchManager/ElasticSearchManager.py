##########################################################################################################
# This class:
# Creates Index, Maps index with a document type, Index documents
# Perform GET for _search (Score in each doc), _count (DF) and _termvector (TF) methods
##########################################################################################################

import sys
from elasticsearch import Elasticsearch
from decimal import Decimal

# sys.path.append('C:\Users\\vikas\Dropbox\CS6200_V_Sangwan\HW1\Common')
# sys.path.append('C:\Users\\vikas\Dropbox\CS6200_V_Sangwan\HW1\Enum')

sys.path.append('C:\Users\\310230279\Dropbox\CS6200_V_Sangwan\HW1\src\Common')
sys.path.append('C:\Users\\310230279\Dropbox\CS6200_V_Sangwan\HW1\src\\Enum')
sys.path.append('C:\Users\\310230279\Dropbox\CS6200_V_Sangwan\HW1\src\\Model')


import Resource
from Enum import ElasticSearchUsedFor
from LaplaceSmoothing import LaplaceSmoothing
import json
##########################################################################################################

class ElasticSearchManager():

    ##########################  Constructor  ######################################
    def __init__(self,indexName, typeName,ESUsageType):
        self.client = Elasticsearch()
        self._indexName = indexName
        self._typeName = typeName

        self._uniqeTermInCorpus = 0
        self._totalNoOfDocsInCorpus = 0
        self._avgDocumentLength = 0
        self._lengthOfAllDocuments = 0

        if ESUsageType is ElasticSearchUsedFor.Indexing:
            self.__CreateIndex__()
            self.__SetMappingForIndex__()

        else:
            # self._uniqeTermInCorpus = self.__GetUniqueTermsInCorpus__()
            # self._avgDocumentLength, self._totalNoOfDocsInCorpus, self._lengthOfAllDocuments = self.__FindAverageLength__()
            # Needs to be removed
            self._totalNoOfDocsInCorpus = 84678
            self._avgDocumentLength = 247.7
            self._lengthOfAllDocuments = 84678 * 247.7



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
        #Adds a typed JSON document in a specific index, making it searchable.
        res = self.client.index(index=self._indexName,doc_type=self._typeName,id=documentId,body=doc)

    def __CurrentIndexStats__(self):
        res = self.client.count(index=self._indexName, doc_type=self._typeName)
        return res

    ######################################################################################################
    # RETRIEVE
    ######################################################################################################

    ######  Return INT - the average length of the entire Corpus   ##########
    def __FindAverageLength__(self):
        documentList = self.__GetAllDocumentIdsFromCorpus__()
        counter =0
        cumulativeSum = 0

        laplaceSmoothingObj = LaplaceSmoothing(self._uniqeTermInCorpus)
        dictForLaplaceSmoothing = {}

        for document in documentList:
            # Fetch docId, docLength for each document to calculate total length of corpus and
            # average length of a document
            counter = counter + 1
            docId = document["_id"]
            dpcLeng = self.__FindDocumentLength__(docId)

            cumulativeSum = cumulativeSum + dpcLeng
            dictForLaplaceSmoothing[docId] =  float(laplaceSmoothingObj.__CalculateDtForLaplaceSmoothing__(0, dpcLeng))

        with open('filename.txt', 'w') as handle:
            json.dump(dictForLaplaceSmoothing, handle)
            handle.close()

        with open('_avgDocumentLength.txt', 'w') as handle:
            json.dump({"_avgDocumentLength": cumulativeSum/counter}, handle)
            handle.close()

        with open('_totalNoOfDocsInCorpus.txt', 'w') as handle:
            json.dump({"_totalNoOfDocsInCorpus": counter}, handle)
            handle.close()

        with open('_lengthOfAllDocuments.txt', 'w') as handle:
            json.dump({"_lengthOfAllDocuments": cumulativeSum}, handle)
            handle.close()


        return cumulativeSum/counter, counter, cumulativeSum

    ##########  Return a list of all DOcuments (hits) in the Corpus  ################################
    def __GetAllDocumentIdsFromCorpus__(self):
        res = self.client.search(index=self._indexName, body=Resource.SEARCHALL_REQUEST_BODY)
        return res["hits"]["hits"]


    ########## Returns INT - count of all unique terms in the corpus - for Laplace Smoothing ########
    def __GetUniqueTermsInCorpus__(self):
        res = self.client.search(index=self._indexName, body=Resource.UNIQUE_TERM_REQUEST_BODY)
        uniqueTermsCount = res["aggregations"]["unique_terms"]["value"]

        with open('_uniqeTermInCorpus.txt', 'w') as handle:
            json.dump({"_uniqeTermInCorpus":uniqueTermsCount},handle)
            handle.close()

        return uniqueTermsCount


    ########### Returns a LIST of dictionary [{DocNo: XX, TermFrequency: XX, LengthOfDoc: XX}] and
    # total frequency for a term ####
    def __GetTermDetailsFromCorpus__(self, termArg):
        # Set 'termArg' in TF_REQUEST_BODY
        functionScorePath = Resource.TF_REQUEST_BODY["query"]["function_score"]
        functionScorePath["query"]["match"]["text"] = termArg
        functionScorePath["functions"][0]["script_score"]["params"]["term"] = termArg

        res = self.client.search(index=self._indexName, body=Resource.TF_REQUEST_BODY)

        # List of Dictionaries {DocNo: XX, TermFrequency: XX, LengthOfDoc: XX}
        TermDetailForAllDocsList = []
        totalFrequency = 0
        totalLength = 0

        for hit in res["hits"]["hits"]:
            # Fetch docId, TF (score) for the termArg, document length, total frequency
            docId =  hit["_id"]
            score = hit["_score"]
            docLength = self.__FindDocumentLength__(docId)
            totalFrequency = totalFrequency + (score)

            totalLength = totalLength + docLength
            TermDetails = {"DocNo": docId, "TermFrequency": score, "LengthOfDoc": docLength}
            TermDetailForAllDocsList.append(TermDetails)

        return TermDetailForAllDocsList, totalFrequency

    ########### Returns INT - length of the given document excluding stop words  ###################
    def __FindDocumentLength__(self, documentIdArg):
        res = self.client.termvectors(index=self._indexName, doc_type=self._typeName, id=documentIdArg)

        wordCount = 0

        if res["term_vectors"].has_key("text"):
            terms = res["term_vectors"]["text"]["terms"]
            for term in terms:
                wordCount = wordCount + terms[term]["term_freq"]

        return wordCount

################################################################################################################
################################################################################################################

##########################################################################################################
# END
##########################################################################################################