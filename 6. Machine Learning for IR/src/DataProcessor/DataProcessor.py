##################################################################
# 1. QREL  -> Get all documents for each query.
# 2. For each model in Trec-Result files, fetch all documents which are present in Qresl.
# 3. Create a Feature Matrix.
##################################################################
import sys, os

sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW6/src/Resource')
sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW6/src/Enum')

import Resource
from Features import FeaturesEnum
import pickle
from sets import Set

################################################################
class DataProcessor:
    def __init__(self):
        self._enumObj = FeaturesEnum()
        self._qrelFilePath = Resource.qrelFilePath
        # {
        #  'Q51' : {'AP101' : 0/1, 'AP102' : 0/1),
        #  'Q55' : {'AP111' : 0/1, 'AP112' : 0/1}
        # }
        self._qrelDict = {}
        # {
        # 1 for IDF : {
        #       'Q51' : {'AP101' : 2.678, 'AP102' : 4.567),
        #       'Q55' : {'AP111' : 1.344, 'AP112' : .08761}
        #      },
        # 2 for JelinekMercer: {
        #       'Q51' : {'AP101' : 2.678, 'AP102' : 4.567),
        #       'Q55' : {'AP111' : 1.344, 'AP112' : .08761}
        #      },
        self._trec_Result = {}
        # {
        #   '54:P890117-0119':['0', '1.292764331', '-28.62477982', '-28.6249676978', '-35.2432771', '-35.2432771'],
        #   '54:P890117-01010':['0', '1.292764331', '-28.62477982', '-28.6249676978', '-35.2432771', '-35.2432771']
        # }
        self._feature_Matrix = {}

    def __LoadQrelFileInDictionary__(self):

        with open(self._qrelFilePath , 'r+') as handle:
            for line in handle:
                lineItemsInList = line.strip('\n').split(" ")
                qId = lineItemsInList[0]
                constantText = lineItemsInList[1]
                docId = lineItemsInList[2]
                relavance = lineItemsInList[3]

                if not self._qrelDict.has_key(qId):
                    self._qrelDict[qId] = {}

                self._qrelDict[qId][docId] =  relavance
                key = qId + ":" + docId
                self._feature_Matrix[key] = [relavance]

    def __LoadTrecResults__(self):
        s = Set()
        for root, dirs, files in os.walk(Resource.HW1_OutputFor1000Docs):
            for file in files:
                filePath = os.path.join(root, file)
                modelName =  file.strip(".txt")
                modelNumber = self._enumObj.fromstring(modelName)
                self._trec_Result[modelNumber] = {}
                with open(filePath , 'r+') as handle:
                    for line in handle:
                        lineItemsInList = line.strip('\n').split(" ")
                        qId = lineItemsInList[0]
                        s.add(qId)
                        constantText = lineItemsInList[1]
                        docId = lineItemsInList[2]
                        rank = lineItemsInList[3]
                        docScore = lineItemsInList[4]

                        if not self._trec_Result[modelNumber].has_key(qId):
                            self._trec_Result[modelNumber][qId] = {}

                        if not self._qrelDict.has_key(qId):
                            print "query id -> ", qId, "dos not exist in qrel file. So dropped."
                            continue

                        if self._qrelDict[qId].has_key(docId):
                            self._trec_Result[modelNumber][qId][docId] =  docScore
                            key = qId + ":" +docId
                            self._feature_Matrix[key].append(docScore)
                            # if key == '91:AP890503-0007':
                            #       print self._feature_Matrix['91:AP890503-0007']

        # print "# of unique queried processed by Models in assignment I", len(s)

        self.__LoadMissingDocIdWithMinValue__()
        self.__Store__(self._feature_Matrix, Resource.FeatureFilePath)
        print "Feature Matrix saved in location -> ", Resource.FeatureFilePath

    def __LoadMissingDocIdWithMinValue__(self):
        for qId, docIdToRelDict in self._qrelDict.iteritems():

            for modelName, qIdToDocIdToScoreDict in self._trec_Result.iteritems():
                if self._trec_Result[modelName].has_key(qId):
                    # print modelName,qId, "->", len(self._trecResult[modelName][qId]), len(self._qrelDict[qId])
                    minValue = self.__GetMinimumScore__(self._trec_Result[modelName][qId])

                    for docId, relevalnce in docIdToRelDict.iteritems():
                        # qrel docId not present in trec-result file.
                        if not self._trec_Result[modelName][qId].has_key(docId):
                            self._trec_Result[modelName][qId][docId] = minValue
                            key = qId + ":" + docId
                            self._feature_Matrix[key].append(minValue)

                    # print  modelName,qId, "->", len(self._trec_Result[modelName][qId]), len(self._qrelDict[qId])

    def __GetMinimumScore__(self, docIdToScoreForAQuery):
        minValue = sys.float_info.max

        for docId, score in docIdToScoreForAQuery.iteritems():
            score = float(score)
            if score < minValue:
                minValue = score
        return minValue

    def __Store__(self, data, fname):
        f = open(fname, "w")
        pickle.dump(data, f)
        print self._feature_Matrix['58:AP890801-0053']

############################################################

obj = DataProcessor()
obj.__LoadQrelFileInDictionary__()
obj.__LoadTrecResults__()

