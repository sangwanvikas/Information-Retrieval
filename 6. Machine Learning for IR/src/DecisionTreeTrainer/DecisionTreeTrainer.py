####################################################################################################
# 1. For Training queries, from Feature_Matrix : Load sample list, QueryId & DocId mapping list, and Label list
# 2. Create numpy array for array(sample), array(label)
# 3. Train 'tree' Decision Tree Model from sklearn library.
#     lr_model.fit(numpy(sample), numpy(label))
# 4. Predict scores for Trec-Result on TrainingSamples.
#     Predict self.predict(lr_model, TrainingSamples)
# 5. Save scores for training 'queryIdDocIdMapping'.
# 6. Predict scores for Trec-Result on TestingSamples.
#     Predict self.predict(lr_model, TestingSamples)
# 7. Save scores for testing 'queryIdDocIdMapping'.
###################################################################################################

import sys
import pickle
from numpy import array
from sklearn import tree
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import AdaBoostRegressor

sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW6/src/Resource')
sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW6/src/Enum')

import Resource

###################################################################################################
class DecisionTreeTrainer:

    def __init__(self, featureFilePath):
        # {
        #  '80AP891025-0074' : [1, 2.62713485343, -12.0703124404, -20.0999655567, 12.7969331221, 1.52380952381],
        #  '94AP890629-0048' : ['0', '-15.0543378719', 1.07393814466, -11.7552998316, 5.58019774315, 0.8],
        #  '51AP890201-0178' : ['0']
        # }
        self._feature_Matrix = {}
        self._feature_Matrix = self.__ReadData__(featureFilePath)
        # iris =  datasets.load_iris()
        # print iris.data
        # print iris.target
        self._qIdsForTraining = Resource.QIdsForTrainingDT
        self._qIdsForTesting = Resource.QIdsForTestingDT

    def __ReadData__(self, fielPath):
        f = open(fielPath, "r")
        self._feature_Matrix = pickle.load(f)

        return self._feature_Matrix

    def __FeedMLAlgo__(self):
        qIdDocIds = []
        trainedSamples = []
        label = []

        i = 0
        for qIdDocId, features in self._feature_Matrix.iteritems():
            i += 1

            qId, docId = qIdDocId.split(":")

            # Proceed only if query Ids belong to 20 training queries.
            if not qId in self._qIdsForTraining:
                continue

            if len(features) < 6:
                features += ["0"] * (6-len(features))

            if len(features) != 6:
                # print i,qIdDocId, map(lambda feature: float(feature), features[1:])
                continue

            #  Load label[], qIdDocIds[] and trainedSamples[] from Training data.
            label.append(int(features[0]))
            qIdDocIds.append(qIdDocId)
            trainedSamples.append(map(lambda feature: float(feature), features[1:]))
        # -----------------------------------------------------------------------------------------------------------
        # Train Machine Leaning Algorithm
        decision_tree_model = self.__Train__(array(trainedSamples), array(label))

        # -----------------------------------------------------------------------------------------------------------
        # Predict and Save Trec-Result file for TrainedData
        self.__CalculateAndStorePredictedTrecResult__(Resource.SortedTrainedTrecResultFilePathDT, self._qIdsForTraining,
                                          qIdDocIds, decision_tree_model, trainedSamples)

        print "Queries for Training Data -> ", self._qIdsForTraining
        print "Treac-Result for Training Queires saved in -> ", Resource.SortedTrainedTrecResultFilePathDT
        print "\n"

        # -----------------------------------------------------------------------------------------------------------
        # Predict and Save Trec-Result file for TrainedData
        testingSamples, testingQIdDocIds = self.__GetSamplesForTrainingQueryId__(self._feature_Matrix)
        self.__CalculateAndStorePredictedTrecResult__(Resource.SortedTestingTrecResultFilePathDT, self._qIdsForTesting ,
                                                      testingQIdDocIds, decision_tree_model, testingSamples)
        print "Queries for Testing Data -> ", self._qIdsForTesting
        print "Treac-Result for Testing Queires saved in -> ", Resource.SortedTestingTrecResultFilePathDT

    def __Train__(self,x, y):
        # Linear Regression model
        # decision_tree_model = tree.DecisionTreeClassifier()
        decision_tree_model = DecisionTreeRegressor(max_depth=4)
        decision_tree_model.fit(x, y)
        # print "Model params:", decision_tree_model.get_params()
        return decision_tree_model

    def __CalculateAndStorePredictedTrecResult__(self, filePath, TrainingOrTestingQueryIds, qIdDocIds,lr_model, samples):
        scores = self.predict(lr_model, samples)
        self.__GetSortedQidByDocScore__(filePath, TrainingOrTestingQueryIds, qIdDocIds, scores)

    def predict(self, decision_tree_model, x):
        return decision_tree_model.predict(x)

    def __GetSamplesForTrainingQueryId__(self, feature_Matrix):
        testingQIdDocIds = []
        testimgSamples = []
        i = 0
        for qIdDocId, features in feature_Matrix.iteritems():
            i += 1

            qId, docId = qIdDocId.split(":")

            #  Proceed only if query Ids belong to 20 Testing queries.
            if not qId in self._qIdsForTesting :
                continue

            if len(features) < 6:
                features += ["0"] * (6-len(features))

            if len(features) != 6:
                # print i,qIdDocId, map(lambda feature: float(feature), features[1:])
                continue

            # Ignore Label from featureMatrix
            testimgSamples.append(map(lambda feature: float(feature), features[1:]))
            testingQIdDocIds.append(qIdDocId)
        return testimgSamples, testingQIdDocIds

    def __GetSortedQidByDocScore__(self, filePath, TrainingOrTestingQueryIds, qIdDocIds, scores):
        # {
        #     '58': {'AP890801-0053':3.5,'AP890801-0101' : 5.5,....},
        #     '60': {'AP890801-0053':3.5,'AP890801-0101' : 5.5,....}
        # }
        qIdToDocIdToScoreDict = {}
        for i in range(0, len(qIdDocIds)):
            qId, docid = qIdDocIds[i].split(":")

            if not qId in TrainingOrTestingQueryIds:
                continue

            score = float(scores[i])

            if not qIdToDocIdToScoreDict.has_key(qId):
                qIdToDocIdToScoreDict[qId] = {}

            if not qIdToDocIdToScoreDict[qId].has_key(docid):
                qIdToDocIdToScoreDict[qId][docid] = -1

            qIdToDocIdToScoreDict[qId][docid] = score
        c=0
        print filePath
        with open(filePath, "w") as handle:
            for qId, docIdToScore in qIdToDocIdToScoreDict.iteritems():

                data = sorted(docIdToScore.items(), key=lambda x: x[1], reverse=True)

                for key, value in data:
                    c += 1
                    aLine = qId + " " + "Q0" + " " + key + " " + str(c) + " " + str(value) + " " + "EXP" + "\n"
                    handle.write(aLine)
# ###########################################################
trainerObj = DecisionTreeTrainer(Resource.FeatureFilePath)
trainerObj.__FeedMLAlgo__()
