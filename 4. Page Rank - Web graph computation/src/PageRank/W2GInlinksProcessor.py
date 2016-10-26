###################################################################################
# 1. Create a file "outlinks.json" mapping
# 2. Create a file "sinks.json" which contains all sinks => ZERO outlinks
##################################################################################

import sys
sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW4/src/Resource')

import Resource
import pickle
from sets import Set


class W2GInlinksProcessor:

    #####################################################################
    def __init__(self, W2GInlinksFileCompletePath, W2GOutlinksFileCompletePath, W2GSinksCompletePath):
        self._w2GInlinksFileCompletePath = W2GInlinksFileCompletePath
        self._w2GOutlinksFileCompletePath = W2GOutlinksFileCompletePath
        self._w2GSinksCompletePath = W2GSinksCompletePath

        self._outlinksMappingDict = {}
        self._inlinksMappingDict = {}
        self._allUrls = []
        self._sinkUrls = []

        self.__GenerateOutlinksMappingFile__()
        self.__GenerateSinksFile__()

    #####################################################################
    # Generate Mappings
    #####################################################################
    def __GenerateOutlinksMappingFile__(self):
        with open(self._w2GInlinksFileCompletePath, "r") as inlinksMappingHandle:
            linkeCounter = 0

            for aLineFromW2GInlinksMappingFile in inlinksMappingHandle:
                linkeCounter += 1

                if len(aLineFromW2GInlinksMappingFile) > 2:

                    aLineFromW2GInlinksMappingFile = aLineFromW2GInlinksMappingFile.rstrip(" \n")
                    urls = aLineFromW2GInlinksMappingFile.split(" ")

                    currentUrl = urls[0]
                    inlinks = list(urls[1:])
                    inlinks = list(Set(inlinks))

                    for inlink in inlinks:
                        if self._outlinksMappingDict.has_key(inlink):
                            self._outlinksMappingDict[inlink].append(currentUrl)
                        else:
                            self._outlinksMappingDict[inlink] = [currentUrl]


                    self._inlinksMappingDict[currentUrl] = inlinks
                    self._allUrls.append(currentUrl)

            # with open("ou.txt", "w+") as han:
            #     for key, value in self._outlinksMappingDict.iteritems():
            #         han.write(key + " " + str(value) + "\n")
    #####################################################################
    def __GenerateSinksFile__(self):
        allUrlsList = self._allUrls
        urlsWhichHaveNonZeroOutlinks = list(self._outlinksMappingDict.keys())

        largerSet = Set(allUrlsList)
        smallerSet = Set(urlsWhichHaveNonZeroOutlinks)
        self._sinkUrls =  Set(largerSet - Set(smallerSet))

    #####################################################################
    # FILE HELPERS
    #####################################################################
    def __DumpDataIntoFile__(self, fileCompletePath, data):
        # print "__DumpDataIntoFile__"
        with open(fileCompletePath, "wb+") as handle:
            # print "Dumping  data ..", fileCompletePath
            pickle.dump(data, handle)
            handle.close()

    def __ReadPickeData__(self, fileCompletePath):
        # print "__ReadPickeData__"
        with open(fileCompletePath, "rb") as handle:
            # print "Reading...", fileCompletePath
            data = pickle.load(handle)
            # print "Data type : ", type(data)
            # print "Length of data : ", len(data)
            return data

    #####################################################################
    # GETTERS
    #####################################################################
    def __GetOutlinksMappingDict__(self):
        print "Loading list with oulinks mapping....", self._w2GOutlinksFileCompletePath
        print "Data type :", type(self._outlinksMappingDict)
        print "Length of outlinks mapping", len(self._outlinksMappingDict)
        print "----------------------------"
        return self._outlinksMappingDict

    #####################################################################
    def __GetInlinksMappingDict__(self):
         print "Loading dictionary with inlinks mapping...", self._w2GInlinksFileCompletePath
         print "Data type :", type(self._inlinksMappingDict)
         print "Length of inlinks mapping", len(self._inlinksMappingDict)
         print "----------------------------"
         return self._inlinksMappingDict

    #####################################################################
    def __GetSinksList__(self):
        print "Loading list with Sink urls...", self._w2GSinksCompletePath
        print "Data type :", type(self._sinkUrls)
        print "Number of sink urls in the resource", len(self._sinkUrls)
        print "----------------------------"
        return self._sinkUrls

    #####################################################################
    def __GetListOfAllUrls__(self):
        resultUrls = []
        print "Loading list with all urls..."
        print "Data type :", type(self._allUrls)
        print "Number of all urls in the resource", len(self._allUrls)
        print "----------------------------"
        return  list(self._allUrls)


#####################################################################################
# END
#####################################################################################

# obj = W2GInlinksProcessor(Resource.W2GInlinksFileCompletePath,
#                           Resource.W2GOutlinksFileCompletePath,
#                           Resource.W2GSinksCompletePath)