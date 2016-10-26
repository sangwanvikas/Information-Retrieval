##########################################################################################################
# START
##########################################################################################################
import datetime, os, re, sys
from sets import Set
import json,pickle

reload(sys)
sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW3/src/Resource')

import Resource

class OutlinkProcessor:

    ################################################################
    def __init__(self, documentDirectory):
        print "from outlink processor"
        self.documentDirPath = documentDirectory
        self.urlDict = {}

    ###############__CreateInlinks__#################################################
    def __CreateInlinks__(self):
        fileCounter = 0
        print '__CreateInlinks__ \n'
        print os.path.exists(self.documentDirPath)
        for root, dirs, files in os.walk(self.documentDirPath):
            print root, dirs, files
            for file in files:
                fileCounter += 1
                filePath = os.path.join(root, file)
                print fileCounter, filePath
                print fileCounter, "Processing file..", filePath
                self.__ProcessAnHtmlDocument__(filePath)

        with open(Resource.FinalInlinksFilePath, "wb+") as handle:
            pickle.dump(self.urlDict, handle, -1)



    ################__ProcessAnHtmlDocument__################################################
    def __ProcessAnHtmlDocument__(self, filePath):
        f = open(filePath, 'r')
        fileContent = f.read()

        docListInAFile = self.__GetDocumentListFromAFile__(fileContent)

        for document in docListInAFile:
            outlinkTextSepBySpace = self.__GetOutlinksForADocument__(document)

            outlinks = outlinkTextSepBySpace.split(" ")
            if len(outlinks) == 0:
                continue

            url = self.__GetUrlForADocument__(document)
            if url == "":
                return

            for outlink in outlinks:
                outlink = outlink.lower().strip()

                if outlink == "" :
                    continue

                if self.urlDict.has_key(outlink):
                    self.urlDict[outlink].add(url)
                else:
                    d = Set()
                    d.add(url)
                    self.urlDict[outlink] = d


    #### HELPERS
    ################__GetDocumentListFromAFile__################################################
    def __GetDocumentListFromAFile__(self, fileContent):
        return re.findall(r'<DOC>(.*?)</DOC>', fileContent, re.DOTALL)

    ################__GetOutlinksForADocument__###########################################
    def __GetOutlinksForADocument__(self, document):
        outlinks = re.findall(r'<OUTLINKS>(.*?)</OUTLINKS>', document, re.DOTALL)
        outlinksText = ""
        for outlink in outlinks:
            outlinksText = outlinksText + " " + outlink.replace("https","http")
        return outlinksText

    ################__GetUrlForADocument__################################################
    def __GetUrlForADocument__(self,document):
        documentIdList = re.findall(r'<URL>(.*?)</URL>', document, re.DOTALL)
        urlAsId = documentIdList[0].replace("https","http")
        # print "IDDDDDd",urlAsId
        return documentIdList[0].lower().strip()





##########################################################################################################
# END
##########################################################################################################

print datetime.datetime.now().time()
_documentDirectory = "C:/vikas/CS6200/HW3/output"

print "Directory path of files , ", _documentDirectory
obj = OutlinkProcessor(_documentDirectory)
obj.__CreateInlinks__()
print "***************************************************************"
