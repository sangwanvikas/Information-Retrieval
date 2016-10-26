##########################################################################################################
# Page Rank - For Merged documents (__GenerateInlinksMappingFile__)
#   1. Get all Urls
#   2. Get all inlinksMapping
#   3. Get all outlinksMapping
#   4. Get sinkUrlsMapping

# Hits
# 1. Get 1000 documents by ranking all pages using in built IDF of ElasticSearch
##########################################################################################################

import sys
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from decimal import Decimal
reload(sys)
sys.setdefaultencoding('utf8')

# Personal laaptop
sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW4/src/Resource')
sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW4/src/Utility')


import Resource, random
import Utility
##########################################################################################################

class ElasticSearchManager():

    ##########################  Constructor  ######################################
    def __init__(self,indexName, typeName):
        self.client = Elasticsearch()
        self._indexName = indexName
        self._typeName = typeName

        self._utilityObj = Utility.Utility()
        self._inlinksMappingDir = {}
        self._outlinksMappingDir = {}
        self._sinkUrls = []
        self._allUrls = []

    ######################################################################################################
    # Page Rank - Merged documents
    ######################################################################################################

    def __CurrentIndexStats__(self):
        res = self.client.count(index=self._indexName, doc_type=self._typeName)
        documentsIndexedSoFar = res['count']
        print documentsIndexedSoFar
        return res

    def __GenerateInlinksMappingFile__(self):
        print "====== Downloading Merged Index & Generating Mappings for it ====="
        hits = self.__GetAll__()
        c = 0
        print "ffffffffffff", len(hits)
        for hit in hits:
            c+=1
            if c < len(hits):
                print "Processing document #", c
                if hit.has_key("fields"):
                    documentUrl = hit["_id"]
                    if hit["fields"].has_key("in_links"):
                        inlinksText = hit["fields"]["in_links"][0]
                    if hit["fields"].has_key("out_links"):
                        outlinksText =  hit["fields"]["out_links"][0]
                        outlinksText = outlinksText.replace("#/", " ")

                    self._inlinksMappingDir[documentUrl] = inlinksText

                    if (len(outlinksText.split(" ")) > 1 or len(outlinksText.split("#/")) > 1) and "http" in outlinksText:
                        print "hiii"
                        self._outlinksMappingDir[documentUrl] = outlinksText
                    else:
                        self._sinkUrls.append(documentUrl)

                    self._allUrls.append(documentUrl)

        print "All Mappings for Merged Index loaded into memory successfully !"
        print "Dumping inlinksMapping, outlinksMapping, sinUrls and allUrls to..", Resource.MergedProcessedDataDir
        print len(self._sinkUrls), Resource.MergedSinkFileCompleteFilePath
        self._utilityObj.__DumpDictDataIntoTextFile2__(Resource.MergedInlinksFileCompleteFilePath, self._inlinksMappingDir)
        self._utilityObj.__DumpDictDataIntoTextFile__(Resource.MergedOutlinksFileCompleteFilePath,self._outlinksMappingDir)
        self._utilityObj.__DumpListDataIntoTextFile__(Resource.MergedSinkFileCompleteFilePath,self._sinkUrls)
        self._utilityObj.__DumpListDataIntoTextFile__(Resource.MergedAllUrlsCompleteFilePath,self._allUrls)

    def __GetAll__(self):
        print "==== Fetching documentd from Merged index ===="
        data = self.client.search(index=self._indexName, doc_type=self._typeName, scroll='60s', size=500, body=Resource.GetAllMapping)

        tweets = []
        tweets += data['hits']['hits']
        fscroll_size = data['hits']['total']
        while (fscroll_size > 0):
            scroll_id = data['_scroll_id']
            rs = self.client.scroll(scroll_id=scroll_id, scroll='60s')
            tweets += rs['hits']['hits']
            scroll_size = len(rs['hits']['hits'])
            fscroll_size -= scroll_size
            print "Documents fetched so far..", len(tweets)
            if len(tweets) >= 59117:
                return tweets

        return tweets

    ######################################################################################################
    # Hits
    ######################################################################################################
    def _Get1000DocForRootSet__(self):
        print "===== Fetching Root Set of 1000 documents for HITS.. ====="
        page = self.client.search(index=self._indexName, doc_type=self._typeName, size=1000, body=Resource.Top100RootSet)

        print "Fetching top 1000 docs for BastSet.."
        print "Creating files for InlinksMapping, OutlinksMapping, SinkUrls .."
        # print len(page["hits"]["hits"])

        hitsHits = page["hits"]["hits"]
        urls = []
        outlinksMapping ={}
        inlinksMapping = {}
        for item in hitsHits:
            currentUrl = item["_id"]
            outlinksText = item["fields"]['out_links'][0].replace("#/"," ")
            inlinksText = item["fields"]['in_links'][0]

            if not currentUrl in urls:
                urls.append(currentUrl)
                outlinksMapping[currentUrl] = outlinksText
                inlinksMapping[currentUrl] = inlinksText

        print "Dumping files for Root Set of 1000 to directory ..", Resource.HitDirectoryPath
        self._utilityObj.__DumpListDataIntoTextFile__(Resource.Top1000Urls, urls)
        self._utilityObj.__DumpDictDataIntoTextFile__(Resource.Top1000OutlinksMappaing, outlinksMapping)
        self._utilityObj.__DumpDictDataIntoTextFile__(Resource.Top1000InlinksMappaing, inlinksMapping)
##########################################################################################################
# END
##########################################################################################################

ESMgrObject = ElasticSearchManager(Resource.INDEX_NAME, Resource.TYPE_NAME)
# Run to get mappings for Page Rank - merged indexed.
# 1.1 run independent
ESMgrObject.__GenerateInlinksMappingFile__()


# Run to get top 1000 Doc for root set.
# 1.2 run independent
# ESMgrObject._Get1000DocForRootSet__()

# ESMgrObject.__GetAll__()
