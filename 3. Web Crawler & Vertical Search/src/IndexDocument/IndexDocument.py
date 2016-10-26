##########################################################################################################
# This class :
# Extracts documents from the files.
# Parses documents to find DOCID and TEXT, and CREATES logical documents ready to be indexed
# Indexes all documents with the help of ElasticSearchManager class
##########################################################################################################

import os, re, sys,string, datetime

from time import sleep

#office laptop
# sys.path.append('C:\Users\\310230279\Dropbox\CS6200_V_Sangwan\HW3\src\ElasticSearchManager')
# sys.path.append('C:\Users\\310230279\Dropbox\CS6200_V_Sangwan\HW3\src\Resource')
# sys.path.append('C:\Users\\310230279\Dropbox\CS6200_V_Sangwan\HW3\src\Enum')

# Personal laaptop
sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW3/src/Resource')
sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW3/src/ElasticSearchManager')
sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW3/src/Enum')
# sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW3/src/OutlinkProcesser')

import Resource
from ElasticSearchManager import ElasticSearchManager
from Enum import ElasticSearchUsedFor
import pickle
# from OutlinkProcesser import InlinkManager
##########################################################################################################

class IndexDocument():
    DocumentCounter = 0

    #########################   Constructor #######################################
    def __init__(self, dirPath):
        self.urlDict = {}

        with open(Resource.InlinksFilePath, "rb") as handle:
            self.urlDict = pickle.load(handle)
            print type(self.urlDict)
            handle.close()

        self.documentDirPath = dirPath
        self._ESMgrObject = ElasticSearchManager(Resource.INDEX_NAME, Resource.TYPE_NAME, ElasticSearchUsedFor.Indexing)

    ################################################################
    def __IndexAllDocumentsInAllFIles__(self):
        fileCounter = 0
        print '\n'
        for root, dirs, files in os.walk(self.documentDirPath):
            for file in files:
                filePath = os.path.join(root, file)
                fileCounter = fileCounter + 1
                # print fileCounter, filePath
                # if fileCounter == 10:
                #     sleep(3)
                # if fileCounter<= 10:
                self.__IndexesAllDocumentsOfOneFile__(filePath)



                # res = self._ESMgrObject.__CurrentIndexStats__()
                # print str(res["count"]) + "/total", "documents indexed.\n"


        res = self._ESMgrObject.__CurrentIndexStats__()
        print str(res["count"]) + "/84678", "documents indexed.\n"



    ################################################################
    def __IndexesAllDocumentsOfOneFile__(self, filePath):
        f = open(filePath, 'r')
        fileContent = f.read()

        docListInAFile = self.__GetDocumentListFromAFile__(fileContent)
        # c = 0
        for document in docListInAFile:

            # if EmailParser.DocumentCounter < 12600:
            #     EmailParser.DocumentCounter = EmailParser.DocumentCounter + 1
            #     print "Skipping : ",EmailParser.DocumentCounter
            #
            #     continue

            documentUrl = self.__GetUrlForADocument__(document)
            documentText = self.__GetTextForADocument__(document)
            documentAuthor = self.__GetAuthorForADocument__(document)
            documentHtml_Source = self.__GetRawHtmlForADocument__(document)
            documentHTTPheader = self.__GetHttpHeaderForADocument__(document)
            documentOut_links = self.__GetOutlinksForADocument__(document)
            documentTitle = self.__GetTitleForADocument__(document)

            documentIn_links = self.__GetInlinksSepBySpace__(documentUrl)

            docno = ""
            depth = ""


            # print "inlinks", documentIn_links
            # print documentUrl
            # print documentText
            # print documentAuthor
            # print documentHtml_Source
            # print documentHTTPheader
            # print documentOut_links


            if len(documentText) > 0:
                IndexDocument.DocumentCounter = IndexDocument.DocumentCounter + 1

            self._ESMgrObject.__UploadDocumentToIndex__(IndexDocument.DocumentCounter,
                                                        documentUrl,
                                                        documentText,
                                                        documentAuthor,
                                                        documentHtml_Source,
                                                        documentHTTPheader,
                                                        documentOut_links,
                                                        documentTitle,
                                                        documentIn_links)


    ################################################################
    def __GetDocumentListFromAFile__(self, fileContent):
        return re.findall(r'<DOC>(.*?)</DOC>', fileContent, re.DOTALL)

    ################################################################
    def __GetDocumentInlinksFromAFile__(self, url):
        return  self.__GetInlinksSepBySpace__(url)



    ################################################################
    def __GetUrlForADocument__(self,document):
        documentIdList = re.findall(r'<URL>(.*?)</URL>', document, re.DOTALL)
        urlAsId = documentIdList[0].replace("https","http")
        # print "IDDDDDd",urlAsId
        return documentIdList[0]

        # return 20

    ################################################################
    def __GetTextForADocument__(self, document):
        documentTextList = re.findall(r'<TEXT>(.*?)</TEXT>', document, re.DOTALL)
        documentText = ""
        # print documentTextList
        for text in documentTextList:
            documentText = documentText + " " + text

        documentText = " ".join(documentText.split("\n"))
        documentText = " ".join(documentText.split("  "))
        # remove punctuation
        # punc = set(string.punctuation)
        # documentText = ''.join(c for c in documentText if not c in punc)

        return documentText.lower()

    def __GetAuthorForADocument__(self, document):
        authors = re.findall(r'<AUTHOR>(.*?)</AUTHOR>', document, re.DOTALL)
        if len(authors) == 0:
            return "Vikas"

        author = authors[0]
        return author

    def __GetRawHtmlForADocument__(self, document):
        documentTextList = re.findall(r'<RAW>(.*?)</RAW>', document, re.DOTALL)
        documentText = ""
        # print documentTextList
        for text in documentTextList:
            documentText = documentText + " " + str(text)

        documentText = " ".join(documentText.split("\n"))
        documentText = " ".join(documentText.split("  "))


        return documentText.lower()
        # return rawHtml[0]

    def __GetHttpHeaderForADocument__(self, document):
        HttpHeaders = re.findall(r'<HTTPHEADER>(.*?)</HTTPHEADER>', document, re.DOTALL)
        if len(HttpHeaders) == 0:
            return ""

        httpHeader = HttpHeaders[0].replace("\n","")
        return httpHeader

    def __GetOutlinksForADocument__(self, document):
        outlinks = re.findall(r'<OUTLINKS>(.*?)</OUTLINKS>', document, re.DOTALL)
        outlinksText = ""
        for outlink in outlinks:
            outlinksText = outlinksText + " " + outlink.replace("https","http")
        return outlinksText

    def __GetTitleForADocument__(self, document):
        titles = re.findall(r'<title>(.*?)</title>', document, re.DOTALL)
        title = ""
        if len(titles) == 0:
            return ""

        return titles[0]

    def __GetInlinksSepBySpace__(self,url):

        inlinksTextSepBySpace = ""
        if self.urlDict.has_key(url):
            setElements = self.urlDict[url]



            if len(setElements) == 0:
                return ""

            for element in setElements:
                inlinksTextSepBySpace = inlinksTextSepBySpace + " " + element

        return inlinksTextSepBySpace

##########################################################################################################
# Run this script to Index all documents from the given files.
##########################################################################################################
print datetime.datetime.now().time()
_documentDirectory = "C:/vikas/CS6200/HW3/output"
print "Directory path of files , ", _documentDirectory
# _documentDirectory = "C:\Users\\vikas\Dropbox\sangwan.ea@gmail.com\AP89_DATA\AP_DATA\\ap89_collection"
x = IndexDocument(_documentDirectory);
x.__IndexAllDocumentsInAllFIles__()
print datetime.datetime.now().time()

##########################################################################################################
# ENDC:\vikas\CS6200\HW3\output
##########################################################################################################

