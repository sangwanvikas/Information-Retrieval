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
import lda
import textmining

currDirPath = os.path.abspath(os.curdir)
os.chdir("..")
srcDirPath =  os.path.abspath(os.curdir)

sys.path.append(srcDirPath +"/Resource")
import Resource
################################################################################################
class TopicModelProcessor:
    TopicCount  = 200
    IterationCount = 100 # higher it is, better the score.
    RandomState = 1
    ############################################################################################
    def __init__(self, docIdCommaDocTextFilePath, docTermMatrixFilePath, docTopicProbDistrFilePath):
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
        self._docTopicProbDistrFilePath = docTopicProbDistrFilePath

    ############################################################################################
    def __RunTopicModelForAQId__(self):
        print "Generating topic model for whole AP89 corpus..."

        totalNoOfDocs = len(self._docId_comma_documentsText_tuple_list)

        print "Running Topic Model for all document [Documents# %d] ..." %totalNoOfDocs
        print "Defining LDA model ..."
        model = lda.LDA(n_topics = TopicModelProcessor.TopicCount,
                        n_iter = TopicModelProcessor.IterationCount,
                        random_state = TopicModelProcessor.RandomState)
        # [document-term matrix] i.e. [#Doc CROSS len(vocabsize)]

        print "Fetching textmining.TermDocumentMatrix, vocabulary and document Ids list ..."
        X, vocab, docIds = self.__GetDataSet__()

        print "Fitting model with TermDocumentMatrix ..."
        model.fit(X)

        fileHandler = open(self._docTopicProbDistrFilePath, 'w', -1)

        self.__CalculateDocTopicProbDistrMatrix__(model, fileHandler)

    def __CalculateDocTopicProbDistrMatrix__(self, model, outputFileHandler):
        print "Calculating Document-Topic probability distribution Matrix..."
        doc_topic = model.doc_topic_
        print doc_topic
        pickle.dump(doc_topic ,outputFileHandler)

        print "Result file saved. Location -> %s\n" %self._docTopicProbDistrFilePath

    def __GetDataSet__(self):
        docTermMatrix = []
        vocab = []
        docIds = []

        for i in range(len(self._docId_comma_documentsText_tuple_list)):
            print i, " extraction.. "
            docId, documentText = self._docId_comma_documentsText_tuple_list[i]
            # tdm.add_doc(documentText.lower())
            docIds.append(docId)

        docTermMatrix = self.__LoadFromPickle__(self._docTermMatrixFilePath)

        return np.array(docTermMatrix), vocab, docIds

    ##############################################################################################

    def __LoadQidToDocumentsTextList__(self):
        print "Loading datasets...\n"
        self._docId_comma_documentsText_tuple_list = self.__LoadFromPickle__(self._QIdToDocumentsTextFilePath)
        # for docIdCommaText in self._docId_comma_documentsText_tuple_list:
        #     print docIdCommaText

    ##############################################################################################
    def __LoadFromPickle__(self, filePath):
        with open(filePath, 'r') as handle:
            return pickle.load(handle)

############################################################################################
##############################################################################################
print datetime.datetime.now().time()
obj = TopicModelProcessor(Resource.DocIdCommaDocTextFilePath,
                          Resource.DocTermMatrixFilePath,
                          Resource.DocTopicProbDistrFilePath)
obj.__LoadQidToDocumentsTextList__()
obj.__RunTopicModelForAQId__()
print datetime.datetime.now().time()
