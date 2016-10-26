#############################################################
#START
# TODO - Remove Urls from tht HTML page content
# TODO - Consider only relevant URLs
# TODO - implement magic hand
# TODO - Add page title in AP89 format document
# TODO - Add HTTP Response header in AP89 document
# TODO - Add ID, URL, the page content cleaned,the raw html, HTTP header, a list of all inlinks, and a list of all outlinks, author
# TODO - Maintain a list of URL being crawled and its Outlinks [ONLY THOSE WHICH WE WILL CRAWL]
# TODO - Remove most frequently URLS like privacy or copyright
#############################################################

# Library for parsing robot.txt
import sys
from reppy.cache import RobotsCache
from bs4 import BeautifulSoup, SoupStrainer
# Join and parses URLs
from urlparse import urljoin
import urlparse
import datetime
# Accurately separate the TLD from the registered domain andsubdomains of a URL, using the Public Suffix List.
from tldextract import tldextract
import requests
from requests.auth import HTTPProxyAuth
import re
reload(sys)
sys.setdefaultencoding('utf8')

# sys.path.append('C:\Users\\310230279\Dropbox\CS6200_V_Sangwan\HW3\src\Resource')
sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW3/src/Resource')

import Resource

#############################################################
class UrlParser:

    def __init__(self):
        print "welcome to the url parser"
        self._keyTerms = Resource.KeyTerms
        self._ignoreWordsInUrl = Resource.IgnoreWords
        print self._ignoreWordsInUrl

        self._OutlinksFileHandle = ""

    def __FetchRobotFileInfo__(self, url, robotDictForDomains,timeStamp):
        domainName = self.__GetComSubdomainOfUrl__(url)
        robotUrl=""

        if robotDictForDomains.has_key(domainName) == False:
            robotUrl = self.__GetRobotUrlForUrl__(domainName)
            cache = RobotsCache()
            try:
                timeStamp[domainName] = datetime.datetime.now()
                robotFileObj = cache.fetch(robotUrl)
                doesUrlExistOnline = self.__DoesUrlExistOnline__(robotUrl)
            except:
                doesUrlExistOnline = False
                robotDictForDomains[domainName] = (doesUrlExistOnline, object)


            if doesUrlExistOnline == True:
                robotDictForDomains[domainName] = (doesUrlExistOnline, robotFileObj)
            else:
                robotDictForDomains[domainName] = (doesUrlExistOnline, object)


        doesUrlExistOnline = robotDictForDomains[domainName][0]
        robotFileObj = robotDictForDomains[domainName][1]
        # print "heyyy",robotUrl, doesUrlExistOnline, robotFileObj, robotDictForDomains
        return doesUrlExistOnline, robotFileObj, robotDictForDomains, timeStamp, domainName

    def __IsUrlAllowedInRobotFile1__(self, url, robotDictForDomains, domainName):
        try:
            # proxyDict = {
            #     'http': 'http://amec.zscaler.philips.com:9480',
            #     'https': 'http://amec.zscaler.philips.com:9480'
            # }
            # auth = HTTPProxyAuth('310230279', 'April@2016')
            # page = requests.get(url, proxies=proxyDict, auth=auth)
            print  "ffff1"
            # robotFileObj = cache.fetch(robotUrl,proxies=proxyDict, auth=auth)
            # print  "ffff2"
            # robotFileObj = cache.fetch(robotUrl)
            robotFileObj = robotDictForDomains[domainName]
            isAllowed = robotFileObj.allowed(url, "Slurp") or robotFileObj.allowed(url, "*")
        except:
            print  "ffff3"
            isAllowed = True

        print  "isallowed in robot", isAllowed
        return isAllowed


    def __GetAllOutLinksForAPage__(self,url, pageContent, frontierQueue, processedUrls, documentDepthDict):
        try:
            absoluteOutlinkUrls = []
            with open(Resource.OutlinkPath, "a+") as handle:
                self._OutlinksFileHandle = handle
            # print doesUrlExistOnline
                for link in BeautifulSoup(pageContent, parseOnlyThese=SoupStrainer('a')):

                    if link.has_attr('href'):
                        outlinkUrl = link['href']
                        outlinkText =  link.text
                        title = link.title


                        if self.__IsRelativeUrlNotLegit__(outlinkUrl):
                            # print "URL is not legit"
                            continue

                        if not bool(urlparse.urlparse(outlinkUrl).netloc):
                            outlinkUrl = urljoin(url, outlinkUrl)

                        # outlinkUrl = outlinkUrl.lower()

                        outlinkUrl = self.__CanonicalizeUrl__(outlinkUrl)
                        # print "Outlink after canoniclization ... ", outlinkUrl
                        absoluteOutlinkUrls.append(outlinkUrl)

                        isUrlAlreadyProcessed = self.__IsUrlALreadyProcessed__(outlinkUrl, processedUrls)
                        # print "Is outlink already PROCESSED? - ", isUrlAlreadyProcessed
                        if isUrlAlreadyProcessed:
                            # print "Outlink is DROPPED."
                            continue

                        isUrlStillInFrontier =  self.__IsUrlStillInFrontier__(outlinkUrl, frontierQueue)
                        # print "Is outlink already in FRONTIER? - ", isUrlStillInFrontier
                        if isUrlStillInFrontier:
                        #     print "Outlink is DROPPED."
                            continue

                        # print outlinkUrl, outlinkText, title, link
                        priorityValue = self.__GetPriorityValueFromMagicFunction__(link, outlinkUrl)
                        # print "Priority queue value :", priorityValue

                        # if priorityValue > -1:
                        #     # print "No key term exist in this URL."
                        #     continue
                        # else:
                        # outlinkUrl = outlinkUrl.lower()
                        frontierQueue.put((priorityValue,outlinkUrl))
                        # documentDepthDict[outlinkUrl] = documentDepthDict[url] + 1
                        # print "depth is", documentDepthDict[outlinkUrl]

                        handle.writelines(str(priorityValue) + " " +outlinkUrl + "\n")
                        # print "absoluteOutlinkUrls",absoluteOutlinkUrls, outlinkUrl


                    # print "******Outlink is ADDED to the Frontier queue.******"


                handle.close()
            # print "\n"
            # self._OutlinksFileHandle.close()
            return frontierQueue, processedUrls,absoluteOutlinkUrls, documentDepthDict
        except:
            print "exc occured"
            return frontierQueue, processedUrls,absoluteOutlinkUrls, {}


    def __DoesStartWithDoubleSlash__(self, url):
        return url.startswith('//')


    def __GetSchemeFromUrl__(self, url):
        parseResult = urlparse.urlparse(url)
        scheme = parseResult[0]
        if len(scheme) > 0:
            return scheme+":"
        return "https:"


    def Is_UrlRelative(self, url):
        parsedResult = urlparse.urlparse(url)
        scheme = parsedResult[0]
        netloc = parsedResult[1]

        return len(scheme) == 0 and len(netloc) == 0


    def __GetRobotUrlForUrl__(self, domainName):
        robotLinkUrl = "http://www." + domainName + ".org/robots.txt"
        return robotLinkUrl


    def __IsOutlinkAllowedInRobotFile__(self, url, doesRobotFileExist, robotFileObj):

        if doesRobotFileExist == True:
            # print "gggggg", robotFileObj.allowed(url, "Slurp") or robotFileObj.allowed(url, "*")
            return robotFileObj.allowed(url, "Slurp") or robotFileObj.allowed(url, "*")

        return True


    def __GetComSubdomainOfUrl__(self, url):
        urlExtractedResults = tldextract.extract(url)
        domainName = urlExtractedResults.domain

        # returns google for  "http://www.google.com/robots.txt"
        return str(domainName)


    def __DoesUrlExistOnline__(self, url):
        try:
            request = requests.get(url)
            # print "kkkkk", url,request.status_code
        except:
            return False

        if request.status_code == 200:
            return True

        return False


    def __IsRelativeUrlNotLegit__(self, relativeUrl):
        return relativeUrl.startswith('#') == True \
               or relativeUrl.startswith("?") == True


    def __CanonicalizeUrl__(self, url):
        parsedResult = urlparse.urlparse(url)
        scheme = parsedResult[0]
        netloc = parsedResult[1]
        path = parsedResult[2]

        finalUrl = scheme+"://" + netloc.replace(":80", "").replace(":443", "") + path
        sp = finalUrl.split(scheme+"://")
        finalUrl = "http://"+sp[1]
        return finalUrl


    def __IsUrlSeenFirstTime__(self,outlinkUrl, frontierQueue, processedUrls):
        return not self.__IsUrlALreadyProcessed__(outlinkUrl, processedUrls) and \
               not self.__IsUrlStillInFrontier__(outlinkUrl, frontierQueue)

    def __IsUrlALreadyProcessed__(self, url, processedUrls):
        return url in processedUrls

    def __IsUrlStillInFrontier__(self, url, frontierQueue):
        return url in (x[1] for x in frontierQueue.queue)

    def __GetPriorityValueFromMagicFunction__(self, link, outlink):
        noOfTermsFoundinLink = 0

        self._keyTerms = ["cold","war","nuclear","spies","nuclear","libert","proxy wars","Nuclear", "Winter","B53", "Bomb","Project", "Azorian","Iron", "Curtain","Berlin", "Wall"]
        query = str(outlink)
        for term in self._keyTerms:
            if term.lower() in query.lower():
                # print "term", term, outlink
                noOfTermsFoundinLink = 1
                break

        # if "cold-war" in query.lower() or "cold_war" in query.lower():
        #     noOfTermsFoundinLink = noOfTermsFoundinLink * 2
        #
        # if ("war" in query.lower() or "cold" in query.lower()) and noOfTermsFoundinLink == -1:
        #     noOfTermsFoundinLink * -5

        return noOfTermsFoundinLink * -1



# up = UrlParser()
# print up.__IsUrlAllowedInRobotFile1__("ss[dd;;",object)
# print up.__GetPriorityValueFromMagicFunction__("http://vec.wikipedia.org/wiki/Illinois")

# up.__CanonicalizeUrl__('http://www.cwi.nl:80/%7Eguido/Python.html')
# up.__CanonicalizeUrl__('http://www.washingtonpost.com/sports/table-tennis-pingpong-or-whiff-whaff-victorian-parlor-game-returns-home-for-london-olympics/2012/07/27/gJQAXnpmDX_story.html')
# up.__CanonicalizeUrl__('https://en.wikipedia.org:443/wiki/w/index.php?title=Table_tennis&action=edit&section=37')
# up.__CanonicalizeUrl__('/wiki/Table_tennis/#cite_note-1')




