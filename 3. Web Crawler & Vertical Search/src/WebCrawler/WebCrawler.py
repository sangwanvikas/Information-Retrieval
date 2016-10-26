#############################################################
#START
#############################################################

import os, sys, time

import requests
from requests.auth import HTTPProxyAuth

# sys.path.append('C:\Users\\310230279\Dropbox\CS6200_V_Sangwan\HW3\src\Resource')

sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW3/src/Resource')

import Resource, datetime
from DocumentParser import DocumentParser
from UrlParser import UrlParser
# Library for parsing robot.txt
from reppy.cache import RobotsCache
from Queue import Queue, PriorityQueue
import memcache

#############################################################

class WebCrawler:
    def __init__(self, bfsFrontierQueue, processedUrls, mc):

        self._docParserObj = DocumentParser()
        self._bfsFrontierQueue = PriorityQueue()
        self._bfsFrontierQueue = bfsFrontierQueue
        self._processedUrls = processedUrls
        self.documentDepthDict = {
            "http://en.wikipedia.org/wiki/Sino-Soviet_split" :0,
            "https://www.marxists.org/history/international/comintern/sino-soviet-split/" : 0,
            "http://www.gilderlehrman.org/history-by-era/seventies/essays/united-states-and-china-during-cold-war" : 0,
            "http://www.atomicarchive.com/History/coldwar/":0,
            "http://digitalarchive.wilsoncenter.org/" : 0,
            "http://thediplomat.com/tag/cold-war/":0
        }

        self._mc = mc
        self._timeStamp = {}
        # self.__WriteStateIntoMemCache__( bfsFrontierQueue, processedUrls)


        self._urlParserObj = UrlParser()
        self._distance = 0
        self._robotObjectsForDomainsDIct = {}
        self._noOfDocumentsCrawled = 0
        # self._processedUrlsDict = {}
        self.__CrawlUrl__(self._processedUrls)


    def __CrawlUrl__(self, processedUrls):
        # processedUrls = []
        docCounter = 0
        cumulativeCounter = 0
        while not self._bfsFrontierQueue.empty() and len(processedUrls) < 60001:

            elem = self._bfsFrontierQueue.get()
            rawUrl = elem[1]
            prioriyScore = elem[0]


            print "---------------------------------------------------------------------"
            print "Buffer size is ", self._bfsFrontierQueue.qsize()
            print "Preparing to crawl.. #",cumulativeCounter,  len(processedUrls),prioriyScore, rawUrl

            processedUrls.append(rawUrl)

            doesRobotFileExist, robotFileObj,self._robotObjectsForDomainsDIct, self._timeStamp, domainName\
                = self._urlParserObj.__FetchRobotFileInfo__(rawUrl,self._robotObjectsForDomainsDIct,self._timeStamp)

            isAllowedInRobotFile = self._urlParserObj.__IsUrlAllowedInRobotFile1__(rawUrl, self._robotObjectsForDomainsDIct, domainName)

            print "Is allowed in Robot file ?", isAllowedInRobotFile, self._robotObjectsForDomainsDIct

            if isAllowedInRobotFile == False:
                continue

            if self._timeStamp.has_key(domainName):
                diffSoFar = (self._timeStamp[domainName] - datetime.datetime.now()).total_seconds()

                if  diffSoFar < 1:
                    time.sleep(1 - diffSoFar)
            else:
                timeStamp[domainName] = datetime.datetime.now()

            try:
                # proxyDict = {
                #     'http': 'http://amec.zscaler.philips.com:9480',
                #     'https': 'http://amec.zscaler.philips.com:9480'
                # }
                # auth = HTTPProxyAuth('310230279', 'April@2016')
                # page = requests.get(url,proxies=proxyDict, auth=auth)
                # print page

                page = requests.get(rawUrl)
            except requests.exceptions.ConnectionError:
                continue
            except:
                continue

            httpHeader = page.headers
            # if httpHeader.has_attr('Content-Length'):
            isPageContentEnglish= True
            try:
                isPageContentEnglish = "en" in httpHeader['Content-Language']
            except:
                isPageContentEnglish = True



            # only parse HTML documents
            if page.status_code != 200 or self._docParserObj.__IsPageHtml__(httpHeader) == False or isPageContentEnglish == False:
                print page.status_code
                continue

            rawText = str(page.text)
            pageContent = str(page.text.encode('utf8'))

            cumulativeCounter+=1
            self._bfsFrontierQueue, processedUrls, outlinks,\
                self.documentDepthDict = self._urlParserObj.__GetAllOutLinksForAPage__(rawUrl,
                                                                                                            pageContent,
                                                                                                            self._bfsFrontierQueue,
                                                                                                            processedUrls,
                                                                                                            self.documentDepthDict)

            # print "Cleaning crawled page content and writing to file in AP89 format........ "
            cleanedText = self._docParserObj.__CleanPageContent__(pageContent)
            docId = str(len(processedUrls))
            outlinksText = ' '.join(outlinks)
            httpHeader = str(httpHeader)
            print "outlinks->  ", outlinksText

            self._docParserObj.__CreateFileInAP89Format__(rawUrl, cleanedText,docId, rawText, httpHeader, outlinksText)
            docCounter += 1

            if docCounter == 200:
                op = self.__WriteStateIntoMemCache__(bfsFrontierQueue, processedUrls)
                docCounter = 0
                print op



    def __DumpContentInFile__(self, filePath, content):
        with open(filePath, "w") as handle:
            handle.writelines(content)
        handle.close()

        return False

    def __WriteStateIntoMemCache__(self,bfsFrontierQueue,processedUrls):
        print "__WriteStateIntoMemCache__"
        self._mc.set("fcount", bfsFrontierQueue.qsize())
        self._mc.set("pcount", len(processedUrls))

        c = 0
        for elem in list(bfsFrontierQueue.queue):
            self._mc.set("f" + str(c), elem)
            c+=1

        # load processedUrls in memcache
        c = 0
        for url in processedUrls:
            # print "p"+str(c)
            self._mc.set("p" + str(c), url)
            c += 1

        return True


