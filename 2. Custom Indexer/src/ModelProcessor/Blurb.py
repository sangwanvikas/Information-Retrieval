
import sys, math, datetime
from stemming.porter2 import stem
import json

sys.path.append('C:\Users\\310230279\Dropbox\CS6200_V_Sangwan\HW2\src\\Enum')
sys.path.append('C:\Users\\310230279\Dropbox\CS6200_V_Sangwan\HW2\src\\IndexerManager')
sys.path.append('C:\Users\\310230279\Dropbox\CS6200_V_Sangwan\HW2\src\\Resource')
sys.path.append('C:\Users\\310230279\Dropbox\CS6200_V_Sangwan\HW2\src\\Resource')
sys.path.append('C:\Users\\310230279\Dropbox\CS6200_V_Sangwan\HW2\src\\Model')

import Resource
from IndexerManager import IndexerManager


class Retrieve():
    #######################  Constructor  #########################################
    def __init__(self):
        print 'Calculating average document length, total document length and unique terms from Elastic search...'

        # Creating objects of ElasticSearchMgr and various model classes.
        self._ESMgrObject = IndexerManager(Resource.FinalCatalogPath)


        print 'Average document length - avg(len(d)) : ', self._ESMgrObject._avgDocumentLength
        print 'Total Number of documents in the corpus - D :', self._ESMgrObject._totalNoOfDocsInCorpus
        print 'Unique terms in corpus - V :', self._ESMgrObject._uniqeTermInCorpus
        print 'Total length of all documents in Corpus', self._ESMgrObject._lengthOfAllDocuments, self._ESMgrObject._totalNoOfDocsInCorpus * self._ESMgrObject._avgDocumentLength
        print '\n'

        print "Execution started at", datetime.datetime.now().time()


    def __CalculateScore__(self,queryNumberArg, queryArg, originalQuery):
        # {u'AP890823-0021':
        #   {'allegations': ['17', '42', '62', '105', '138', '168','478']},
        #   {'measures' : ['20', '50', '91', '444']}
        # }
        documentDict = {}

        print "Processing Query # ", str(queryNumberArg), ". Query :", originalQuery, "....." "\n"
        for queryTerm in queryArg:
            queryTerm = queryTerm.lower()

            print "Query # ", str(
                queryNumberArg), ".... is in progress ...... for ", "Query Term - ", queryTerm, ". Stemmed value - ", stem(queryTerm)
            print "Fetching relevant list of {DocNo: XX, TermFrequency: XX, LengthOfDoc: XX} from Elasticsearch for the term - ", queryTerm, " ..."

            listOfDictionaryForATerm, NoOfDocsContainingterm = self._ESMgrObject.__GetTermDetailsForBlurb__(stem(queryTerm))

            print "Fetched !! Total Number of documents containing  ", queryTerm, "  term are : ", NoOfDocsContainingterm
            print "Calculating dt for all 5 models for query term - ", queryTerm, "..."

            if len(listOfDictionaryForATerm) > 0:

                for aDictOfDocIdAndPositions in listOfDictionaryForATerm:
                    docId = aDictOfDocIdAndPositions["DocNo"]
                    if documentDict.has_key(docId):
                        documentDict[docId][queryTerm] = aDictOfDocIdAndPositions["Positions"]
                    else:
                        documentDict[docId] = {queryTerm : aDictOfDocIdAndPositions["Positions"]}

        kAndSValueForDocs = {}
        for docId in documentDict:
            dictTermAsKeyAndPosAsValue = documentDict[docId]

            if len(dictTermAsKeyAndPosAsValue) > len(queryArg)/2 :
                k,s = self.GetKAndSForADocument(dictTermAsKeyAndPosAsValue)

                dtValueForDocId = self.FindDtForBlurb(k,s)
                kAndSValueForDocs[docId] = dtValueForDocId

        for docId, dtValue in kAndSValueForDocs.iteritems():
            self.__MergeFinal__(queryNumberArg, kAndSValueForDocs, Resource.IDFPath + "\\" + queryNumberArg + ".txt", "w",
                                True)
            self.__MergeFinal__(queryNumberArg, kAndSValueForDocs, Resource.ResultPath + "\\Blurb.txt", "a+", False)

    ############################################################################
    ############################  MERGE final files ####################################
    def __MergeFinal__(self, queryNumber, newDict, fileName, permission, order):
        c = 0
        with open(fileName, permission) as text_file:
            data = sorted(newDict.items(), key=lambda x: x[1], reverse=order)
            for key, value in data:
                c = c + 1
                if c <= 1000:
                    text_file.write(str(queryNumber) + " " + "Q0" + " " + str(key) + " " + str(c) + " " + str(
                        value) + " " + "EXP" + "\n")
                else:
                    break

    ###########################################################################

    def GetKAndSForADocument(self, dictTermAsKeyAndPosAsValue):
        k = len(dictTermAsKeyAndPosAsValue)
        s = 0

        tempListOfPosList = []
        for key, value in dictTermAsKeyAndPosAsValue.iteritems():
            tempListOfPosList.append(value)

        minRange = 6362283530
        while self.IsAnyListEmptyInTempListOfPosList(tempListOfPosList) == False:
            currentSlab = []
            minValue =0
            for listOfPositions in tempListOfPosList:
                if len(listOfPositions) > 0:
                    posList = int(listOfPositions[0])
                    currentSlab.append(posList)

            minValue = min(currentSlab)
            maxValue = max(currentSlab)
            minRange = maxValue - minValue
            minPosIndexInCurrentSlab= currentSlab.index(minValue)

            if range < minRange:
                minRange = range

            if len(tempListOfPosList[minPosIndexInCurrentSlab]) > 0:
                firstElementToBeDeleted = tempListOfPosList[minPosIndexInCurrentSlab][0]

                tempListOfPosList[minPosIndexInCurrentSlab].remove(firstElementToBeDeleted)


        s= minRange
        return k, s


    ##################################################
    def IsAnyListEmptyInTempListOfPosList(self, tempListOfPosList):
        isEmpty = False
        for positionList in tempListOfPosList:
            if len(positionList) == 0:
                isEmpty = True
                break
        return isEmpty


    #################################################

    def FindDtForBlurb(self,k,s):
        dt = 0
        dt = math.pow(.5,(s-k)/k)
        return dt



