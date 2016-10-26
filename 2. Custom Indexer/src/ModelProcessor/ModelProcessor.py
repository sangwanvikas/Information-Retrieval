##########################################################################################################
# This class:
# Retrieves term and document statistics with the help of custom IndexerManager
# This custom IndexManager has replaced the need of ElasticManager
##########################################################################################################

import sys, math, datetime
from stemming.porter2 import stem
import json

sys.path.append('C:\Users\\310230279\Dropbox\CS6200_V_Sangwan\HW2\src\\IndexerManager')
sys.path.append('C:\Users\\310230279\Dropbox\CS6200_V_Sangwan\HW2\src\\Resource')
sys.path.append('C:\Users\\310230279\Dropbox\CS6200_V_Sangwan\HW2\src\\Resource')
sys.path.append('C:\Users\\310230279\Dropbox\CS6200_V_Sangwan\HW2\src\\Model')

import Resource
from IndexerManager import IndexerManager
from OkapiTF import OkapiTF
from OkapiBM25 import OkapiBM25
from LaplaceSmoothing import LaplaceSmoothing
##########################################################################################################


class ModelProcessor():

    #######################  Constructor  #########################################
    def __init__(self):
        print 'Calculating average document length, total document length and unique terms from Elastic search...'
        
        # Creating objects of ElasticSearchMgr and various model classes.
        self._ESMgrObject = IndexerManager(Resource.FinalCatalogPath)
        self._okapiTFObj = OkapiTF()
        self._okapiBM25Obj = OkapiBM25()
        self._laplaceSmoothingObj = LaplaceSmoothing(self._ESMgrObject._uniqeTermInCorpus)

        print 'Average document length - avg(len(d)) : ', self._ESMgrObject._avgDocumentLength
        print 'Total Number of documents in the corpus - D :', self._ESMgrObject._totalNoOfDocsInCorpus
        print 'Unique terms in corpus - V :', self._ESMgrObject._uniqeTermInCorpus
        print 'Total length of all documents in Corpus', self._ESMgrObject._lengthOfAllDocuments, self._ESMgrObject._totalNoOfDocsInCorpus * self._ESMgrObject._avgDocumentLength
        print '\n'

        print "Execution started at", datetime.datetime.now().time()

    ################################################################
    def __ProcessQuery__(self, queryNumberArg, queryArg, originalQuery):
        # Dictionaries : To save scoring value, calculated using Various models, for each document.
        dictForOkapiTF = {}
        dictForIDF = {}
        dictForOkapiBM25 = {}

        listOfdictForLaplace = []

        print "Processing Query # ", str(queryNumberArg), ". Query :",  originalQuery, "....." "\n"
        for queryTerm in queryArg:
            TFOfTermInQuery = self.__GetTFOfTermInQuery__(queryTerm, originalQuery)
            queryTerm = queryTerm.lower()

            print "Query # ", str(queryNumberArg),".... is in progress ...... for ", "Query Term - ",queryTerm ,". Stemmed value - ", stem(queryTerm)
            print "Fetching relevant list of {DocNo: XX, TermFrequency: XX, LengthOfDoc: XX} from Elasticsearch for the term - ", queryTerm, " ..."

            listOfDictionaryForATerm, totalFrequency= self._ESMgrObject.__GetTermDetailsFromCorpus__(stem(queryTerm))
            NoOfDocsContainingterm = len(listOfDictionaryForATerm)

            print "Fetched !! Total Number of documents containing  ", queryTerm, "  term are : ",NoOfDocsContainingterm
            print "Calculating dt for all 5 models for query term - ", queryTerm, "..."


            dictForATermForLaplaceSmoothing = {}
            # For Laplace, for each document with its dt value (when TF =0) is stored in a dictionary.
            # {"docId1":dtValue, "docId2, dtValue...84k} is read from a file. This file is created when program begins
            # and exeutes a method to find total length of documents in the Corpus.
            with open('filename.txt', 'rb') as handle:
                b = json.load(handle)
                handle.close()
            # This dictionary is reset every time for a new term in query because it is updated with correct dt values
            # for the relevant document, which means doc where query term exists.
            dictForATermForLaplaceSmoothing = b

            for oneDictionary in listOfDictionaryForATerm:

                docId = oneDictionary["DocNo"]
                tf = oneDictionary["TermFrequency"]
                docLength = oneDictionary["LengthOfDoc"]

                summationOfTotalLengthCompliment = self._ESMgrObject._lengthOfAllDocuments

                dtValueForOneWordInOneDoc , \
                dtValueForIDF, \
                dtValueForOneWordOkapiBM25, \
                dtValueForOneWordLaplaceSmoothing, \
                dtValueForJelinekMercer = self.__CalculateDtForModels__(tf,
                                                                        docLength,
                                                                        self._ESMgrObject._avgDocumentLength,
                                                                        self._ESMgrObject._totalNoOfDocsInCorpus,
                                                                        NoOfDocsContainingterm,
                                                                        TFOfTermInQuery,
                                                                        totalFrequency,
                                                                        summationOfTotalLengthCompliment)

                # Okapi TF and IDF
                if  dictForOkapiTF.has_key(docId):
                    dictForOkapiTF[docId] = dictForOkapiTF[docId]  + dtValueForOneWordInOneDoc
                    dictForIDF[docId] = dictForIDF[docId]  + dtValueForIDF
                else:
                    dictForOkapiTF[docId] = dtValueForOneWordInOneDoc
                    dictForIDF[docId] = dtValueForIDF

                # OkapiBM25
                if dictForOkapiBM25.has_key(docId):
                    dictForOkapiBM25[docId] = dictForOkapiBM25[docId] + dtValueForOneWordOkapiBM25
                else:
                    dictForOkapiBM25[docId] = dtValueForOneWordOkapiBM25

                # # Laplace Smoothing - for Vector Space Models only one dictionary was sufficient, but here I need
                # # a list of dictionaries. One dictionary of 84678 length for every query term.
                if dictForATermForLaplaceSmoothing.has_key(docId):
                    dictForATermForLaplaceSmoothing[docId] = float(dtValueForOneWordLaplaceSmoothing)

            # # List contains as many dictionaries as the number of terms in a query:
            # # [ ({"docId1":dtValue,"docId2":dtValue.......84658},("docId1":dtValue, "docId2":dtValue.......84658)]
            listOfdictForLaplace.append(dictForATermForLaplaceSmoothing)

            print "list len(listOfdictForLaplace)", len(listOfdictForLaplace)
            print "CALCULATED!! dt for -> ", queryTerm, "\n"

        resultDictionary = self.__FindSummationForLaplace__(listOfdictForLaplace)



        # For a Query, respective dictionaries with {docId:ScoringFnValue} are passed to append Output file
        self.__WriteQueryResultIntoOutputFiles__(queryNumberArg, dictForOkapiTF, dictForIDF, dictForOkapiBM25,resultDictionary,)

        print "Scoring values for all 5 models computed successfully."
        print "Updated output files, for this query, with top 1000 documents (sorted based on the scoring values)."
        print "-------------------------------Query # ", str(queryNumberArg), " processed successfully-------------------\n"

    ################ Laplace Smoothing Summation################################################
    def __FindSummationForLaplace__(self, listOfLaplaceDict):
        # Opening file just to fetch all docIds, we are creating a dictionary with docId as key and don't care about
        # value, because it is used just to iterate over all documents present in the corpus
        with open('filename.txt', 'rb') as handle:
            b = json.load(handle)
            handle.close()
        dictForATermForLaplaceSmoothing = b

        newDict = {}

        for key, value in dictForATermForLaplaceSmoothing.iteritems():
            for dictr in listOfLaplaceDict:
                if newDict.has_key(key):
                    newDict[key] = newDict[key]+ math.log10(dictr[key])
                else:
                    newDict[key] = math.log10(dictr[key])

        return newDict

    ################################################################
    def __GetTFOfTermInQuery__(self,queryTerm, originalQuery):
        return originalQuery.lower().count(queryTerm.lower())

    ########################  Calculate dt for all Models ########################################
    def __CalculateDtForModels__(self, tf, docLength, avgDocumentLength, totalNoOfDocumentsInCorpus,
                                 NoOfDocsContainingterm,TFOfTermInQuery, summationOfTFCompliment,
                                 summationOfTotalLengthCompliment):
        dtValueForOkapiTF = self._okapiTFObj.__CalculateDtForOneTermInOneDocuments__(tf,
                                                                                     docLength,
                                                                                     avgDocumentLength)

        dtValueForIDF = dtValueForOkapiTF * (math.log10(totalNoOfDocumentsInCorpus / NoOfDocsContainingterm))

        dtValueForOkapiBM25 = self._okapiBM25Obj.__CalculateDtForOkapiBM__(tf, docLength, avgDocumentLength,
                                                                           totalNoOfDocumentsInCorpus,
                                                                           NoOfDocsContainingterm,
                                                                           TFOfTermInQuery)

        dtValueForLaplaceSmoothing = self._laplaceSmoothingObj.__CalculateDtForLaplaceSmoothing__(tf,docLength)

        dtValueForJelinekMercer = 0

        return dtValueForOkapiTF,dtValueForIDF,dtValueForOkapiBM25,dtValueForLaplaceSmoothing, dtValueForJelinekMercer

    ################################################################
    def __WriteQueryResultIntoOutputFiles__(self,queryNumberArg,newDict,newDictIDF,okapiBMDtDict,LaplaceSmoothingDict):
        self.__MergeFinal__(queryNumberArg, newDict, Resource.OkapiTFPath + "\\" + queryNumberArg + ".txt", "w", True)
        self.__MergeFinal__(queryNumberArg, newDict, Resource.ResultPath + "\\OkapiTF.txt", "a+", True)

        self.__MergeFinal__(queryNumberArg, newDictIDF, Resource.IDFPath + "\\" + queryNumberArg + ".txt", "w", True)
        self.__MergeFinal__(queryNumberArg, newDictIDF, Resource.ResultPath + "\\Idf.txt", "a+", True)

        self.__MergeFinal__(queryNumberArg, okapiBMDtDict, Resource.OkapiBM25Path + "\\" + queryNumberArg + ".txt", "w", True)
        self.__MergeFinal__(queryNumberArg, okapiBMDtDict, Resource.ResultPath + "\\OkapiBM25.txt", "a+", True)

        self.__MergeFinal__(queryNumberArg, LaplaceSmoothingDict,Resource.LaplaceSmoothingPath + "\\" + queryNumberArg + ".txt", "w", True)
        self.__MergeFinal__(queryNumberArg, LaplaceSmoothingDict, Resource.ResultPath + "\\LaplaceSmoothing.txt", "a+", True)

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