#############################################################
print "hi"
mc = memcache.Client(['127.0.0.1:11211'], debug=0)


processedUrlsListSizeFromCache = 0
processedUrlsListSizeFromCache = mc.get("pcount")

processedUrls =[]
if not processedUrlsListSizeFromCache:
    processedUrls = []
else:
    #  Load processedUrls with memcached obj
    counter = processedUrlsListSizeFromCache - 1
    while counter > -1:
        processedUrlElement = mc.get("p" + str(counter))
        processedUrls.append(processedUrlElement)
        # print processedUrlElement
        counter -= 1
    print "Loaded processedUrls with memcached obj", processedUrlsListSizeFromCache



bfsFrontierQueue = PriorityQueue()
frontierQueueSizeFromCache =0
frontierQueueSizeFromCache = mc.get("fcount")
print "hi"
# seedUrls = ["http://en.wikipedia.org/wiki/Sino-Soviet_split", "https://www.marxists.org/history/international/comintern/sino-soviet-split/","http://www.gilderlehrman.org/history-by-era/seventies/essays/united-states-and-china-during-cold-war", "http://www.atomicarchive.com/History/coldwar/"]

seedUrls = ["http://en.wikipedia.org/wiki/Cold_War"]

# seedUrls = ["http://en.wikipedia.org/wiki/Sino-Soviet_split","http://en.wikipedia.org/wiki/MediaWiki:Spam-blacklist"]
if not  frontierQueueSizeFromCache:
   bfsFrontierQueue = PriorityQueue()
   for seedUrl in seedUrls:
       print "seed url", seedUrl
       bfsFrontierQueue.put((-20, seedUrl))
else:
    frontierQueueSizeFromCache -= 1
    while frontierQueueSizeFromCache > -1:
        frontierElement = mc.get("f" + str(frontierQueueSizeFromCache))

        if frontierElement != None:
            url = frontierElement[1]
            bfsFrontierQueue.put(frontierElement)

            frontierQueueSizeFromCache -= 1

    print "Loaded bfFrontier with memcached obj", bfsFrontierQueue.qsize()




webCrawlerObject = WebCrawler(bfsFrontierQueue, processedUrls, mc)
#############################################################