#######################################################################################
# 1. Manually create list of ngrams related to spam (e.g. 'win', 'free', 'porn' etc.
# 2. Create two Feature Matrices - 1. for Training feature, 2. Testing Feature.
#   (No need of 'Sparse Matrix' because # features are less ~ 20)
# 3. Use 'Spam/Ham' as Label (fetch from indexed documents)
# 4. Use Elastic search to query for features i.e. score for ngrams are feature values.
#######################################################################################

import os, sys
print os.curdir

currDirPath = os.path.abspath(os.curdir)
os.chdir("..")
srcDirPath =  os.path.abspath(os.curdir)

sys.path.append(srcDirPath +"/Resource")
sys.path.append(srcDirPath+"/ElasticSearchManager")

import Resource
import pickle
from ElasticSearchManager import ElasticSearchManager
from stemming.porter2 import stem
from sets import Set

######################################################################################
class FeatureMatrixGenerator:
    def __init__(self, trainingMatrixFilePath, trainLabelsFilePath, testingMatrixFilePath, testLabelsFilePath):
        print "ManualSpamClassifer"
        # Manually created ngrams list
        # ["job", "lose weight", "sex", "alert", "virus", "bonus", "discount", "subscribe"]
        self._feature_terms = self.__GetSpamWordsList__(Resource.ManualSpamWordsFilePath)
        self._stopList = self.__GetSpamWordsList__(Resource.StopWordsFilePath)
        print self._stopList
        newFeatures = []
        for feature in self._feature_terms:
            if not feature in self._stopList:
                newFeatures.append(feature)

        self._feature_terms = list(Set(newFeatures))
        print "total # number of featues loaded " , len(self._feature_terms)
        print self._feature_terms
        # {
        #     'inmail.155' : [0, 0, 0, 0, 1.076837] },
        #     'inmail.100' : [0.34139505, 0, 0.38573068, 0.53888994, 0]
        # }
        self._train_FeatureMatrix = {}
        # [0, 0, 1, 0] where 1 is SPAM and 0 is HAM
        self._train_labels = []

        self._test_FeatureMatrix = {}
        self._test_labels = []

        self._training_matrix_file_Path = trainingMatrixFilePath
        self._train_labels_file_Path = trainLabelsFilePath
        self._testing_matrix_file_Path = testingMatrixFilePath
        self._test_labels_file_Path = testLabelsFilePath

    def __GetSpamWordsList__(self, filePath):
        spamWords = []
        with open(filePath, 'r') as handle:
            for line in handle:
                line = line.strip('\n')
                line = line.strip()
                spamWords.append(line.lower())
        return spamWords

    def __GenerateFeatureMatrixFromEmailCorpus__(self,  indexName, docTypeName):
        print "Generating Feature matrix..."
        testingEmailIdToRelaLabel = {}
        trainingEmailIdToRelaLabel = {}
        for x in range(len(self._feature_terms)):
            feature_term = stem(self._feature_terms[x])
            print x, "Updating feature matrix for feature term : %s"  %feature_term
            tfDetailsForSpamTerm = []
            # [
            #     {'docId' : "inmail.12", 'label':'spam', 'split':'train', 'score':0.0345},
            #     {'docId' : "inmail.2222", 'label':'ham', 'split':'test', 'score':0.51}
            # ]
            tfDetailsForSpamTerm = self.__GetTermDetailsFromElasticSearch__(feature_term, indexName, docTypeName)
            if len(tfDetailsForSpamTerm) == 0:
                print feature_term

            # ---------------------------------------------------------------------------------
            for tfDetailDict in tfDetailsForSpamTerm:
                docId = tfDetailDict['docId']
                label = tfDetailDict['label']
                split = tfDetailDict['split']
                score = float(tfDetailDict['score'])

                isSpam = 0
                if label == 'spam':
                    isSpam = 1
                # ---------------------------------------------------------------------------------
                # Generate Training Feature Matrix
                if split == 'train':
                    if not self._train_FeatureMatrix.has_key(docId):
                        self._train_FeatureMatrix[docId] = []
                        for i in range(len(self._feature_terms)):
                             self._train_FeatureMatrix[docId].append(0)
                        self._train_labels.append(isSpam)

                    self._train_FeatureMatrix[docId][x] = score
                    if not trainingEmailIdToRelaLabel.has_key(docId):
                        trainingEmailIdToRelaLabel[docId] = isSpam
                # ---------------------------------------------------------------------------------
                # Generate Testing Feature Matrix
                if split == 'test':
                    if not self._test_FeatureMatrix.has_key(docId):
                        self._test_FeatureMatrix[docId] = []
                        for i in range(len(self._feature_terms)):
                            self._test_FeatureMatrix[docId].append(0)
                        self._test_labels.append(isSpam)

                    self._test_FeatureMatrix[docId][x] = score
                    if not testingEmailIdToRelaLabel.has_key(docId):
                        testingEmailIdToRelaLabel[docId] = isSpam

        # ---------------------------------------------------------------------------------
        print ""
        print "Dumping Training matrix and real label list for training data..."
        self.__Dump__(self._train_FeatureMatrix, self._training_matrix_file_Path)
        self.__Dump__(self._train_labels, self._train_labels_file_Path)

        print "Dumping Testing matrix and real label list for Testing data..."
        self.__Dump__(self._test_FeatureMatrix, Resource.TestMatrixFilePath)
        self.__Dump__(self._test_labels,self._test_labels_file_Path)

        print "Dumping EmailId to RealLabel mapping for training and testing data..."
        self.__Dump__(testingEmailIdToRelaLabel, Resource.TestEmailIdToLabelFilePath)
        self.__Dump__(trainingEmailIdToRelaLabel, Resource.TrainEmailIdToLabelFilePath)

    def __GetTermDetailsFromElasticSearch__(self, termArg, indexName, docTypeName):
        elasticSearchMgrObject = ElasticSearchManager(indexName, docTypeName)
        result =  elasticSearchMgrObject.__GetTermDetails__(termArg)
        # [
        #     {'docId':"inmail.12",'label':'spam', 'split':'train', 'score':0.0345},
        #     {'docId':"inmail.2222",'label':'ham', 'split':'test', 'score':0.51}
        # ]
        return result

    def __Dump__(self, data, filePath):
        with open(filePath, 'w') as handle:
            pickle.dump(data,handle)
            print "Files saved. Location -> %s" % filePath


#####################################################################################
featureMatrixGeneratorObj = FeatureMatrixGenerator(Resource.TrainMatrixFilePath,  Resource.TrainLabelsFilePath,
                                                         Resource.TestMatrixFilePath, Resource.TestLabelsFilePath)
featureMatrixGeneratorObj.__GenerateFeatureMatrixFromEmailCorpus__(Resource.INDEX_NAME, Resource.TYPE_NAME)