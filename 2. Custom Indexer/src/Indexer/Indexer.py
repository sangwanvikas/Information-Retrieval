##########################################################################################################
# This class :
# Parses documents to find DOCID and TEXT, and CREATES logical documents ready to be indexed
# Implemented my own index, to replace Elastic search, to be able to handle large numbers of documents and
# terms without using excessive memory or disk I/O.
# In this project I indexed 85k documents (260MB data) on the local file system.
##########################################################################################################

import os, re, sys,string, datetime
from stemming.porter2 import stem
import json, shutil
import collections

sys.path.append('C:\Users\\310230279\Dropbox\CS6200_V_Sangwan\HW2\src\Resource')

import Resource

##########################################################################################################

class Indexer():
    DocumentCounter = 0
    IntermediateFileNumber = 1
    cumulativeDocCounter = 0
    BatchSize = 10000
    LengthOfEOF = 2

    #########################  Constructor #######################################
    def __init__(self, dirPath):
        self._documentDirPath = dirPath
        self._stopWordsList = []
        self._stopWordsList = self.__GetStopWordsList__()

        self._previousFinalCatalogDict = {}
        self._invertedIndexDictForCurrentBatch = {}
        self._catalogFileForCurrentBatch = {}

        self._docInfoDic = {}
        self._documentIdMappingDict = {}
        self._termIdMappingDict = {}

        self._lineNumber = 0
        self._startIndex = 0
        self._totalLengthOfAllDocuments = 0

        # self.__CleanIntermediateFiles__()

    ################################################################
    def __DeleteAllIntermediateFiles__(self):
        # _eachDocumentLength.txt.txt
        if os.path.isfile(Resource.EachDocumentLengthFilePath) :
            os.remove(Resource.EachDocumentLengthFilePath)

        # _individualLengthOfEachDoc.txt
        if os.path.isfile(Resource.TotalLengthOfAllFiles):
            os.remove(Resource.TotalLengthOfAllFiles)

        # _totalNumberOfDocsInCorpus.txt
        if os.path.isfile(Resource.TotalNumberOfDocsInCorpusFilePath):
            os.remove(Resource.TotalNumberOfDocsInCorpusFilePath)

        # _totalUniqueTermsInCorpus.txt
        if os.path.isfile(Resource.TotalNumberOfUniqueTermsInCorpusFilePath):
            os.remove(Resource.TotalNumberOfUniqueTermsInCorpusFilePath)

    ################################################################
    def __GetStopWordsList__(self):
        stopWords = []

        with open('stoplist.txt', 'rb') as handle:
            for line in handle:
                stopWords.append(line.lower().rstrip())
            handle.close()

        return stopWords

    ################################################################
    def __DumpDocumentIdMapping__(self, docIdMappingArg):
        with open(Resource.DocumentIdMapping, "w") as handle:
            json.dump(docIdMappingArg, handle)
            handle.close()

    ################################################################
    def __IndexAllDocumentsInAllFIles__(self):
        fileCounter = 0
        print Resource.EOFChar

        for root, dirs, files in os.walk(self._documentDirPath):
            for file in files:
                fileCounter = fileCounter + 1
                filePath = os.path.join(root, file)
                self.__IndexesAllDocumentsOfOneFile__(filePath)
                self.__DumpDocumentIdMapping__(self._documentIdMappingDict)

        self.__WriteCorpusInfo__()

        print fileCounter

    ################################################################
    def __IndexesAllDocumentsOfOneFile__(self, filePath):
        f = open(filePath, 'r')
        fileContent = f.read()

        docListInAFile = self.__GetDocumentListFromAFile__(fileContent)

        # for every document in a documentListInAFile
        for document in docListInAFile:
            Indexer.cumulativeDocCounter += 1

            # If it is 1000th doc of a batch then DUMP and Merge
            if Indexer.DocumentCounter == Indexer.BatchSize or Indexer.cumulativeDocCounter == 84678:
                currentIntermediateFileNo = str(Indexer.IntermediateFileNumber)
                previousIntermediateFileNo = str(Indexer.IntermediateFileNumber - 1)

                currentFinalCatalogFilePath = ""
                currentCatalogFilePath = ""
                previousFinalIntermediateFilePath = ""
                currentFinalIntermediateFilePath = ""
                currentIntermediateFilePath = ""

                currentFinalCatalogFilePath,\
                currentCatalogFilePath,\
                previousFinalIntermediateFilePath,\
                currentFinalIntermediateFilePath,\
                currentIntermediateFilePath = self.__GetIntermediateFilesPath__(previousIntermediateFileNo, currentIntermediateFileNo)

                self.__DumpInvertedIndexDictIntoTextFile__(currentIntermediateFilePath, self._invertedIndexDictForCurrentBatch)
                self.__DumpCatalogDictIntoTextFile__(currentCatalogFilePath, self._catalogFileForCurrentBatch)

                if (Indexer.IntermediateFileNumber > 1):
                    print datetime.datetime.now().time()
                    print "Merging ...", Indexer.cumulativeDocCounter - Indexer.BatchSize, " to ", Indexer.cumulativeDocCounter
                    # Merge Inverted files and create currentFinalCatalogFilePath (Preveious catalogdic, currentCatalogDIct)
                    self.__MergePreviousFinalInvertedFile__(self._previousFinalCatalogDict,
                                                            self._catalogFileForCurrentBatch,
                                                            currentFinalCatalogFilePath,
                                                            previousFinalIntermediateFilePath,
                                                            currentIntermediateFilePath,
                                                            currentFinalIntermediateFilePath)
                else:
                    shutil.copy(currentIntermediateFilePath, currentFinalIntermediateFilePath)
                    shutil.copy(currentCatalogFilePath, currentFinalCatalogFilePath)
                    self._previousFinalCatalogDict = self._catalogFileForCurrentBatch


                self._invertedIndexDictFor1000Doc = {}
                Indexer.DocumentCounter = 0
                self._lineNumber = 0
                self._startIndex = 0
                self._catalogFileForCurrentBatch = {}
                self._invertedIndexDictForCurrentBatch = {}

                Indexer.IntermediateFileNumber += 1


            Indexer.DocumentCounter = Indexer.DocumentCounter + 1
            print Indexer.DocumentCounter, Indexer.cumulativeDocCounter

            # Parse docs and get documentId and documentText
            # Assign a unique integer ID to each document in the collection.
            documentId = self.__GetIdForADocument__(document)
            self._documentIdMappingDict[Indexer.cumulativeDocCounter] = documentId

            documentId = str(Indexer.cumulativeDocCounter)
            documentText = self.__GetTextForADocument__(document)

            wordsListOfADoc = documentText.split()
            tokenListOfADoc = []
            docLength = 0
            for word in wordsListOfADoc:
                tokenListOfADoc.append(stem(word.rstrip(".").strip()))
            documentText = " ".join(tokenListOfADoc)

            # Create InvertedIndex for each document
            # self._invertedIndexDictForCurrentBatch = {token : {docId1:[pos1, pos2, pos3], docId2 : [pos1,pos2]}}
            self.__CreateInvertedIndexDictionary__(tokenListOfADoc, documentId, documentText, docLength)

    ###############################################################
    def __GetIntermediateFilesPath__(self, previousIntermediateFileNo, currentIntermediateFileNo):
        currentFinalCatalogFilePath = Resource.IntFilesPath + '\\' + currentIntermediateFileNo + 'CF.txt'
        currentCatalogFilePath = Resource.IntFilesPath + '\\' + currentIntermediateFileNo + 'IntCatFile.txt'

        previousFinalIntermediateFilePath = Resource.IntFilesPath + '\\' + previousIntermediateFileNo + 'FF.txt'
        currentFinalIntermediateFilePath = Resource.IntFilesPath + '\\' + currentIntermediateFileNo + 'FF.txt'
        currentIntermediateFilePath = Resource.IntFilesPath + '\\' + currentIntermediateFileNo + 'IntInvertedIndexFile.txt'

        return currentFinalCatalogFilePath, currentCatalogFilePath, previousFinalIntermediateFilePath,currentFinalIntermediateFilePath,currentIntermediateFilePath

    ################################################################
    def __WriteCorpusInfo__(self):
        # Length of each document
        with open(Resource.EachDocumentLengthFilePath, "w") as handle:
            json.dump(self._docInfoDic, handle)
            handle.close()

        # Total length of all documents in Corpus
        with open(Resource.TotalLengthOfAllFiles, "w") as handle:
            json.dump({"_totalLengthOfAllDocuments": self._totalLengthOfAllDocuments}, handle)
            handle.close()

        # Total number of documents indexed in the corpus
        with open(Resource.TotalNumberOfDocsInCorpusFilePath, "w") as handle:
            json.dump({"_totalNumberOfDocsInCorpus": Indexer.cumulativeDocCounter - 1}, handle)
            handle.close()

        # unique terms in the corpus = total number of lines in Final Cumulative file
        with open(Resource.TotalNumberOfUniqueTermsInCorpusFilePath, "w") as handle:
            json.dump({"_totalUniqueTermsInCorpus": len(self._previousFinalCatalogDict)}, handle)
            handle.close()

        with open(Resource.TermIdMapping, "w") as handle:
            json.dump(self._termIdMappingDict, handle)
            handle.close()

    ################################################################
    def __CreateInvertedIndexDictionary__(self, tokenListOfADoc, documentId, documentText, docLength):
        for token in tokenListOfADoc:
            # self._invertedIndexDictForCurrentBatch = {token : {docId1:[pos1, pos2, pos3], docId2 : [pos1,pos2]}}
            isDotAllowed = True
            
            # ignore invalid token i.e. a word which contains more than one dot in a row
            if len(token.split(".")) > 1:
                if len(token.split(".")[1]) > 0:
                    isDotAllowed = True
                else:
                    isDotAllowed = False
               
            # is token does not exist in stoplist and len(token) > 0 and isValidToken     
            if token.strip(".").lower() not in self._stopWordsList and len(token) > 0 and isDotAllowed:
                docLength += 1
                tokenPositions = [i for i, x in enumerate(tokenListOfADoc) if x == token]
                token  = token.strip(".")

                if self._invertedIndexDictForCurrentBatch.has_key(token) == False:
                    self._invertedIndexDictForCurrentBatch[token] = {documentId: (tokenPositions)}
                else:
                    if self._invertedIndexDictForCurrentBatch[token].has_key(documentId) == False:
                        self._invertedIndexDictForCurrentBatch[token][documentId] = (tokenPositions)
            
            # Update totalLength of the corpus counter
            self._totalLengthOfAllDocuments += docLength
            
            # Update dictionary which contains {documentId : documentLength}
            self._docInfoDic[documentId] = docLength

    ###############################################################
    def __DumpInvertedIndexDictIntoTextFile__(self, intFileCompleatePath, invertedIndexDictArg):
        print intFileCompleatePath
        with open(intFileCompleatePath, 'w') as handle:
            for key, value in invertedIndexDictArg.iteritems():
                # $DOcId1 pos1 pos2$DocId2 pos2
                # $001 10 27$005 100 198$010 109 115$101 0 30
                textForLine = self.__ConvertInvertedIndexValueToString(key, value)
                handle.writelines(textForLine + "\n")
        handle.close()

    ################################################################    
    def __ConvertInvertedIndexValueToString(self, term, data):
        lineText = ""
        c = 0
        # data = {docId1:[pos1, pos2, pos3], docId2 : [pos1,pos2]}
        # sort inverted index value for a term in descending order of its Term Frequencies
        invertedIndexForATermSortedByTF = sorted(data, key=lambda k: len(data[k]), reverse=True)
        self._lineNumber = self._lineNumber + 1
        
        for key in invertedIndexForATermSortedByTF:
            c = c +1
            docId = key
            positionsList = data[key]
            positionText = ""

            for position in positionsList:
                positionText = positionText + " " + str(position)

            lineText = lineText + "$" + docId  + positionText

        # update catalogFileObject for CurrentBatch
        lenOfALine = self._startIndex + len(lineText) + Indexer.LengthOfEOF
        self._catalogFileForCurrentBatch[term] = str(self._lineNumber) + " "  + str(self._startIndex)+" "+ str(lenOfALine)
        self._startIndex = lenOfALine

        return lineText

    ################################################################
    def __DumpCatalogDictIntoTextFile__(self, catFileCompleatePath, catFileDictArg):
        with open(catFileCompleatePath, 'w') as handle:
            for key, value in catFileDictArg.iteritems():
                aLineInCatalogFile = str(key).strip() + Resource.Space + value.strip()
                handle.writelines(aLineInCatalogFile + Resource.EOFChar)
            handle.close()

    ################################################################
    def __LoadPreviousFinalCatalogFile__(self, catalogFilePath):
        catalogFileDict={}

        with open(catalogFilePath, "r") as handleFinalCatalog:
            for aLineInCatalog in handleFinalCatalog:
                # term LineNumber StartOffset EndOffset
                # aLineInCatalog = "fawn 1 0 45"
                posOfFirstOccuranceOfSpace = aLineInCatalog.find(Resource.Space)
                termFromACatalogLine = aLineInCatalog[:posOfFirstOccuranceOfSpace].strip()
                ValueFromACatalogLine = aLineInCatalog[posOfFirstOccuranceOfSpace:].strip()
                catalogFileDict[termFromACatalogLine] = ValueFromACatalogLine

        return catalogFileDict

    ###############################################################
    def __MergePreviousFinalInvertedFile__(self, previousFinalCatalogFileDict,currentCatalogFileDict,
                                           currentFinalCatalogFilePath,
                                           previousFinalIntermediateFilePath,
                                           currentIntermediateFilePath,
                                           currentFinalIntermediateFilePath):
        # currentFinalCatalogFilePath,  # create this file
        finalCatalogDict = {}

        previousFinalCatalogFileDict = collections.OrderedDict(sorted(previousFinalCatalogFileDict.items()))
        currentCatalogFileDict = collections.OrderedDict(sorted(currentCatalogFileDict.items()))

        # with open(currentFinalCatalogFilePath,"w") as currentFinalCatalogHandle:
        with open(currentFinalIntermediateFilePath, "w") as currentFinalIntermediateHandle:
            previousFinalCatalogList = previousFinalCatalogFileDict.items()
            currentCatalogList = currentCatalogFileDict.items()
            # print previousFinalCatalogList

            # print  previousFinalCatalogList[0]



            lineNumberInFinalIntermediateFile = 0
            startIndex = 0
            while len(previousFinalCatalogList) > 0 and len(currentCatalogList) > 0:
                lineNumberInFinalIntermediateFile += 1
                text=""
                termIdFromPreviousFinalCatalog = previousFinalCatalogList[0][0]
                aLineFromPreviousFinalCatalog = previousFinalCatalogList[0]

                termIdFromCurrentCatalog = currentCatalogList[0][0]
                aLineFromCurrentCatalog = currentCatalogList[0]


                term= ""
                if termIdFromPreviousFinalCatalog == termIdFromCurrentCatalog:
                    term, text = self.__ConcatenateLinesFromTwoInvertedIndexFilesForSameTerm__(previousFinalIntermediateFilePath, aLineFromPreviousFinalCatalog,
                                                                                               currentIntermediateFilePath, aLineFromCurrentCatalog)
                    previousFinalCatalogList.remove(aLineFromPreviousFinalCatalog)
                    currentCatalogList.remove(aLineFromCurrentCatalog)
                    # print "1.1 when match", term, text

                else:
                    if termIdFromPreviousFinalCatalog < termIdFromCurrentCatalog:
                        term, text = self.GetALineFromIntermediateFile(previousFinalIntermediateFilePath,aLineFromPreviousFinalCatalog)
                        previousFinalCatalogList.remove(aLineFromPreviousFinalCatalog)
                        # print "1.2.1 when prev < curr", term, text

                    else:
                        term, text = self.GetALineFromIntermediateFile(currentIntermediateFilePath, aLineFromCurrentCatalog)
                        currentCatalogList.remove(aLineFromCurrentCatalog)
                        # print "1.2.1 when prev > curr", term, text


                currentFinalIntermediateHandle.write(text)
                self._termIdMappingDict[term] = lineNumberInFinalIntermediateFile

                lenOfALine = startIndex + len(text) +1
                finalCatalogDict[term] = str(lineNumberInFinalIntermediateFile) + " " + \
                                                                       str(startIndex) + " " +\
                                                                       str(lenOfALine)
                startIndex = lenOfALine

            while len(previousFinalCatalogList) > 0:
                lineNumberInFinalIntermediateFile += 1
                termIdFromPreviousFinalCatalog = previousFinalCatalogList[0][1]

                aLineFromPreviousFinalCatalog = previousFinalCatalogList[0]

                term,text = self.GetALineFromIntermediateFile(previousFinalIntermediateFilePath, aLineFromPreviousFinalCatalog)

                previousFinalCatalogList.remove(aLineFromPreviousFinalCatalog)
                currentFinalIntermediateHandle.write(text)
                self._termIdMappingDict[term] = lineNumberInFinalIntermediateFile
                # print "2 when prevInt is remaining", term, text
                lenOfALine = startIndex + len(text) + 1
                finalCatalogDict[term] = str(lineNumberInFinalIntermediateFile) + " " + \
                                         str(startIndex) + " " + \
                                         str(lenOfALine)
                startIndex = lenOfALine

            while len(currentCatalogList) > 0:
                lineNumberInFinalIntermediateFile += 1
                termIdFromCurrentCatalog = currentCatalogList[0][1]
                aLineFromCurrentCatalog = currentCatalogList[0]

                term, text = self.GetALineFromIntermediateFile(currentIntermediateFilePath, aLineFromCurrentCatalog)
                currentCatalogList.remove(aLineFromCurrentCatalog)

                currentFinalIntermediateHandle.write(text)
                self._termIdMappingDict[term] = lineNumberInFinalIntermediateFile
                # print "3 currentCat is rema", term, text
                lenOfALine = startIndex + len(text) + 1
                finalCatalogDict[term] = str(lineNumberInFinalIntermediateFile) + " " + \
                                         str(startIndex) + " " + \
                                         str(lenOfALine)
                startIndex = lenOfALine

        currentFinalIntermediateHandle.close()
        # currentFinalCatalogFilePath.close()
        self.__DumpCatalogDictIntoTextFile__(currentFinalCatalogFilePath, finalCatalogDict)
        self._previousFinalCatalogDict = finalCatalogDict

        print "Merging Completed !!"
        print datetime.datetime.now().time()
        print "\n"

    #################################################################
    def GetALineFromIntermediateFile(self, invertedIndexFilePath, aLineFromCatalogList):
        # aLineFromCatalogList = "fawn 28353 18323754 18323904"
        term = aLineFromCatalogList[0]
        lineNumber, startOffset, endOffset = aLineFromCatalogList[1].split(Resource.Space)

        aLineFromInvertedIndexFile = ""
        with open(invertedIndexFilePath, "r") as intFileHanlde:
            intFileHanlde.seek(int(startOffset))
            aLineFromInvertedIndexFile = intFileHanlde.readline()

        return term, aLineFromInvertedIndexFile

    ################################################################
    def __ConcatenateLinesFromTwoInvertedIndexFilesForSameTerm__(self, previousFinalInvertedIndexFilePath,
                                                                   aLineFromPreviousFinalCatalogList,
                                                                   currentBatchInvertedIndexFilePath,
                                                                   aLineFromCurrentBatchCatalogList):


        term, aLineFromPreviousFinalInvertedIndexFile = self.GetALineFromIntermediateFile(previousFinalInvertedIndexFilePath,
                                                                                     aLineFromPreviousFinalCatalogList)

        term, aLineFromCurrentBatchInvertedIndexFile = self.GetALineFromIntermediateFile(currentBatchInvertedIndexFilePath,
                                                                                         aLineFromCurrentBatchCatalogList)

        aLineFromPreviousFinalIntermediate =  aLineFromPreviousFinalInvertedIndexFile.strip(Resource.EOFChar)
        aLineFromCurrentBatchInvertedIndexFile = aLineFromCurrentBatchInvertedIndexFile.strip(Resource.EOFChar)

        # a new line for the current final Inverted Index File
        # concatenated lines must be sorted descending based on the term frequencies
        aConcatedLine = self.__MergeTwoInvertedIndexLinesForATermAndSortByTermFreq__(aLineFromPreviousFinalIntermediate,
                                                                                     aLineFromCurrentBatchInvertedIndexFile)

        return term, aConcatedLine + Resource.EOFChar

    ############# Merge SOrt  #######################################
    def __MergeTwoInvertedIndexLinesForATermAndSortByTermFreq__(self, aLineFromFirstInvertedIndexFile,
                                                                anIntermediateLineFromSecondFile):
        concatenatedText = ""
        concatenatedDict = []
        # aLineFromFirstInvertedIndexFile = $9199 403 405 407$9184 403 405 407$22663 138 140$15740 414
        # anIntermediateLineFromSecondFile = $5448 654$5243 38

        firstFileDocumentInfoList = aLineFromFirstInvertedIndexFile.split(Resource.DollarAsDocSplitter)
        secondFileDocumentInfoList = anIntermediateLineFromSecondFile.split(Resource.DollarAsDocSplitter)

        while self.__IsNotEmpty__(firstFileDocumentInfoList)and self.__IsNotEmpty__(secondFileDocumentInfoList):
            firstElementFromFirstList = firstFileDocumentInfoList[0]
            termFreqForFirstElementFromFirstList = len(firstElementFromFirstList.split(Resource.Space)) - 1

            firstElementFromSecondList = secondFileDocumentInfoList[0]
            termFreqForFirstElementFromSecondList = len(firstElementFromSecondList.split(Resource.Space)) - 1

            if termFreqForFirstElementFromFirstList == termFreqForFirstElementFromSecondList:
                concatenatedDict.append(firstFileDocumentInfoList[0])
                firstFileDocumentInfoList.remove(firstFileDocumentInfoList[0])

                concatenatedDict.append(secondFileDocumentInfoList[0])
                secondFileDocumentInfoList.remove(secondFileDocumentInfoList[0])
            else:
                if termFreqForFirstElementFromFirstList >  termFreqForFirstElementFromSecondList:
                    concatenatedDict.append(firstFileDocumentInfoList[0])
                    firstFileDocumentInfoList.remove(firstFileDocumentInfoList[0])
                else:
                    concatenatedDict.append(secondFileDocumentInfoList[0])
                    secondFileDocumentInfoList.remove(secondFileDocumentInfoList[0])

        while self.__IsNotEmpty__(firstFileDocumentInfoList):
            concatenatedDict.append(firstFileDocumentInfoList[0])
            firstFileDocumentInfoList.remove(firstFileDocumentInfoList[0])

        while self.__IsNotEmpty__(secondFileDocumentInfoList):
            concatenatedDict.append(secondFileDocumentInfoList[0])
            secondFileDocumentInfoList.remove(secondFileDocumentInfoList[0])

        for termWithAllPositions in concatenatedDict:
            if len(termWithAllPositions)>0:
                concatenatedText = concatenatedText + Resource.DollarAsDocSplitter + termWithAllPositions

        return concatenatedText

    #################################################################
    def __IsNotEmpty__(self, list):
        if len(list) > 0:
            return True

        return False

    ################################################################
    def __GetDocumentListFromAFile__(self, fileContent):
        return re.findall(r'<DOC>(.*?)</DOC>', fileContent, re.DOTALL)

    ################################################################
    def __GetIdForADocument__(self,document):
        documentIdList = re.findall(r'<DOCNO> (.*?) </DOCNO>', document, re.DOTALL)
        return documentIdList[0]

    ################################################################
    def __GetTextForADocument__(self, document):
        documentTextList = re.findall(r'<TEXT>\n(.*?)\n</TEXT>', document, re.DOTALL)
        documentText = ""

        for text in documentTextList:
            documentText = documentText + " " + text

        documentText = " ".join(documentText.split("\n"))
        documentText = " ".join(documentText.split("  "))
        documentText = re.sub('[^a-zA-Z0-9\n\.]', ' ', documentText)

        return documentText.lower()

#####################################################################
# Run this script to Index all documents from the given files.
##########################################################################################################
print datetime.datetime.now().time()
x = Indexer(Resource.AP89CorpusLocation);
# x.__IndexAllDocumentsInAllFIles__()
print datetime.datetime.now().time()

##########################################################################################################
# END
##########################################################################################################

