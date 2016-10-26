import sys, os, re
from Queue import Queue
import pickle

documentDirPath = "C:/vikas/CS6200/HW3/output"

urlToOutlink = {}
urlToDepth = {
    "http://en.wikipedia.org/wiki/Sino-Soviet_split": 0,
    "https://www.marxists.org/history/international/comintern/sino-soviet-split/": 0,
    "http://www.gilderlehrman.org/history-by-era/seventies/essays/united-states-and-china-during-cold-war": 0,
    "http://www.atomicarchive.com/History/coldwar/": 0,
}

Q = Queue()
Q.put("http://en.wikipedia.org/wiki/Sino-Soviet_split")
Q.put("https://www.marxists.org/history/international/comintern/sino-soviet-split/")
Q.put("http://www.gilderlehrman.org/history-by-era/seventies/essays/united-states-and-china-during-cold-war")
Q.put("http://www.atomicarchive.com/History/coldwar/")


c=0
for root, dirs, files in os.walk(documentDirPath):
    for file in files:
        c+=1
        filePath = os.path.join(root, file)

        print filePath

        f = open(filePath, 'r')
        fileContent = f.read()

        documentIdList = re.findall(r'<URL>(.*?)</URL>', fileContent, re.DOTALL)
        urlAsId = documentIdList[0].replace("https", "http")
        print urlAsId

        outlinks = re.findall(r'<OUTLINKS>(.*?)</OUTLINKS>', fileContent, re.DOTALL)
        outlinksText = ""
        for outlink in outlinks:
            outlinksText = outlinksText + " " + outlink.replace("https", "http")

        outlinksList = outlinksText.split(" ")
        print outlinksList

        urlToOutlink[urlAsId] = outlinksList


print Q.qsize()
c = 0
while not Q.empty():

    url = Q.get()

    if url in urlToOutlink:

        outlinks = urlToOutlink[url]
        outlinks = list(set(outlinks))
        for outlink in outlinks:

            if outlink in urlToOutlink and outlink != url:
                depth = urlToDepth[url] + 1
                Q.put(outlink)
                urlToDepth[outlink] = depth

                print "{} {} {} {}".format(url, urlToDepth[url], outlink, depth)
                # sys.exit()


    c+=1
    print c

with open("urlToDepth.json", "wb+") as handle:
    pickle.dump(urlToDepth, handle, -1)
    handle.close()

with open("urlToDepth.json", "rb") as handle:
    print pickle.load(handle)












