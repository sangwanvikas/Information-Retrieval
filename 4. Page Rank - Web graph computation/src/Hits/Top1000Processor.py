##############################################################
#1.1 First run ESMgrObject.__GenerateInlinksMappingFile__() to load-
# MergedInlinksFileCompleteFilePath,
# MergedOutlinksFileCompleteFilePath
# MergedSinkFileCompleteFilePath
# MergedAllUrlsCompleteFilePath

# 1.2 Run ESMgrObject._Get1000DocForRootSet__() to load Root set-
# Top1000Urls,
# Top1000OutlinksMappaing
# Top1000InlinksMappaing

#1.3 Run obj._AddPagesInToTheRootSet() to load BaseSet
# RootSetCompleteFilePath
# RootSetInlinksMappingPath,
# RootSetOutlinksMappingPath
#############################################################

import sys
reload(sys)
sys.setdefaultencoding('utf8')

# Personal laaptop
sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW4/src/Resource')
sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW4/src/Utility')


import Resource
import Utility
from sets import Set

#  Root set -> Base Set
class Top1000Processor:
    D = 50
    def __init__(self):
        print "Top1000Processor class"
        self._utilityObj = Utility.Utility()
        self._utilityObj = Utility.Utility()

    #####################################################################
    def _AddPagesInToTheRootSet(self):
        print "Creating Base set for HITS.."

        allCrawledUrls = self._utilityObj.__ReadListFromTextFile__(Resource.MergedAllUrlsCompleteFilePath)
        top1000Urls = self._utilityObj.__ReadListFromTextFile__(Resource.Top1000Urls)
        inlinksForTop1000UrlsDict = self._utilityObj.__ReadDictFromTextFile__(Resource.Top1000InlinksMappaing)
        outlinksForTop1000UrlsDict = self._utilityObj.__ReadDictFromTextFile__(Resource.Top1000OutlinksMappaing)

        rootSet = Set()
        c = 0
        for url in top1000Urls:
            c = c +1
            url = url.lower()
            inlinks = inlinksForTop1000UrlsDict[url]
            inlinkCounter = 0
            for inlink in inlinks:
                if inlinkCounter <= 5:
                    inlink = inlink.lower().replace("https", "http")
                    inlinkCounter += 1
                    rootSet.add(inlink)

            outlinks = outlinksForTop1000UrlsDict[url]
            outlinkCounter = 0
            for outlink in outlinks:
                if outlinkCounter <= 5:
                    outlink = outlink.lower().replace("https", "http")
                    outlinkCounter += 1
                    rootSet.add(outlink)

        for url in top1000Urls:
            if not url.lower().replace("https", "http") in rootSet:
                rootSet.add(url)

        print "Created Base Set of #", len(rootSet), " documents"
        print "Dumping inlinksMapping, outlinkMapping and urls to..", Resource.HitBaseSetDirectoryPath

        self._utilityObj.__DumpListDataIntoTextFile__(Resource.BaseSetCompleteFilePath,list(Set(rootSet)))

        self.__CreateInlinksMappingForBaseSet__(rootSet)

    #####################################################################
    def __CreateInlinksMappingForBaseSet__(self, baseSet):
        allMergedInlinksDict = self._utilityObj.__ReadDictFromTextFile__(Resource.MergedInlinksFileCompleteFilePath)
        allMergedOutlinksDict = self._utilityObj.__ReadDictFromTextFile__(Resource.MergedOutlinksFileCompleteFilePath)

        baseSetInlinksMappingDict = {}
        baseSetOutlinksMappingDict = {}

        for url in baseSet:
            url = url.lower()
            if allMergedInlinksDict.has_key(url.lower().replace("https", "http")):
                baseSetInlinksMappingDict[url]= ' '.join(allMergedInlinksDict[url])

            if allMergedOutlinksDict.has_key(url.lower().replace("https", "http")):
                baseSetOutlinksMappingDict[url] = ' '.join(allMergedOutlinksDict[url])

        # print " baseSetOutlinksMappingDict", len( baseSetOutlinksMappingDict), "baseSetInlinksMappingDict", len(baseSetInlinksMappingDict)
        self._utilityObj.__DumpDictDataIntoTextFile__(Resource.BaseSetInlinksMappingPath, baseSetInlinksMappingDict)
        self._utilityObj.__DumpDictDataIntoTextFile__(Resource.BaseSetOutlinksMappingPath, baseSetOutlinksMappingDict)


obj = Top1000Processor()
obj._AddPagesInToTheRootSet()
