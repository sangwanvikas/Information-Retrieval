########################################################################
# I am using Iterative Page Rank algorithm
# 1. Page rank for Resource
# 2. Page rank for Merged Index
# Compute the PageRank of every page in your crawl (merged team index).
# List the top 500 pages by the PageRank score.
# Get the graph linked by the in-links in file resources/wt2g_inlinks.txt.zip
# Compute the PageRank of every page.
########################################################################
import sys
sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW4/src/Resource')
sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW4/src/PageRank/W2GInlinksProcessor')
sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW4/src/PageRank/MergedIndexProcessor')

from W2GInlinksProcessor import W2GInlinksProcessor
from MergedIndexProcessor import MergedIndexProcessor
import Resource
from decimal import *
import math
from sets import Set

class PageRank:
    D = .85
    N = 0
    def __init__(self, type):
        print "Loading class members for Page Rank class...."
        # if page rank is being run for W2G Documents
        if type is "Resource":
            self._w2gInlinklsProcessorObj =  W2GInlinksProcessor(Resource.W2GInlinksFileCompletePath,
                                                                Resource.W2GOutlinksFileCompletePath,
                                                                Resource.W2GSinksCompletePath)

            self._inlinksMappingDict = self._w2gInlinklsProcessorObj.__GetInlinksMappingDict__()
            self._outlinksMappingDict =  self._w2gInlinklsProcessorObj.__GetOutlinksMappingDict__()
            self._sinks = self._w2gInlinklsProcessorObj.__GetSinksList__()
            self._urls =  self._w2gInlinklsProcessorObj.__GetListOfAllUrls__()
            PageRank.N = len(self._urls)
            self._resultFileCompletePath = Resource.W2GResultCompletePath
        else:
            self._EMObject =  MergedIndexProcessor(Resource.MergedInlinksFileCompleteFilePath,
                                                   Resource.MergedOutlinksFileCompleteFilePath,
                                                   Resource.MergedSinkFileCompleteFilePath,
                                                   Resource.MergedAllUrlsCompleteFilePath)

            self._inlinksMappingDict = self._EMObject.__GetInlinksMappingDict__()
            self._outlinksMappingDict =  self._EMObject.__GetOutlinksMappingDict__()
            self._sinks = self._EMObject.__GetSinksList__()
            self._urls =  self._EMObject.__GetListOfAllUrls__()
            self._idToUrlMapping = self._EMObject.__GetIdToUrlMapping__()
            PageRank.N = len(self._urls)
            self._resultFileCompletePath = Resource.MergedResultCompletePath


        self._PageRankDict = {}
        self._perplexityList = []
        self._iterationCount = 0

        print "Loading finished !!"

    ############################################################################
    def __CalculatePageRank__(self):
        initialValueForPageRank = float(1)/float(PageRank.N)
        teleportationValue  = float(1 - PageRank.D) / float(PageRank.N)

        print "Initial Page rank value : ", initialValueForPageRank
        print "Teleportation Value : ",teleportationValue

        for url in self._urls:
            self._PageRankDict[url] = initialValueForPageRank

        while self.__IsNotConvereged__(self._PageRankDict):
        # while self._iterationCount <= 50:
            self._iterationCount += 1
            sinkPR = 0

            for url in self._sinks:
                if self._PageRankDict.has_key(url):
                    sinkPR += self._PageRankDict[url]

            newPR= {}
            for url in self._urls:
                newPR[url] = teleportationValue
                newPR[url] += float(PageRank.D * sinkPR) / float(PageRank.N)

                if not self._inlinksMappingDict.has_key(url):
                    # print url
                    continue

                inlinksForUrl = self._inlinksMappingDict[url]
                for inlinkForUrl in inlinksForUrl:
                    if self._outlinksMappingDict.has_key(inlinkForUrl):
                        noOfOutlinksFromUrl = len(self._outlinksMappingDict[inlinkForUrl])
                        if self._PageRankDict.has_key(inlinkForUrl):
                            newPR[url] += float(PageRank.D) * float(self._PageRankDict[inlinkForUrl]) / float(noOfOutlinksFromUrl)

            # for url in self._urls:
            self._PageRankDict = newPR

        resultListWithTop500 = self.__GetTop500UrlToValueDict__(self._PageRankDict)
        self.__DumpResultInFile__(resultListWithTop500)


    ############################################################################
    def __CalculatePageRank1__(self):
        initialValueForPageRank = float(1)/float(PageRank.N)
        teleportationValue  = float(1 - PageRank.D) / float(PageRank.N)

        print "Initial Page rank value : ", initialValueForPageRank
        print "Teleportation Value : ",teleportationValue

        for url in self._urls:
            self._PageRankDict[url] = initialValueForPageRank

        while self.__IsNotConvereged__(self._PageRankDict):
            self._iterationCount += 1
            sinkPR = 0

            for url in self._sinks:
                sinkPR += self._PageRankDict[url]

            newPR= {}
            for url in self._urls:
                newPR[url] = teleportationValue
                newPR[url] += float(PageRank.D * sinkPR) / float(PageRank.N)

                inlinksForUrl = self._inlinksMappingDict[url]
                for inlinkForUrl in inlinksForUrl:
                    noOfOutlinksFromUrl = len(self._outlinksMappingDict[inlinkForUrl])
                    newPR[url] += float(PageRank.D) * float(self._PageRankDict[inlinkForUrl]) / float(noOfOutlinksFromUrl)

            for url in self._urls:
                self._PageRankDict[url] = newPR[url]

        resultListWithTop500 = self.__GetTop500UrlToValueDict__(self._PageRankDict)
        self.__DumpResultInFile__(resultListWithTop500)

    ##################################################################################
    def __IsNotConvereged__(self, pageRankDict):
        perplexities = self.__CalculatePerplexity__(pageRankDict)

        if len(perplexities) > 5:
            isConverged = int(perplexities[-1]) == int(perplexities[-2]) == int(perplexities[-3]) == int(perplexities[-4])
            if isConverged:
                resultListWithTop500 = self.__GetTop500UrlToValueDict__(pageRankDict)
                self.__DumpResultInFile__(resultListWithTop500)
            return  not isConverged
        else:
            return  True

    ##################################################################################
    def __CalculatePerplexity__(self, pageRankDict):
        shannonEntropy = float(0)

        for url, pageRankValue in pageRankDict.iteritems():
            shannonEntropy += float(pageRankValue) * float(math.log(pageRankValue,2))

        perplexity = math.pow(2,-shannonEntropy)
        self._perplexityList.append(perplexity)

        print "Iteration #", self._iterationCount, ", Perplexity",self._perplexityList[-1], perplexity
        return self._perplexityList

    ###############################################################################
    def __GetTop500UrlToValueDict__(self, pageRankDict):
        print "==== Get 500 documents with top socres ===="

        cumulativeSum = 0
        for key, value in pageRankDict.iteritems():
            cumulativeSum += value
        print "Summation of all Page Ranks before filtering out to 500 : ", cumulativeSum

        top500Values = sorted(pageRankDict.items(), key=lambda x: x[1], reverse = True)
        resultListWithTop500 = []
        c=0
        for url, value in top500Values:
            c+=1
            if c > 500:
                break

            resultListWithTop500.append(str(c) + " " + url + "   " + str(value))
        return resultListWithTop500

    ##############################################################################
    def __DumpResultInFile__(self, resultList):
        with open(self._resultFileCompletePath, "w+") as handle:
            for aLine in resultList:
                handle.write(aLine+"\n")

            handle.close()

##################################################################################
# END
##################################################################################

obj = PageRank("Resource")
obj.__CalculatePageRank__()