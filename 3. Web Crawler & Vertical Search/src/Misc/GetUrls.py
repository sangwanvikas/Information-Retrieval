import os, re
import requests, urlfetch, time
import urllib2
outputPath = "C:\\vikas\\CS6200\\HW33\\output"


# ----------------------------------------------------------------------------
for root, dirs, files in os.walk(outputPath):
    c=0
    for file in files:
        filePath = os.path.join(root, file)

        f = open(filePath, 'r')
        fileContent = f.read()

        print "Processing url from ",filePath
        with open("uq.txt","a+") as handle:
            c = c+ 1
            print c
            url = str(re.findall(r'<URL>(.*?)</URL>', fileContent, re.DOTALL)[0]) + "\n"
            if "http://allthingsnuclear.org/category/china" in url or "http://www.britannica.com/eb/article-9056451/nuclear-winter" in url:
                continue
            # text = str(re.findall(r'<TEXT>(.*?)</TEXT>', fileContent, re.DOTALL)[0]) + "\n"
            # if "404 - Error" not in text and "500 - Error" not in text:
            handle.writelines(url)
# ----------------------------------------------------------------------------
# unrequiredUrls = []
# with open("uq1.txt", "r") as handle:
#     opener = urllib2.build_opener(urllib2.HTTPRedirectHandler)
#     c=0
#     while handle:
#         url = handle.readline()
#
#         if "http://ww1centenary.oucs.ox.ac.uk/space-into-place/commonwealth-cemeteries-of-world-war-one/about/about/about/" in url:
#             c += 1
#             unrequiredUrls.append(url)
#             # print c, url
#             if c==661:
#                 break
# with open("delete.txt","w") as handle:
#
#     for url in unrequiredUrls:
#         print url
#         handle.write(url)
# ----------------------------------------------------------------------------


        # request = opener.open(url)
        # print url, request.url



        # response = urlfetch.fetch(url, follow_redirects=True)
        #
        # if response.headers.has_key('location'):
        #     location = response.headers["location"]
        #     print url, location
        #     time.sleep(.5)

        # else
        #     print url

        # response = requests.get(url)
        # print "-----------------------------"
        # if response.history:
        #     print "Request was redirected"
        #     for resp in response.history:
        #         print resp.status_code, resp.url.encode('utf-8')
        #     print "Final destination:"
        #     print response.status_code, response.url.encode('utf-8')
        # else:
        #     print "Request was not redirected"

