#############################################################
#START
# TODO Ignore .mp3 , .png etc
# for .mp3, .png etc kind of pages, also don't create file for them
#############################################################
import sys, os, re
from bs4 import BeautifulSoup, SoupStrainer
import xml.etree.ElementTree as ET
import html2text

reload(sys)
sys.setdefaultencoding('utf8')

# sys.path.append('C:\Users\\310230279\Dropbox\CS6200_V_Sangwan\HW3\src\Resource')
sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW3/src/Resource')
import Resource

#############################################################
class DocumentParser:
    def __init__(self):
        print "hi from DocumentParser"

    def __IsPageHtml__(self, pageHeader):
        pageType = pageHeader['Content-Type']
        if "html" in pageType:
            return True

    def __CleanPageContent__(self, pageContent):
        try:
            # create a new bs4 object from the html data loaded
            soup = BeautifulSoup(pageContent)
            # remove all javascript and stylesheet code
            for script in soup(["script", "style"]):
                script.extract()
            # get text
            text = soup.get_text()
            # break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            text =  text.replace("\n", " ")
            text = text.replace("  ", " ")

            # clean remaining contents
            h = html2text.HTML2Text()
            h.ignore_links = True
            text = h.handle(text)

            return str(text)
        except:
            return ""

    def __CreateFileInAP89Format__(self, url, cleanedText, docId, rawText, httpHeader, outLinks):
        filePath = Resource.outputDirPath+"//" + docId+".txt"

        with open(filePath, "w") as templateHandle:
            line1 = "<DOC>\n"
            line11 = "<AUTHOR>Vikas</AUTHOR>\n"
            line2 = "<DOCNO>"+docId+"</DOCNO>\n"
            line21 = "<URL>" + url.lower().replace("https","http") + "</URL>\n"
            line22 = "<TITLE>"+self.__GetTitle__(rawText) +"</TITLE>\n"
            line3 = "<TEXT>" +cleanedText+"\n</TEXT>\n"
            line31 = "<RAW>"+rawText+"</RAW>\n"
            line32 = "<HTTPHEADER>"+httpHeader+"</HTTPHEADER>\n"
            line33 = "<OUTLINKS>"+outLinks.lower().replace("https","http")+"</OUTLINKS>\n"
            line4 = "</DOC>"
            fileContent = line1+line11+ line2+line21+ line22+ str(line3) +line31+line32+line33+ line4
            templateHandle.write(fileContent)
            templateHandle.close()


    def __GetTitle__(self,rawText):
        titleList = re.findall(r'<title>(.*?)</title>', rawText, re.DOTALL)
        if len(titleList) == 0:
            return ""

        return titleList[0]


# d = DocumentParser()
# d.__CreateFileInAP89Format__("df","Df")
