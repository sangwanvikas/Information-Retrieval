################################################################################################
# Pre requisite for this script : DocumentSetGenerator.cs script must have run to load data (#3).
# 1. Install lda and textmining packages to Python2.7.9.
# 2. Numpy is already installed.
# 3. Load dictionary mapping QueryId to List of tuple (documentId, documentText)
# 4. Load all queries which Topic model is going to run for.
# 5. Calculate Document-Term Matrix(X), vocabulary using 'textmining' library.
# 6. Fit LDA model with X (calculated above)
# 7. Generate Topic-Word probability distribution i.e. Calculate top 10-20 topics for each query.
#       (using topic_word = model.components_)
# 8. Document-Topic probability distribution i.e. find all relevant topics for each document for each query.
#       (using doc_topic = model.doc_topic_)
# Generate a file for each query saving results (calculated in #7 and #8)
################################################################################################

import os, sys, pickle
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
    TopicCount  = 20
    IterationCount = 1500 # higher it is, better the score.
    RandomState = 1
    TopWordsCountForATopic = 20
    def __init__(self, qIdToDocumentsTextMapFilePath, allQueryIdsFilePath, matrixFilePath, topicModelResultsFilePath):
        # --------------------------------------------------------------------
        # {
        #     'AP-43':[
        #               ("AP85-101","Text from First document for AP-43"),
        #               ("AP85-101", "Text from second document for AP-43")
        #             ],
        #     'AP-100':[
        #               ("AP85-101","Text from First document for AP-43"),
        #               ("AP85-101", "Text from second document for AP-43")
        #             ],
        #     ....
        #     'AP-99':[
        #               ("AP85-101","Text from First document for AP-43"),
        #               ("AP85-101", "Text from second document for AP-43")
        #             ],
        # }
        self._qid_to_documentsTextList_Map = {}
        self._QIdToDocumentsTextFilePath = qIdToDocumentsTextMapFilePath
        # --------------------------------------------------------------------
        # [51,60,83]
        self._all_queryIds_list = []
        self._allQueryIdsFilePath = allQueryIdsFilePath
        # --------------------------------------------------------------------
        self._matrixFilePath = matrixFilePath
        self.topicModelResultsFilePath = topicModelResultsFilePath

   ############################################################################################
    def __GenerateTopicsForAllQIds__(self):
        print "Generating topic model for all %d queries..." %len(self._all_queryIds_list)
        i = 0
        for qId in self._all_queryIds_list:
            i += 1
            self.__RuntTopicModelForAQId__(i, qId)

    def __RuntTopicModelForAQId__(self, i, qId):
        outputFileNameForThisQuery =  '{}/{}.txt'.format(self.topicModelResultsFilePath, qId)
        fileHandler = open(outputFileNameForThisQuery, 'w')
        totalNoOfDocs = len(self._qid_to_documentsTextList_Map[qId])
        print "Generating Document-Term Matrix for queryId %d, which contains %d documents ..." %(qId, totalNoOfDocs )

        queryId = qId
        print "%d/%d Running Topic Model for qId %s [Documents# %d] ..." %(i, len(self._all_queryIds_list), qId, totalNoOfDocs)

        model = lda.LDA(n_topics = TopicModelProcessor.TopicCount,
                        n_iter = TopicModelProcessor.IterationCount,
                        random_state = TopicModelProcessor.RandomState)
        # [document-term matrix] i.e. [#Doc CROSS len(vocabsize)]
        X, vocab, docIds = self.__GetDataSetForAQueryId__(queryId)

        model.fit(X)

        # a. Topic - Word probability distribution. Top 10-20 for each Topic
        topic_word = model.components_  # model.components_ also works

        for i, topic_dist in enumerate(topic_word):
            topic_words = np.array(vocab)[np.argsort(topic_dist)][:-(TopicModelProcessor.TopWordsCountForATopic + 1):-1]
            topicWordResult = 'Topic {}: {}'.format(i, ' '.join(topic_words))
            fileHandler.write(topicWordResult + "\n")

        # b. Document - Topic probability distribution
        # [scores for topics] for each document for qId  i.e. [#Doc CROSS #Topics]
        doc_topic = model.doc_topic_
        for i in range(totalNoOfDocs):
            documentTopicsResult = "{} {} (top topic: {})".format(i+1, docIds[i], doc_topic[i].argsort())
            fileHandler.write(documentTopicsResult + "\n")

        print "Result file saved. Location -> %s\n" %outputFileNameForThisQuery

    def __GetDataSetForAQueryId__(self, queryId):
        docTermMatrix = []
        vocab = []
        docIds = []
        tdm = textmining.TermDocumentMatrix()
        documentsTextList =  self._qid_to_documentsTextList_Map[queryId]

        for i in range(len(documentsTextList)):
            docId, documentText = documentsTextList[i]
            tdm.add_doc(documentText.lower())
            docIds.append(docId)

        # Write Document-Term matrix
        tdm.write_csv(self._matrixFilePath, cutoff=3)

        # Load docTermMatrix  and vocabulary.
        i = -1
        for row in tdm.rows(cutoff=1):
            i += 1
            # First row of 'document-term matrix' is vocabulary
            if i==0:
                for vocabWord in row:
                    vocab.append(vocabWord)
                continue
            # Remaiing rows are []
            docTermMatrix.append(row)

        return np.array(docTermMatrix), vocab, docIds

    ##############################################################################################
    def __LoadQidToDocumentsTextList__(self):
        print "Loading datasets...\n"
        self._qid_to_documentsTextList_Map = self.__LoadFromPickle__(self._QIdToDocumentsTextFilePath)

    ##############################################################################################
    def __LoadFromPickle__(self, filePath):
        with open(filePath, 'r') as handle:
            return pickle.load(handle)

    #############################################################################################
    def __LoadAllQueryIds__(self):
        print "Loading all queries from %s..." %self._allQueryIdsFilePath
        with open(self._allQueryIdsFilePath,'r') as handle:
            for line in handle:
                qId =  int(line.strip())
                self._all_queryIds_list.append(qId)
        print "Program is running for # %d queries" % len( self._all_queryIds_list)
        print "Query Ids :", self._all_queryIds_list,"\n"

    ############################################################################################

#######################################################
# Run in Python2.7.9
obj = TopicModelProcessor(Resource.QIdToDocumentsTextMapFilePath,
                          Resource.AllQueryIdsFilePath,
                          Resource.DocumentTermMatrixFilePath,
                          Resource.TopicModelResultsFilePath)
obj.__LoadQidToDocumentsTextList__() # Load - self._qid_to_documentsTextList_Map
obj.__LoadAllQueryIds__() # Load - self._all_queryIds_list
obj.__GenerateTopicsForAllQIds__()