#################################################################################

blurbObject = Retrieve()
values = [3,4,5,0,6]
# print values.index(min(values))
blurbObject.__CalculateScore__("85",Resource.blurbquery85TersmList  ,Resource.OriginalQuery85TersmList)
blurbObject.__CalculateScore__("59",Resource.blurbquery59TersmList ,Resource.OriginalQuery59TersmList)
blurbObject.__CalculateScore__("56",Resource.blurbquery56TersmList ,Resource.OriginalQuery56TersmList)
blurbObject.__CalculateScore__("71",Resource.blurbquery71TersmList ,Resource.OriginalQuery71TersmList)
blurbObject.__CalculateScore__("64",Resource.blurbquery71TersmList64,Resource.OriginalQuery71TersmList64)
blurbObject.__CalculateScore__("62",Resource.blurbquery71TersmList62,Resource.OriginalQuery71TersmList62)
blurbObject.__CalculateScore__("93",Resource.blurbquery71TersmList93,Resource.OriginalQuery71TersmList93)
blurbObject.__CalculateScore__("99",Resource.blurbquery71TersmList99,Resource.OriginalQuery71TersmList99)
blurbObject.__CalculateScore__("58",Resource.blurbquery71TersmList58,Resource.OriginalQuery71TersmList58)
blurbObject.__CalculateScore__("77",Resource.blurbquery71TersmList77,Resource.OriginalQuery71TersmList77)
blurbObject.__CalculateScore__("54",Resource.blurbquery71TersmList54,Resource.OriginalQuery71TersmList54)
blurbObject.__CalculateScore__("87",Resource.blurbquery71TersmList87,Resource.OriginalQuery71TersmList87)
blurbObject.__CalculateScore__("94",Resource.blurbquery71TersmList94,Resource.OriginalQuery71TersmList94)
blurbObject.__CalculateScore__("100",Resource.blurbquery71TersmList100,Resource.OriginalQuery71TersmList100)
blurbObject.__CalculateScore__("89",Resource.blurbquery71TersmList89,Resource.OriginalQuery71TersmList89)
blurbObject.__CalculateScore__("61",Resource.blurbquery71TersmList61,Resource.OriginalQuery71TersmList61)
blurbObject.__CalculateScore__("95",Resource.blurbquery71TersmList95,Resource.OriginalQuery71TersmList95)
blurbObject.__CalculateScore__("68",Resource.blurbquery71TersmList68,Resource.OriginalQuery71TersmList68)
blurbObject.__CalculateScore__("57",Resource.blurbquery71TersmList57,Resource.OriginalQuery71TersmList57)
blurbObject.__CalculateScore__("97",Resource.blurbquery71TersmList97,Resource.OriginalQuery71TersmList97)
blurbObject.__CalculateScore__("98",Resource.blurbquery71TersmList98,Resource.OriginalQuery71TersmList98)
blurbObject.__CalculateScore__("60",Resource.blurbquery71TersmList60,Resource.OriginalQuery71TersmList60)
blurbObject.__CalculateScore__("80",Resource.blurbquery71TersmList80,Resource.OriginalQuery71TersmList80)
blurbObject.__CalculateScore__("63",Resource.blurbquery71TersmList63,Resource.OriginalQuery71TersmList63)
blurbObject.__CalculateScore__("91",Resource.blurbquery71TersmList91,Resource.OriginalQuery71TersmList91)




