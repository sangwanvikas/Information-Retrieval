##########################################################################################################
# START
##########################################################################################################

import sys, datetime, os, re
from sets import Set
import pickle

reload(sys)
sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW3/src/Resource')

import Resource
class InlinkProcessor:

    ################################################################
    def __init__(self, documentDirectory):
        print "from Inlink processor"
        self.documentDirPath = documentDirectory
        self.urlDict = {}

        with open(Resource.FinalInlinksFilePath, "rb") as handle:
            self.urlDict = pickle.load(handle)
            print type(self.urlDict)
            handle.close()

##########################################################################################################
##########################################################################################################
    def  __GetInlinksSepBySpace__(self,url):

        if self.urlDict.has_key(url):
            setElements = self.urlDict[url]

            inlinksTextSepBySpace = ""

            if len(setElements) == 0:
                return ""

            for element in setElements:
                inlinksTextSepBySpace = inlinksTextSepBySpace + " " + element

            return inlinksTextSepBySpace


##########################################################################################################
# END
##########################################################################################################

# print datetime.datetime.now().time()
_documentDirectory = "C:/vikas/CS6200/HW33/output"
#
# print "Directory path of files , ", _documentDirectory
obj = InlinkProcessor(_documentDirectory)

inlinksText1 = obj.__GetInlinksSepBySpace__("http://en.wikipedia.org/wiki/Bombing_of_Cologne_in_World_War_II")
inlinksText2 = obj.__GetInlinksSepBySpace__("http://en.wikipedia.org/wiki/Flight_and_expulsion_of_Germans_from_Romania_during_and_after_World_War_II")
print inlinksText1, inlinksText2
