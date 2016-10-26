##########################################################################################################
# This class:
# Creates Inverted Index of the corpus of 85k documents (260MB data) in my local file system
# Perform GET for _search (Score in each doc), _count (DF) and _termvector (TF) methods
##########################################################################################################

import sys,datetime
from elasticsearch import Elasticsearch
from decimal import Decimal
from stemming.porter2 import stem
sys.path.append('C:\Users\\310230279\Dropbox\CS6200_V_Sangwan\HW2\src\Resource')
sys.path.append('C:\Users\\310230279\Dropbox\CS6200_V_Sangwan\HW2\src\\Model')


import Resource
from LaplaceSmoothing import LaplaceSmoothing
import json
##########################################################################################################

class IndexerManager():

    ##########################  Constructor  ######################################
    def __init__(self, finalCatalogPath):
        print "Em constructor"
        self._finalCatalogPath = finalCatalogPath

        self._avgDocumentLength = 0
        self._totalNoOfDocsInCorpus = 0
        self._lengthOfAllDocuments = 0
        self._uniqeTermInCorpus = 0

        self._avgDocumentLength,\
        self._totalNoOfDocsInCorpus,\
        self._lengthOfAllDocuments, \
        self._uniqeTermInCorpus = self.__GetInfoAboutIndexedCorpus__()

        self.__eachDocumentLength = {}
        # Length of each document
        with open(Resource.EachDocumentLengthFilePath, "r") as handle:
            self.__eachDocumentLength = json.load( handle)
            handle.close()

        self._documentIdMappingDict = {}
        with open(Resource.DocumentIdMapping, "r") as handle:
            self._documentIdMappingDict  = json.load(handle)
            handle.close()

        self._termIdMappingDict = {}
        with open(Resource.TermIdMapping, "r") as handle:
            self._termIdMappingDict = json.load(handle)
            handle.close()

        self.__CreateFileWithAllIdsAndDefaultdtForLaplaceSmoothing()


    ######################################################################################################
    # RETRIEVE information from my Index : required to run Vector Space and Language based model.
    ######################################################################################################

    def __GetInfoAboutIndexedCorpus__(self):
        _totalLengthOfAllDocuments = 0
        _totalNumberOfDocsInCorpus = 0
        _totalUniqueTermsInCorpus = 0

        # Total length of all documents in Corpus
        with open(Resource.TotalLengthOfAllFiles, "r") as handle:
            _totalLengthOfAllDocuments = int(json.load(handle)["_totalLengthOfAllDocuments"])
            handle.close()

        # Total number of documents indexed in the corpus
        with open(Resource.TotalNumberOfDocsInCorpusFilePath, "r") as handle:
            _totalNumberOfDocsInCorpus = int(json.load(handle)["_totalNumberOfDocsInCorpus"])
            handle.close()

        # Unique terms in Corpus
        with open(Resource.TotalNumberOfUniqueTermsInCorpusFilePath, "r") as handle:
            _totalUniqueTermsInCorpus = int(json.load(handle)["_totalUniqueTermsInCorpus"])
            handle.close()

        return _totalLengthOfAllDocuments/_totalNumberOfDocsInCorpus,\
               _totalNumberOfDocsInCorpus, \
               _totalLengthOfAllDocuments, \
               _totalUniqueTermsInCorpus

    #######################################################################
    def __FindDocumentLength__(self, documentIdArg):
        return self.__eachDocumentLength[documentIdArg]

    ########### Returns a LIST of dictionary [{DocNo: XX, TermFrequency: XX, LengthOfDoc: XX}] and
    # total frequency for a term
    def __GetTermDetailsFromCorpus__(self, term):
        TermDetailForAllDocsList = []

        term = stem(term)
        catalogFilePath =  Resource.CFPath
        IntFilePath =  Resource.InvFPath
        finalCatalogDict = self.__LoadPreviousFinalCataFile__(catalogFilePath)
        allDocumentsContainingTerm = []

        totalFrequency = 0

        if finalCatalogDict.has_key(term):
            aLineFromFinalInvertedFileForTerm = self.GetALineFromIntermediateFile(IntFilePath,
                                                                                  (term, finalCatalogDict[term]))
            allDocumentsContainingTerm = aLineFromFinalInvertedFileForTerm.split(Resource.DollarAsDocSplitter)
            allDocumentsContainingTerm.remove(allDocumentsContainingTerm[0])
            for aDocumentWithTF in allDocumentsContainingTerm:
                documentIdAndTFfrom = aDocumentWithTF.split(" ")
                docId = documentIdAndTFfrom[0]
                # -1 is for removing term from array of terms and positions
                tfScore = len(documentIdAndTFfrom) - 1
                totalFrequency += tfScore
                docLength = self.__FindDocumentLength__(docId)
                docId = self._documentIdMappingDict[documentIdAndTFfrom[0]]
                TermDetails = {"DocNo": docId, "TermFrequency": tfScore, "LengthOfDoc": docLength}
                TermDetailForAllDocsList.append(TermDetails)

        return TermDetailForAllDocsList, totalFrequency

    #Returns a LIST of dictionary [{DocNo: XX, Positions: [pos1, pos2]] and total frequency for a term
    ######################################################################
    def __GetTermDetailsForBlurb__(self, term):
        TermDetailForAllDocsList = []
        totalFrequency = 0
        term = stem(term)
        catalogFilePath = Resource.CFPath
        IntFilePath = Resource.InvFPath
        finalCatalogDict = self.__LoadPreviousFinalCataFile__(catalogFilePath)

        if finalCatalogDict.has_key(term):
            aLineFromFinalInvertedFileForTerm = self.GetALineFromIntermediateFile(IntFilePath,
                                                                                  (term, finalCatalogDict[term]))
            allDocumentsContainingTerm = aLineFromFinalInvertedFileForTerm.split(Resource.DollarAsDocSplitter)
            allDocumentsContainingTerm.remove(allDocumentsContainingTerm[0])
            for aDocumentWithTF in allDocumentsContainingTerm:
                positions = []
                documentIdAndTFfrom = aDocumentWithTF.split(Resource.Space)
                docId = documentIdAndTFfrom[0]

                tfScore = len(documentIdAndTFfrom) - 1
                totalFrequency += tfScore

                documentIdAndTFfrom.remove(documentIdAndTFfrom[0])
                for position in documentIdAndTFfrom:
                    positions.append(int(position))

                docId = self._documentIdMappingDict[docId]
                TermDetails = {"DocNo": docId, "Positions": positions}
                TermDetailForAllDocsList.append(TermDetails)

        return TermDetailForAllDocsList, totalFrequency

    ######################################################################
    def GetALineFromIntermediateFile(self, intermediateFilePath, aLineFromCatalogList):
        termFromCatalog = aLineFromCatalogList[0]
        lineNumber, startOffset, endOffset = aLineFromCatalogList[1].split(Resource.Space)
        aLineFromIntFile = ""
        with open(intermediateFilePath, "r") as intFileHanlde:
            intFileHanlde.seek(int(startOffset))
            aLineFromIntFile = intFileHanlde.readline()
        return aLineFromIntFile

        ################################################################

    #####################################################################
    def __LoadPreviousFinalCataFile__(self, catalogFilePath):
        catalogFileDict = {}
        with open(catalogFilePath, "r") as handleFinalCatalog:
            for aLineInCatalog in handleFinalCatalog:
                # aLineInCatalog = "fawn 1 0 45"
                posOfFirstOccuranceOfSpace = aLineInCatalog.find(Resource.Space)
                termFromLineInCatalog = aLineInCatalog[:posOfFirstOccuranceOfSpace].strip()
                valueFromLineInCatalog = aLineInCatalog[posOfFirstOccuranceOfSpace:].strip()
                catalogFileDict[termFromLineInCatalog] = valueFromLineInCatalog

        return catalogFileDict

    #####################################################################
    def __CreateFileWithAllIdsAndDefaultdtForLaplaceSmoothing(self):
        dictForLaplaceSmoothing = {}
        laplaceSmoothingObj = LaplaceSmoothing(self._uniqeTermInCorpus)

        for docId, documentLength in self.__eachDocumentLength.iteritems():
            if self._documentIdMappingDict.has_key(docId):
                originalId = self._documentIdMappingDict[docId]
                dictForLaplaceSmoothing[originalId] = float(laplaceSmoothingObj.__CalculateDtForLaplaceSmoothing__(0, documentLength))


        with open('filename.txt', 'w') as handle:
            json.dump(dictForLaplaceSmoothing, handle)
            handle.close()

    ####################################################################
    def __TestMethodForTA__(self, testInputfilePath, IntFilePath, catalogFilePath):
        finalCatalogDict = self.__LoadPreviousFinalCataFile__(catalogFilePath)
        with open(Resource.OutputFileForTA,"w") as outputFileHandle:
            with open(testInputfilePath,"r") as handle:
                for aLine in handle:
                    print "aLine", aLine
                    term = aLine.strip(Resource.EOFChar)
                    df = self.GetDocumentFrequencyForATerm(term, IntFilePath, finalCatalogDict)
                    ttf = self.GetTermFrequencyForATerm(term, IntFilePath, finalCatalogDict)
                    aLine = term + " " + str(df) + " " + str(ttf) + Resource.EOFChar
                    outputFileHandle.write(aLine)
                handle.close()
            outputFileHandle.close()
        print datetime.datetime.now().time()

    ################################################################
    def GetDocumentFrequencyForATerm(self, term, IntFilePath, finalCatalogDict):
        term = stem(term)
        df = 0

        if finalCatalogDict.has_key(term):
            aLineFromFinalInvertedFileForTerm = self.GetALineFromIntermediateFile(IntFilePath, (
            term, finalCatalogDict[term]))
            df =  len(aLineFromFinalInvertedFileForTerm.split(Resource.DollarAsDocSplitter)) - 1

        return df

    ################################################################
    def GetTermFrequencyForATerm(self, term, IntFilePath, finalCatalogDict):
        term = stem(term)
        tfCounter = 0

        if finalCatalogDict.has_key(term):
            aLineFromFinalInvertedFileForTerm = self.GetALineFromIntermediateFile(IntFilePath,
                                                                                  (term,
                                                                                   finalCatalogDict[term]))
            allDocumentsContainingTerm = aLineFromFinalInvertedFileForTerm.split(Resource.DollarAsDocSplitter)
            allDocumentsContainingTerm.remove(allDocumentsContainingTerm[0])
            for aDocumentWithTF in allDocumentsContainingTerm:
                documentIdAndTFfrom = aDocumentWithTF.split(Resource.Space)
                tfCounter +=  len(documentIdAndTFfrom) - 1

        return tfCounter
##########################################################################################################
# END
##########################################################################################################
# print datetime.datetime.now().time()
# em = IndexerManager(Resource.FinalCatalogPath)
# em.__TestMethodForTA__("InputFileFromTA.txt", Resource.InvFPath, Resource.CFPath)
