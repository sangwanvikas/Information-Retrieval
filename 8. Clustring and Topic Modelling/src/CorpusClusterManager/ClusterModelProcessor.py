################################################################################################
# Pre requisite for this script : TopicModelProcessor .cs script must have run to load data (#3 & #4).
# 1. Install KMeans packages to Portable Python2.7.6.
# 2. Load Document-Term Probability Distribution.
# 3. Load Index To Document Id Dictionary.
# 4. Run K-MEAN Clustering Partitioning Algorithm.
# 5. Dump DocumentIds which are Grouped by ClusterIds
################################################################################################
import os, sys, pickle, datetime
from sklearn.cluster import KMeans

currDirPath = os.path.abspath(os.curdir)
os.chdir("..")
srcDirPath =  os.path.abspath(os.curdir)

sys.path.append(srcDirPath +"/Resource")
import Resource
################################################################################################
class ClusterModelProcessor:
    n_samples = 1500
    RandomState = 170
    NumberOfClusters = 25 # n_clusters <= n_samples(i.e. # rows in X)
    if NumberOfClusters > Resource.CorpusSize:
        NumberOfClusters = Resource.CorpusSize
    print "Clustering will run for K = %d \n" %NumberOfClusters

    #########################################################################################
    def __init__(self, docTopicProbDistrFilePath, docIdCommaDocTextFilePath, resultsForEachClusterFilePath):
        # -----------------------------------------------------------------
        # [ n_docs CROSS n_topics] i.e. [84670 CROSS 200]
        # [   [ 0.00049751  0.00049751  0.00049751 ...,  0.00049751  0.00049751 0.00547264]
        #     [ 0.00044843  0.00044843  0.00044843 ...,  0.00044843  0.00044843 0.00044843]
        # ]
        self._doc_to_term_prob_dist = []
        self._docTopicProbDistrFilePath = docTopicProbDistrFilePath
        # -----------------------------------------------------------------
        # {
        #     0: 'AP890210-0144',
        #     1: 'AP890210-0145',
        #     ...
        #     84677: 'AP890210-0147',
        #     84678: 'AP890210-0148'
        # }
        self._index_to_docId_map = {}
        self._docIdCommaDocTextFilePath = docIdCommaDocTextFilePath
        # -----------------------------------------------------------------
        self._clusterId_to_documentIds_map = {}
        self._outputResultsForEachClusterFilePath = resultsForEachClusterFilePath
    #####################################################################################
    def __RunClusteringPartitioningAlgorithm__(self):
        print "Running K-MEAN clustering partitioning algorithm for # %d documents ..." %len(self._index_to_docId_map)

        X = self._doc_to_term_prob_dist
        print "K-MEAN Model defined !!"
        estimator = KMeans(n_clusters = ClusterModelProcessor.NumberOfClusters,
                        random_state = ClusterModelProcessor.RandomState)

        print "Fitting Clustering model with Doc-Term Probability distribution Matrix ..."
        estimator.fit(X)    # estimator.fit_predict(X)

        # [1 1 0 2 1 1 1 1 4 3] when n_clusters = 5 and # rows in X = 10 i.e. total 10 docIs
        print "Calculating cluster labels ..."
        labels = estimator.labels_

        self._clusterId_to_documentIds_map = self.__GetDocumentIdsGroupedByClusterId__(labels)

    def __GetDocumentIdsGroupedByClusterId__(self, labels):
        print "Grouping documentIds by respective ClusterIndex..."
        labelIdToDocumentIds = {}

        for i in range(len(labels)):
            clusterId = labels[i]
            docId = self._index_to_docId_map[i]

            if not labelIdToDocumentIds.has_key(clusterId):
                labelIdToDocumentIds[clusterId] = []

            labelIdToDocumentIds[clusterId].append(docId)
        # print labelIdToDocumentIds
        return labelIdToDocumentIds

    def __DumpDocumentIdsGroupedByClusterId__(self):
        for clusterId, documentIds in self._clusterId_to_documentIds_map.iteritems():
            filePath = '{}/{}.txt'.format(self._outputResultsForEachClusterFilePath, clusterId)
            print "Dumping all document Ids for ClusterIndex # %d to %s..." %(clusterId, filePath)
            with open(filePath, 'w') as handle:

                for x in range(len(documentIds)):

                    documentId = documentIds[x]
                    aLine = "{} {} \n".format(x, documentId)
                    handle.write(aLine)

    #####################################################################################
    def __LoadDocToTermProbsbilityDistr__(self):
        print "Loading DocId to TermProbability distribution matrix ... (%s )" %self._docTopicProbDistrFilePath

        self._doc_to_term_prob_dist = self.__LoadFromPickle__(self._docTopicProbDistrFilePath)
        print  "Shape : ", self._doc_to_term_prob_dist.shape, "(n_docs CROSS n_topics)\n"

    #####################################################################################
    def __LoadIndexToDocIdMap__(self):
        print "Loading indexId to docId mapping ... (%s)\n" %self._docIdCommaDocTextFilePath

        docId_comma_documentsText_tuple_list = self.__LoadFromPickle__(self._docIdCommaDocTextFilePath)

        for x in range(len(docId_comma_documentsText_tuple_list)):
            docId, _ = docId_comma_documentsText_tuple_list[x]
            self._index_to_docId_map[x] = docId
        # print self._index_to_docId_map

    #####################################################################################
    def __LoadFromPickle__(self, filePath):
        with open(filePath, 'r') as handle:
            return pickle.load(handle)

################################################################################################
print datetime.datetime.now().time()
obj = ClusterModelProcessor(Resource.DocTopicProbDistrFilePath,
                            Resource.DocIdCommaDocTextFilePath,
                            Resource.ResultsForEachClusterFilePath)
obj.__LoadDocToTermProbsbilityDistr__()
obj.__LoadIndexToDocIdMap__()
obj.__RunClusteringPartitioningAlgorithm__()
obj.__DumpDocumentIdsGroupedByClusterId__()
print datetime.datetime.now().time()