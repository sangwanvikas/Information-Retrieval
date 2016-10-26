################################################################################################
# Pre requisite for this script : DocumentSetGenerator.cs script must have run to load data (#3 & #4).
# 1. Install lda and textmining packages to Python2.7.9.
# 2. Numpy is already installed.
# 3. Load List of tuple (documentId, documentText)
# 4. Calculate Document-Term Matrix(X), vocabulary using 'textmining' library.
# 5. Ftr LDA model with X (calculated above)
# 6. Get Document-Topic probability distribution i.e. find all relevant topics for each document for each query.
#       (using doc_topic = model.doc_topic_)
# 7. Generate a file for saving results (obtained in #6)
################################################################################################

import os, sys, pickle, datetime

import numpy as np
import textmining


currDirPath = os.path.abspath(os.curdir)
os.chdir("..")
srcDirPath =  os.path.abspath(os.curdir)

sys.path.append(srcDirPath +"/Resource")
import Resource
################################################################################################
class DocumentTermMatrixGenerator:
    TopicCount  = 200
    IterationCount = 100 # higher it is, better the score.
    RandomState = 1
    ############################################################################################
    def __init__(self, docIdCommaDocTextFilePath, docTermMatrixFilePath):
        # --------------------------------------------------------------------
        # [
        #     ("AP85-101","Text from First document for AP-43"),
        #     ("AP85-102", "Text from second document for AP-43"),
        #     ("AP85-103","Text from First document for AP-43"),
        #     ("AP85-104", "Text from second document for AP-43")
        # ]
        self._docId_comma_documentsText_tuple_list = []
        self._QIdToDocumentsTextFilePath = docIdCommaDocTextFilePath
        # --------------------------------------------------------------------
        self._docTermMatrixFilePath = docTermMatrixFilePath

    ############################################################################################
    def __RunTopicModelForAQId__(self):
        totalNoOfDocs = len(self._docId_comma_documentsText_tuple_list)

        print "Generating Document-Topic matrix for whole AP89 corpus. [Documents# %d] ..." %totalNoOfDocs
        print "Fetching Document-Term Matrix, vocabulary and document Ids list ..."

        corpus, vocab, docIds = self.__GetDataSet__()

        fileHandler = open(self._docTermMatrixFilePath, 'w', -1)
        self.__DumpDocTermMatrix__(corpus, fileHandler)

    def __DumpDocTermMatrix__(self, doc_topic, outputFileHandler):
        print "Dumping Document-Term Matrix generator ..."

        pickle.dump(doc_topic ,outputFileHandler)

        print "Result file saved. Location -> %s\n" %outputFileHandler

    def __GetDataSet__(self):
        docTermMatrix = []
        vocab = []
        docIds = []
        tdm = textmining.TermDocumentMatrix()

        for i in range(len(self._docId_comma_documentsText_tuple_list)):
            print i, " extraction.. "
            docId, documentText = self._docId_comma_documentsText_tuple_list[i]
            tdm.add_doc(documentText.lower())
            # docIds.append(docId)

        i = -1
        for row in tdm.rows(cutoff = 3):
            row = row[0:18000]
            i += 1
            # First row of 'document-term matrix' is vocabulary
            if i==0:
                for vocabWord in row:
                    vocab.append(vocabWord)
                continue
            print i, "Loading from tdm matrix.."
            # Remaiing rows are []
            docTermMatrix.append(row)

        print "Converting doc-term matrix to numpy array..."
        return np.array(docTermMatrix), vocab, docIds

    ##############################################################################################

    def __LoadQidToDocumentsTextList__(self):
        print "Loading datasets...\n"
        self._docId_comma_documentsText_tuple_list = self.__LoadFromPickle__(self._QIdToDocumentsTextFilePath)

    ##############################################################################################
    def __LoadFromPickle__(self, filePath):
        with open(filePath, 'r') as handle:
            return pickle.load(handle)

############################################################################################
##############################################################################################
print datetime.datetime.now().time()
obj = DocumentTermMatrixGenerator(Resource.DocIdCommaDocTextFilePath,
                          Resource.DocTermMatrixFilePath)
obj.__LoadQidToDocumentsTextList__()
obj.__RunTopicModelForAQId__()
print datetime.datetime.now().time()
