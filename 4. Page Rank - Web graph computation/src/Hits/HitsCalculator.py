



import sys
reload(sys)
sys.setdefaultencoding('utf8')

# Personal laaptop
sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW4/src/Resource')
sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW4/src/Utility')

import Resource
import Utility
import math
from sets import Set

#####################################################################
class HitsCalculator:
    def __init__(self):
        print "============HITS CALCULATOR STARTED============"
        self._utilityObj = Utility.Utility()

        self._baseSetAllUrls = []
        self._baseSetInlinksMapping = {}
        self._baseSetOutlinksMappnig = {}

        self.__loadBaseSetData__()

        self._AScore = {}
        self._HScore = {}
        self._perplexityAuthList = []
        self._perplexityHubList = []
        self._iterationCount = 0


    #####################################################################
    def __loadBaseSetData__(self):
        self._baseSetAllUrls = self._utilityObj.__ReadListFromTextFile__(Resource.BaseSetCompleteFilePath)
        self._baseSetInlinksMapping = self._utilityObj.__ReadDictFromTextFile__(Resource.BaseSetInlinksMappingPath)
        self._baseSetOutlinksMappnig = self._utilityObj.__ReadDictFromTextFile__(Resource.BaseSetOutlinksMappingPath)
        print "Base Set size is..", len(self._baseSetAllUrls)
        print "Loaded inlinksMapping for Base Set successfully !"
        print "Loaded outlinksmapping for Base Set successfully !"

    def __CalculateHits1__(self):
        print "\n"
        print "====Script running to calculate HITS - HUB and AUTHORITATIVE scores==="
        self.__CalculateHits__(self._baseSetAllUrls, self._baseSetInlinksMapping, self._baseSetOutlinksMappnig)
    #####################################################################
    def __CalculateHits__(self, allUrls, inlinksMappingDict, outlinksMappingDict):
        for url in allUrls:
                self._AScore[url] = 1
                self._HScore[url] = 1

        normalizedAFactor = self.__FindNormalizationFactor__(self._AScore)
        normalizedHFactor = self.__FindNormalizationFactor__(self._HScore)

        self._AScore = self.__GetIdToNormalizedScoreDict__(self._AScore,normalizedAFactor)
        self._HScore = self.__GetIdToNormalizedScoreDict__(self._HScore,normalizedHFactor)

        newH= {}
        newA = {}
        while  self.__IsNotConvereged__(self._AScore, self._HScore):
            self._iterationCount += 1

            for url in allUrls:
                if inlinksMappingDict.has_key(url):
                    inlinks = inlinksMappingDict[url]
                    HSumForInlinks = 0
                    i=0
                    for inlink in inlinks:
                         i+=1
                         if self._AScore.has_key(inlink):
                             HSumForInlinks += self._AScore[inlink]
                             newH[url] = HSumForInlinks

                if outlinksMappingDict.has_key(url):
                    outlinks = Set(outlinksMappingDict[url])
                    ASumForOutlinks = 0
                    x = 0
                    for outlink in outlinks :
                        x +=1
                        if self._HScore.has_key(outlink):
                            ASumForOutlinks += self._HScore[outlink]
                            newA[url] = ASumForOutlinks

            normalizedAFactor = self.__FindNormalizationFactor__(newA)
            normalizedHFactor = self.__FindNormalizationFactor__(newH)

            self._AScore = self.__GetIdToNormalizedScoreDict__(newA,normalizedAFactor)
            self._HScore = self.__GetIdToNormalizedScoreDict__(newH,normalizedHFactor)


        # resultListWithTop500Auth = self.__GetTop500UrlToValueDict__( self._AScore)
        # resultListWithTop500AHub = self.__GetTop500UrlToValueDict__( self._HScore)
        #
        # print "====Dumping HUB and AUTHORITATIVE to files===="
        # self._utilityObj.__DumpListDataIntoTextFile__(Resource.HitsAuthResultFilePath,resultListWithTop500Auth)
        # self._utilityObj.__DumpListDataIntoTextFile__(Resource.HitsHubResultFilePath ,resultListWithTop500AHub)

    ##################################################################################
    def __FindNormalizationFactor__(self, scoreDict):
        summation = 0
        for key, value in scoreDict.iteritems():
            summation += value*value

        return math.sqrt(summation)

    ##################################################################################
    def __IsNotConvereged__(self, urlToAScoreDict, urlToHScoreDict):
        perplexitiesForAuth = self.__CalculatePerplexityForAuth__(urlToAScoreDict)
        perplexitiesForHub = self.__CalculatePerplexityForHub__(urlToHScoreDict)

        if len(perplexitiesForAuth) > 5 and len(perplexitiesForHub) > 5:
            # isAuthConverged = int(perplexitiesForAuth[-1]) == int(perplexitiesForAuth[-2]) == int(perplexitiesForAuth[-3]) == int(perplexitiesForAuth[-4])
            # isHubConverged = int(perplexitiesForHub[-1]) == int(perplexitiesForHub[-2]) == int(perplexitiesForHub[-3]) == int(perplexitiesForHub[-4])

            isAuthConverged = (perplexitiesForAuth[-1] - perplexitiesForAuth[-2]) == (perplexitiesForAuth[-3] - perplexitiesForAuth[-4]) == .00001
            print "perp auth.", perplexitiesForAuth[-1] , perplexitiesForAuth[-2] , perplexitiesForAuth[-3] , perplexitiesForAuth[-4]
            isHubConverged = (perplexitiesForHub[-1] == perplexitiesForHub[-2]) and (perplexitiesForHub[-3] == perplexitiesForHub[-4]) == .00001
            print "perp hub",  perplexitiesForHub[-1] , perplexitiesForHub[-2] , perplexitiesForHub[-3] , perplexitiesForHub[-4]

            print isAuthConverged, isHubConverged, not (isAuthConverged and isHubConverged)
            print (perplexitiesForAuth[-1] - perplexitiesForAuth[-2]) == (perplexitiesForAuth[-3] - perplexitiesForAuth[-4])
            if isAuthConverged and isHubConverged:
                resultListWithTop500Auth = self.__GetTop500UrlToValueDict__(urlToAScoreDict)
                resultListWithTop500AHub = self.__GetTop500UrlToValueDict__(urlToHScoreDict)
                print "\n"
                print "====Dumping HUB and AUTHORITATIVE to files===="
                self._utilityObj.__DumpListDataIntoTextFile__(Resource.HitsAuthResultFilePath,resultListWithTop500Auth)
                self._utilityObj.__DumpListDataIntoTextFile__(Resource.HitsHubResultFilePath ,resultListWithTop500AHub)
            return  not (isAuthConverged and isHubConverged)
        else:
            return  True

    ##################################################################################
    def __CalculatePerplexityForAuth__(self, urlToAScoreDict):
        shannonEntropy = float(0)

        for url, pageRankValue in urlToAScoreDict.iteritems():
            shannonEntropy += float(pageRankValue)

        perplexity = math.pow(2,-shannonEntropy)
        self._perplexityAuthList.append(perplexity)

        print "Iteration #", self._iterationCount, ", Score for Authority ",self._perplexityAuthList[-1]
        return self._perplexityAuthList

    def __CalculatePerplexityForHub__(self, urlToHScoreDict):
        shannonEntropy = float(0)

        for url, pageRankValue in urlToHScoreDict.iteritems():
            shannonEntropy += float(pageRankValue)

        perplexity = math.pow(2,-shannonEntropy)
        self._perplexityHubList.append(perplexity)

        print "Iteration #", self._iterationCount, ", Score for HUB",self._perplexityHubList[-1]
        print "\n"
        return self._perplexityHubList

    #####################################################################
    def __GetTop500UrlToValueDict__(self, pageRankDict):
        print "\n"
        print "=======Fetching URLs with top 500 scores====="
        print len(pageRankDict)
        top500Values = sorted(pageRankDict.items(), key = lambda x: x[1], reverse = True)
        resultListWithTop500 = []
        c=0
        for url, value in top500Values:
            if c > 500:
                break

            if not "history.com" in url:
                resultListWithTop500.append(url + "\t" + str(value))
                c+=1

        return resultListWithTop500

    ####################################################################
    def __GetIdToNormalizedScoreDict__(self,idToScoreDict,normalizedAFactor):
        newIdToScoreDict = {}
        # print normalizedAFactor

        for id, value in idToScoreDict.iteritems():
            newIdToScoreDict[id] = value/normalizedAFactor

        return newIdToScoreDict

##################################################################################
# END
##################################################################################
obj = HitsCalculator()
obj.__CalculateHits1__()



