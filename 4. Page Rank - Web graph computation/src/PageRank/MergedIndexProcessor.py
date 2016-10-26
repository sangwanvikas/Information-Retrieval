##############################################################################
# START -
# 1. Run ESMgrObject.__GenerateInlinksMappingFile__() method to -
#  Get inlinksMapping, outlinksMapping, allUrls, SinkUrls for the merged index
#  Dump everything to "C:\vikas\CS6200\HW4\ProcessedData\Merged"

# 2. Run PageRank algorithm and Pass "text" other than "Resource" to c'tor
# obj = PageRank("TEXT")
# obj.__CalculatePageRank__()
##############################################################################


import sys

sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW4/src/Resource')
sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW4/src/Utility')

import Utility
import Resource
from sets import Set

class MergedIndexProcessor:

    def __init__(self, MergedInlinksFileCompleteFilePath,
                 MergedOutlinksFileCompleteFilePath,
                 MergedSinkFileCompleteFilePath,
                 MergedAllUrlsCompleteFilePath):

        self.MergedInlinksFileCompleteFilePath = MergedInlinksFileCompleteFilePath
        self.MergedOutlinksFileCompleteFilePath = MergedOutlinksFileCompleteFilePath
        self.MergedSinkFileCompleteFilePath = MergedSinkFileCompleteFilePath
        self.MergedAllUrlsCompleteFilePath = MergedAllUrlsCompleteFilePath

        print "df"
        self._utilityObj = Utility.Utility()

        ############################################
        self._outlinksMappingDict = {}
        self._inlinksMappingDict = {}
        self._allUrls = []
        self._sinkUrls = []
        self._idToUrlMapping = {}

        self.__GenerateOutlinksMappingFile__()
        self.__GenerateSinksFile__()
        self.__getinlinksWithCount__()

        ############################################

    def __GenerateOutlinksMappingFile__(self):
        tempAllSet = Set()
        with open(self.MergedInlinksFileCompleteFilePath, "r") as inlinksMappingHandle:
            linkeCounter = 0

            for aLineFromW2GInlinksMappingFile in inlinksMappingHandle:
                linkeCounter += 1

                aLineFromW2GInlinksMappingFile = aLineFromW2GInlinksMappingFile.strip("\n").lower()

                urls = aLineFromW2GInlinksMappingFile.split(" ")
                urls = filter(None, urls)

                if len(urls) < 1 or "about/about/about/about" in urls[0]:
                    continue

                currentUrl = urls[0]
                currentUrl = currentUrl.lower()
                tempAllSet.add(currentUrl)
                self._idToUrlMapping[currentUrl] = list(urls[1:])

                inlinks = list(urls[1:])
                inlinks = list(Set(inlinks))

                for inlink in inlinks:
                    inlink = inlink.lower().replace("https", "http")
                    if self._outlinksMappingDict.has_key(inlink):
                        if currentUrl in self._outlinksMappingDict[inlink] :
                            continue
                        self._outlinksMappingDict[inlink].append(currentUrl)
                    else:
                        self._outlinksMappingDict[inlink] = [currentUrl]
                        self._allUrls.append(inlink)

                self._inlinksMappingDict[currentUrl] = inlinks
                self._allUrls.append(currentUrl)

        self._allUrls = list(Set(self._allUrls))

        tempOutlinks = {}

        rdpSet = set(self._outlinksMappingDict)
        namesSet = set(self._allUrls)

        print "common", len(rdpSet.intersection(namesSet))
        for name in rdpSet.intersection(namesSet):
            # print name
            if len(self._outlinksMappingDict[name]) > 0:
                tempOutlinks[name] = self._outlinksMappingDict[name]
            # else:
            #     print "dffffffffffffffffff",  name, self._outlinksMappingDict[name]
        self._outlinksMappingDict = tempOutlinks

        self._utilityObj.__DumpDictDataIntoTextFile__("ou.txt", self._outlinksMappingDict)
        self._utilityObj.__DumpDictDataIntoTextFile__("in.txt", self._inlinksMappingDict)
        print "Allurls count #",len(self._allUrls), len(Set(self._allUrls))
        print "Inlinks count #",len(self._inlinksMappingDict)
        print "Outlinks count #",len(self._outlinksMappingDict)


    # def __GenerateOutlinksMappingFile1__(self):
    #     with open(self.MergedInlinksFileCompleteFilePath, "r") as inlinksMappingHandle:
    #         linkeCounter = 0
    #
    #         for aLineFromW2GInlinksMappingFile in inlinksMappingHandle:
    #             linkeCounter += 1
    #
    #             if len(aLineFromW2GInlinksMappingFile) > 2:
    #
    #                 aLineFromW2GInlinksMappingFile = aLineFromW2GInlinksMappingFile.rstrip("\n")
    #                 urls = aLineFromW2GInlinksMappingFile.split(" ")
    #                 urls = filter(None, urls)
    #
    #                 currentUrl = urls[0]
    #                 currentUrl = currentUrl.lower().replace("https", "http")
    #                 inlinks = list(urls[1:])
    #                 inlinks = list(Set(inlinks))
    #
    #                 if not "http" in currentUrl:
    #                     continue
    #
    #                 for inlink in inlinks:
    #                     inlink = inlink.lower().replace("https", "http")
    #
    #                     if self._outlinksMappingDict.has_key(inlink):
    #                         if currentUrl in self._outlinksMappingDict[inlink]:
    #                             continue
    #                         self._outlinksMappingDict[inlink].append(currentUrl)
    #                     else:
    #                         self._outlinksMappingDict[inlink] = [currentUrl]
    #
    #                 if len(inlinks) > 0:
    #                     self._inlinksMappingDict[currentUrl] = inlinks
    #                 self._allUrls.append(currentUrl)
    #
    #         print len(self._outlinksMappingDict["http://en.wikipedia.org/wiki/main_page"]), self._outlinksMappingDict["http://en.wikipedia.org/wiki/main_page"]
    #
    #         self._utilityObj.__DumpDictDataIntoTextFile__("ou.txt", self._outlinksMappingDict)
    #         self._utilityObj.__DumpDictDataIntoTextFile__("in.txt", self._inlinksMappingDict)
    #         # with open("ou.txt", "w+") as han:
    #         #     for key, value in self._outlinksMappingDict.iteritems():
    #         #         han.write(key + " " + str(value) + "\n")

    def __GenerateSinksFile__(self):
        allUrlsList = self._allUrls
        urlsWhichHaveNonZeroOutlinks = list(self._outlinksMappingDict.keys())

        largerSet = Set(allUrlsList)
        smallerSet = Set(urlsWhichHaveNonZeroOutlinks)
        self._sinkUrls =  Set(largerSet - Set(smallerSet))
        print "length of sink links", len(self._sinkUrls)

    def __GetOutlinksMappingDict__(self):
        print "Loading list with oulinks mapping....", self.MergedOutlinksFileCompleteFilePath
        print "Data type :", type(self._outlinksMappingDict)
        print "Length of outlinks mapping", len(self._outlinksMappingDict)
        print "----------------------------"
        return self._outlinksMappingDict

    #####################################################################
    def __GetInlinksMappingDict__(self):
         print "Loading dictionary with inlinks mapping...", self.MergedInlinksFileCompleteFilePath
         print "Data type :", type(self._inlinksMappingDict)
         print "Length of inlinks mapping", len(self._inlinksMappingDict)
         print "----------------------------"
         return self._inlinksMappingDict

    #####################################################################
    def __GetSinksList__(self):
        print "Loading list with Sink urls...", self.MergedSinkFileCompleteFilePath
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


    def __GetIdToUrlMapping__(self):
        return self._idToUrlMapping

    def __getinlinksWithCount__(self):
        tempDict = {}
        for url, inlinks in self._inlinksMappingDict.iteritems():
           if not "about/about/about" in url:
            # if self._inlinksMappingDict.has_key(url):
                tempDict[url] = len(self._inlinksMappingDict[url])

        tempDict = sorted(tempDict.items(), key=lambda x: x[1], reverse = True)
        self._utilityObj.__DumpListDataIntoTextFile__("uq1.txt", tempDict)




#
# _EMObject =  MergedIndexProcessor(Resource.MergedInlinksFileCompleteFilePath,
#                                                    Resource.MergedOutlinksFileCompleteFilePath,
#                                                    Resource.MergedSinkFileCompleteFilePath,
#                                                    Resource.MergedAllUrlsCompleteFilePath)
# _EMObject.__getinlinksWithCount__()



