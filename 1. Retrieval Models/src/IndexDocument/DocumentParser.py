##########################################################################################################
# This class :
# Extracts documents from the files.
# Parses documents to find DOCID and TEXT, and CREATES logical documents ready to be indexed
# Indexes all documents with the help of ElasticSearchManager class
##########################################################################################################

import os, re, sys,string, datetime

from time import sleep

# sys.path.append('C:\Users\\vikas\Dropbox\CS6200_V_Sangwan\HW1\Common')
# sys.path.append('C:\Users\\vikas\Dropbox\CS6200_V_Sangwan\HW1\ElasticSearchManager')
# sys.path.append('C:\Users\\vikas\Dropbox\CS6200_V_Sangwan\HW1\Enum')

sys.path.append('C:\Users\\310230279\Dropbox\CS6200_V_Sangwan\HW1\src\Common')
sys.path.append('C:\Users\\310230279\Dropbox\CS6200_V_Sangwan\HW1\src\ElasticSearchManager')
sys.path.append('C:\Users\\310230279\Dropbox\CS6200_V_Sangwan\HW1\src\Enum')

import Resource
from ElasticSearchManager import ElasticSearchManager
from Enum import ElasticSearchUsedFor
##########################################################################################################

class DocumentParser():
    DocumentCounter = 0

    #########################   Constructor #######################################
    def __init__(self, dirPath):
        self.documentDirPath = dirPath
        self._ESMgrObject = ElasticSearchManager(Resource.INDEX_NAME, Resource.TYPE_NAME, ElasticSearchUsedFor.Indexing)

    ################################################################
    def __IndexAllDocumentsInAllFIles__(self):
        fileCounter = 0
        print '\n'
        for root, dirs, files in os.walk(self.documentDirPath):
            for file in files:
                filePath = os.path.join(root, file)

                # if testX is 1:
                self.__IndexesAllDocumentsOfOneFile__(filePath)
                res = self._ESMgrObject.__CurrentIndexStats__()
                print str(res["count"]) + "/84678", "documents indexed.\n"

        sleep(.5)
        res = self._ESMgrObject.__CurrentIndexStats__()
        print str(res["count"]) + "/84678", "documents indexed.\n"



    ################################################################
    def __IndexesAllDocumentsOfOneFile__(self, filePath):
        f = open(filePath, 'r')
        fileContent = f.read()

        docListInAFile = self.__GetDocumentListFromAFile__(fileContent)

        for document in docListInAFile:

            documentId = self.__GetIdForADocument__(document)
            documentText = self.__GetTextForADocument__(document)

            if len(documentText) > 0:
                DocumentParser.DocumentCounter = DocumentParser.DocumentCounter + 1

            self._ESMgrObject.__UploadDocumentToIndex__(DocumentParser.DocumentCounter,documentId, documentText)


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
        # remove punctuation
        # punc = set(string.punctuation)
        # documentText = ''.join(c for c in documentText if not c in punc)

        return documentText.lower()

##########################################################################################################
# Run this script to Index all documents from the given files.
##########################################################################################################
print datetime.datetime.now().time()
_documentDirectory = "C:\Users\\310230279\Dropbox\sangwan.ea@gmail.com\AP89_DATA\AP_DATA\\ap89_collection"
print "Directory path of files , ", _documentDirectory
# _documentDirectory = "C:\Users\\vikas\Dropbox\sangwan.ea@gmail.com\AP89_DATA\AP_DATA\\ap89_collection"
x = DocumentParser(_documentDirectory);
x.__IndexAllDocumentsInAllFIles__()
print datetime.datetime.now().time()

##########################################################################################################
# END
##########################################################################################################

