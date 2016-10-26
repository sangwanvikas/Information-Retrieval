##########################################################################################################
# This class :
# Read emails from a directory, parse and clean content.
# Using given mapping find if a given email text file is SPAM or HAM.
# Determine Training and Testing data (75%-25%)
# Construct an object to be able to index to ElasticSearch.
# Indexes all email objects with the help of ElasticSearchManager class
##########################################################################################################

import os, re, sys,string, datetime
from time import sleep
import pyzmail

currDirPath = os.path.abspath(os.curdir)
os.chdir("..")
srcDirPath =  os.path.abspath(os.curdir)


sys.path.append(srcDirPath +"/Resource")
sys.path.append(srcDirPath+"/ElasticSearchManager")
sys.path.append(srcDirPath +"/MyHTMLParser")

import Resource
import email
from MyHTMLParser import MyHTMLParser
from ElasticSearchManager import ElasticSearchManager

##########################################################################################################

class EmailPrser():
    DocumentCounter = 0
    TestingDataInPercent = 25

    #########################   Constructor #######################################
    def __init__(self, emailDirPath, spamMappingFilePath):
        self._emailDirPath = emailDirPath
        self._spamIdentifierMapFilePath = spamMappingFilePath

        # {'inmail.1' :'Spam', 'inmail.10':'Ham',...........'inmail.200':'Spam'}
        self._emailFileNameToSpamOrHamMap = {}
        self._emailFileNameToSpamOrHamMap = self.__LoadFileNameToSpamOrHamMapping__(self._spamIdentifierMapFilePath)

        self._myHtmlParserObj = MyHTMLParser()
        self.fp = "test.txt"

        if os.path.isfile(self.fp) :
            os.remove(self.fp)
        with open(self.fp, 'w') as handle:
            handle.write(str(datetime.datetime.now()))
        self.bulkList = []

        self._ESMgrObject = ElasticSearchManager(Resource.INDEX_NAME, Resource.TYPE_NAME)

    ##############################################################################
    def __LoadFileNameToSpamOrHamMapping__(self, spamIdentifierMapFilePath):
        fileNameToSpamOrHamMapping = {}
        with open(spamIdentifierMapFilePath, 'r') as handle:
            for aLine in handle:
                # aLine -> spam ../data/inmail.1
                SpamOrHam, relativeFilePath = aLine.split(' ')
                fileName = (relativeFilePath.split('/')[-1]).strip('\n')
                fileNameToSpamOrHamMapping[fileName] = SpamOrHam

        return fileNameToSpamOrHamMapping

    def __IndexAllEmailsInDirectory__(self, emailDirPath):
        print "All emails are present in directory -> ", emailDirPath
        fileCounter = -1
        print '\n'
        bulkList = []
        i = 0
        for root, dirs, files in os.walk(emailDirPath):
            for file in files:
                # To find which document is missing from the email documents directory
                # i = i +   int(os.path.basename( os.path.join(root, file)).split('.')[1])
                # print i
                # continue

                emailFilePath = os.path.join(root, file)
                fileCounter += 1

                fileName = os.path.basename(emailFilePath)

                # if len(fileName) == 11 or len(fileName) == 10:
                LabelSpamOrHam = self.__GetLabelAsSpamOrHam__(fileName)
                SplitTrainOrTest = self.__GetSplitAsTrainOrTest__(fileCounter)

                print "Cleaning...",fileCounter+1, '/ 75149. ',fileName, LabelSpamOrHam, SplitTrainOrTest
                # emailFilePath = 'C:/Users/vikas/Dropbox/sangwan.ea@gmail.com/hw7/Input/trec07p/data\inmail.1885'
                emailContent = self.__GetEmailContent__(emailFilePath)
                # print emailContent

                # self.__IndexesEmailDoc__(fileName, emailContent, LabelSpamOrHam, SplitTrainOrTest)
                logicalDocumentForElasticSearch = self.__ConsituteDocument__(fileName, emailContent, LabelSpamOrHam, SplitTrainOrTest)
                bulkList.append(logicalDocumentForElasticSearch)

                # if emailFilePath == 'C:/Users/vikas/Dropbox/sangwan.ea@gmail.com/hw7/Input/trec07p/data\inmail.1884':
                #     print "220"
                #     print logicalDocumentForElasticSearch
                #     exit()

            #     self.__IndexesDocsInBulk__(bulkList)
            #     exit()

        sleep(.5)
        print "Indexing all email in bulk..."
        self.__IndexesDocsInBulk__(bulkList)
        exit()

        res = self._ESMgrObject.__CurrentIndexStats__()
        print str(res["count"]) + "/ 75149", "documents indexed.\n"

    def __GetEmailContent__(self, filePath):
        self._myHtmlParserObj = MyHTMLParser()
        emailContent = ""
        with open(filePath, 'r') as handle:
                emailMessage  = email.message_from_file(handle)

                emailBody = ""
                if emailMessage.is_multipart():
                    for part in emailMessage.walk():

                        if part.get_content_type() == "text/html" or part.get_content_type() == "text/plain":
                            partPayload = part.get_payload()
                            emailBody = emailBody + ' ' + partPayload
                else:
                    if emailMessage.get_content_type() == "text/html" or emailMessage.get_content_type() == "text/plain":
                        emailBody = emailMessage.get_payload()




                # Cleaning email content
                emailSubject = ''
                if emailMessage.has_key('subject'):
                    emailSubject = self.__CleanEmailContent__(emailMessage['subject'])

                emailContent = self._myHtmlParserObj.GetParsedContentFromHtml(emailBody)

                emailContent = str(emailSubject) + " "+ str(emailContent)
                emailContent = self.__CleanEmailContent__(emailContent)

                return emailContent

    def __CleanEmailContent__(self,emailContent):
        #  Remove new line char
        emailContent = emailContent.replace('\n', ' ')
        #  Remove other than alphabets and numbers
        emailContent = re.sub('[^a-zA-Z0-9\n]', ' ', emailContent)
        # all words in lower case
        emailContent = emailContent.lower()
        # Remove multiple spaces between words
        emailContent = re.sub(' +', ' ', str(emailContent))
        return emailContent

    def __GetLabelAsSpamOrHam__(self, fileName):
       return self._emailFileNameToSpamOrHamMap[fileName]

    def __GetSplitAsTrainOrTest__(self,fileCounter):
        everyNthNoForTest = 100 / EmailPrser.TestingDataInPercent
        TrainOrTest = 'train'
        if (fileCounter + 1) % everyNthNoForTest == 0:
            TrainOrTest = 'test'

        return  TrainOrTest

    def __IndexesEmailDoc__(self, fileName, emailContent, SpamOrHam, TrainOrTest):
        self._ESMgrObject.__IndexDoc__(fileName, emailContent,SpamOrHam, TrainOrTest)


    def __ConsituteDocument__(self, fileName, emailContent, SpamOrHam, TrainOrTest):
        action = {"_index": Resource.INDEX_NAME, '_type': Resource.TYPE_NAME, '_id': fileName, '_source': {
            "text": emailContent,
            "label" : SpamOrHam,
            "split" : TrainOrTest,
            "name": fileName
        }}
        return action

    def __IndexesDocsInBulk__(self, bulkList):
        self._ESMgrObject.__IndexBulkDoc__(bulkList)
##########################################################################################################
# Run this script to Index all en=mail in the given directory.
##########################################################################################################
print "Program started at :", datetime.datetime.now().time()
EmailDirPath = Resource.EmailDirectoryPath
SpamMappingFilePath = Resource.SpamIdentifierMapFilePath

x = EmailPrser(EmailDirPath, SpamMappingFilePath)
x.__IndexAllEmailsInDirectory__(x._emailDirPath)

# print datetime.datetime.now().time()
# print x.__IsTrainingORTesting__(5)
##########################################################################################################
# END
##########################################################################################################