##########################################################################################################

print datetime.datetime.now().time()
finalResultDict = {}
obj = ModelProcessor()

obj.__ProcessQuery__("85",Resource.query85TersmList  ,Resource.OriginalQuery85TersmList)
obj.__ProcessQuery__("59",Resource.query59TersmList ,Resource.OriginalQuery59TersmList)
obj.__ProcessQuery__("56",Resource.query56TersmList ,Resource.OriginalQuery56TersmList)
obj.__ProcessQuery__("71",Resource.query71TersmList ,Resource.OriginalQuery71TersmList)
obj.__ProcessQuery__("64",Resource.query71TersmList64,Resource.OriginalQuery71TersmList64)
obj.__ProcessQuery__("62",Resource.query71TersmList62,Resource.OriginalQuery71TersmList62)
obj.__ProcessQuery__("93",Resource.query71TersmList93,Resource.OriginalQuery71TersmList93)
obj.__ProcessQuery__("99",Resource.query71TersmList99,Resource.OriginalQuery71TersmList99)
obj.__ProcessQuery__("58",Resource.query71TersmList58,Resource.OriginalQuery71TersmList58)
obj.__ProcessQuery__("77",Resource.query71TersmList77,Resource.OriginalQuery71TersmList77)
obj.__ProcessQuery__("54",Resource.query71TersmList54,Resource.OriginalQuery71TersmList54)
obj.__ProcessQuery__("87",Resource.query71TersmList87,Resource.OriginalQuery71TersmList87)
obj.__ProcessQuery__("94",Resource.query71TersmList94,Resource.OriginalQuery71TersmList94)
obj.__ProcessQuery__("100",Resource.query71TersmList100,Resource.OriginalQuery71TersmList100)
obj.__ProcessQuery__("89",Resource.query71TersmList89,Resource.OriginalQuery71TersmList89)
obj.__ProcessQuery__("61",Resource.query71TersmList61,Resource.OriginalQuery71TersmList61)
obj.__ProcessQuery__("95",Resource.query71TersmList95,Resource.OriginalQuery71TersmList95)
obj.__ProcessQuery__("68",Resource.query71TersmList68,Resource.OriginalQuery71TersmList68)
obj.__ProcessQuery__("57",Resource.query71TersmList57,Resource.OriginalQuery71TersmList57)
obj.__ProcessQuery__("97",Resource.query71TersmList97,Resource.OriginalQuery71TersmList97)
obj.__ProcessQuery__("98",Resource.query71TersmList98,Resource.OriginalQuery71TersmList98)
obj.__ProcessQuery__("60",Resource.query71TersmList60,Resource.OriginalQuery71TersmList60)
obj.__ProcessQuery__("80",Resource.query71TersmList80,Resource.OriginalQuery71TersmList80)
obj.__ProcessQuery__("63",Resource.query71TersmList63,Resource.OriginalQuery71TersmList63)
obj.__ProcessQuery__("91",Resource.query71TersmList91,Resource.OriginalQuery71TersmList91)

print datetime.datetime.now().time()
##########################################################################################################
##########################################################################################################