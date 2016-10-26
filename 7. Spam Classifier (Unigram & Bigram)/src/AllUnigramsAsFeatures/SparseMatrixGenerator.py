#######################################################################################
# 1. Manually create list of ngrams related to spam (e.g. 'win', 'free', 'porn' etc.
# 2. Create two Feature Matrices - 1. for Training feature, 2. Testing Feature.
#   (No need of 'Sparse Matrix' because # features are less ~ 20)
# 3. Use 'Spam/Ham' as Label (fetch from indexed documents)
# 4. Use Elastic search to query for features i.e. score for ngrams are feature values.
# After all steps copy training sparse matrix and testing-sparse-matrix files train_matrix and test_matrix)
#  to linux m/c to run# train LibLinear model and predict labels for train-sparse-data.(
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

######################################################################################
class SparseMatrixGenerator:
    def __init__(self, trainingMatrixFilePath, testingMatrixFilePath, indexName, documentType):
        # {'ngram1':1, 'ngram2':2}
        self._feature_terms = {}
        self._index_name = indexName
        self._document_type = documentType

        self._training_matrix_file_Path = trainingMatrixFilePath
        self._testing_matrix_file_Path = testingMatrixFilePath

        # [('inmail.2', 0, 0), ('inmail.6', 1, 1), ('inmail.12', 2, 1), ('inmail.16', 3, 1), ('inmail.21', 4, 0)]
        self._training_emailIdCommaSnoCommaLabel = []
        # [('inmail.2', 0, 0), ('inmail.6', 1, 1), ('inmail.12', 2, 1), ('inmail.16', 3, 1), ('inmail.21', 4, 0)]
        self._testing_emailIdCommaSnoCommaLabel = []

    ############ All unigrams in Indexed email corpus as FEATURES ################
    def __GenerateAllFeatures__(self, indexName, docTypeName):
        featureNameToId = {}
        features = self.__GetFeaturesAsFeaturesFromEmailCorpus__(indexName, docTypeName)
        buckets = features["aggregations"]["features"]["buckets"]
        print "Total # of unigrams fetched from Elastic Search as features %s" % len(buckets)
        counter = 0
        for bucket in buckets:
            counter += 1
            key = bucket['key']
            featureNameToId[key] = counter
        self.__SaveFeaturesToTextFile__(featureNameToId, Resource.FeatureNameToIdMapFilePath)

    def __GetFeaturesAsFeaturesFromEmailCorpus__(self,  indexName, docTypeName):
        elasticSearchMgrObject = ElasticSearchManager(indexName, docTypeName)
        print "Featching all unigrams from Elastic Search ...."
        result =  elasticSearchMgrObject.__GetAllUnigramsAsFeatures__()
        # "aggregations": {
        #     "features": {
        #         "doc_count_error_upper_bound": 0,
        #         "sum_other_doc_count": 0,
        #         "buckets": [
        #             {
        #                 "key": "http",
        #                 "doc_count": 4274
        #             },
        #             {
        #                 "key": "s",
        #                 "doc_count": 3958
        #             }
        #         ]
        #     }
        # }
        return result

    def __SaveFeaturesToTextFile__(self, features, filePath):
        with open(filePath, 'w') as handle:
            for key, value in features.iteritems():
                handle.write(u"%s\t%d\n" % (key, value))
        print "Unigrams name to Index mapping {indianapoli	10498, game 99} saved in location %s\n" % filePath

    def __LoadFeatures__(self, filePath):
        print "Loading Feature Name to Feature Id mapping.."
        if not os.path.exists(filePath):
            self.__GenerateAllFeatures__( self._index_name, self._document_type)

        with open(filePath, 'r') as handle:
            for line in handle:
                key, index = line.split()
                self._feature_terms[key] = int(index)
        # print type(self._featureName_to_Id_map["indianapoli"])

    ############ Generate SPARSE FEATURE MATRIX for all extracted FEATURES #########
    def __GenerateFeatureMatrixFromEmailCorpus__(self,  indexName, docTypeName):
        print "Generating SPARSE FEATURE MATRIX ..."

        UniTrainFileHandle = open(self._training_matrix_file_Path, 'w')
        UniTestFileHandle = open(self._testing_matrix_file_Path,'w')
        trainCounter = -1
        testCounter = -1
        for x in range(1, 75419):
            emailDocId = 'inmail.' + str(x)
            resultForTermVectors = self.__GetTermVectorForDoc__(emailDocId, indexName, docTypeName)

            # {u'text': {u'terms': {u'ciali': {u'term_freq': 1}, u'old': {u'term_freq': 1},
            termVectors =  resultForTermVectors['term_vectors']

            splitTerms = termVectors['split']['terms']
            labelTerms = termVectors['label']['terms']

            splitTrainOrTest = self.__GetSplitTypeAsTrainOrTest__(splitTerms)
            label = self.__GetLabelValue__(labelTerms)

            # print emailDocId, termVectors
            print emailDocId
            if not termVectors.has_key('text'):
                continue

            if not termVectors['text'].has_key('terms'):
                continue

            termToTermFreqMap = {}
            for featureTermName, termFreqWordToValue in termVectors['text']['terms'].iteritems():
                if self.RepresentsInt(featureTermName):
                    continue
                featureId = self.__GetFeatureIdForFeatureName( featureTermName)
                termFrequency = termFreqWordToValue['term_freq']
                termToTermFreqMap[featureId] = float(termFrequency)

            if len(termToTermFreqMap.values()) == 0:
                # print termToTermFreqMap
                continue

            # [(64, 1.0), (91, 1.0), (103, 1.0)]
            sortedFeatureIdCommaScore = sorted(termToTermFreqMap.items(), key=lambda x:x[0])

            # Generate Train Feature Matrix
            if splitTrainOrTest == 'train':
                trainCounter +=1
                UniTrainFileHandle.write(str(label))
                for featureId, termFreq in sortedFeatureIdCommaScore:
                    # featureIds.add(featureId)
                    UniTrainFileHandle.write(" %d:%d" % (featureId, termFreq))
                UniTrainFileHandle.write('\n')
                self._training_emailIdCommaSnoCommaLabel.append((emailDocId,trainCounter, label))

            # Generate Test Feature Matrix
            if splitTrainOrTest == 'test':
                testCounter += 1
                UniTestFileHandle.write(str(label).strip())
                for featureId, termFreq in sortedFeatureIdCommaScore:
                    UniTestFileHandle.write(" %d:%d" % (featureId, termFreq))
                UniTestFileHandle.write('\n')
                self._testing_emailIdCommaSnoCommaLabel.append((emailDocId,testCounter, label))

            if splitTrainOrTest == 'unknown':
                print emailDocId , "for unknown"
                self._train_FeatureMatrix, self._training_matrix_file_Path
            if label == -1:
                print emailDocId, "for label as -1"

        print "\n"
        print "File saved. Sparse Matrix for Train data -> ", self._training_matrix_file_Path
        print "File saved. Sparse Matrix for TEST data  -> %s \n" % self._testing_matrix_file_Path

        # [('inmail.2', 0, 0), ('inmail.6', 1, 1), ('inmail.12', 2, 1), ('inmail.16', 3, 1), ('inmail.21', 4, 0)]
        self.__Dump__(self._training_emailIdCommaSnoCommaLabel, Resource.UniTrainEmailIdToSnoCommaLabelFilePath)
        #    [('inmail.2', 0, 0), ('inmail.6', 1, 1), ('inmail.12', 2, 1), ('inmail.16', 3, 1), ('inmail.21', 4, 0)]
        self.__Dump__(self._testing_emailIdCommaSnoCommaLabel, Resource.UniTestEmailIdToSnoCommaLabelFilePath)


    def __GetTermVectorForDoc__(self, emailDocId, indexName, docTypeName):
        elasticSearchMgrObject = ElasticSearchManager(indexName, docTypeName)
        result =  elasticSearchMgrObject.__GetTermVectorForDoc__(emailDocId)
        # u'term_vectors': {
        # "text": {
        #      "terms": {
        #         "confirm": {
        #            "term_freq": 1
        #         },
        #         "30": {
        #            "term_freq": 1
        #         },
        #         "approv": {
        #            "term_freq": 1
        #         }
        #      }
        #   },
        # u'split': {u'terms': {u'train': {u'term_freq': 1}}}, u'label': {u'terms': {u'spam': {u'term_freq': 1}}},
        # }
        return result

    ########## Helper functions ###################################################
    def __GetLabelValue__(self, termLabelInTermVectors):
        isSpam = -1
        if termLabelInTermVectors.has_key('spam'):
            isSpam = 1
        if termLabelInTermVectors.has_key('ham'):
            isSpam = 0

        return  isSpam

    def __GetSplitTypeAsTrainOrTest__(self,splitTerms):
        splitType = 'unknown'
        if splitTerms.has_key('train'):
            splitType = 'train'
        if splitTerms.has_key('test'):
            splitType = 'test'

        return splitType

    def __GetFeatureIdForFeatureName(self, featureName):
        id = -1
        featureName = featureName.strip('\t')
        if self._feature_terms.has_key(featureName):
            id = self._feature_terms[featureName]
        return int(id)

    def RepresentsInt(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    def __Dump__(self, data, filePath):
        with open(filePath, 'w') as handle:
            pickle.dump(data,handle)
            print "Files saved. Location -> %s" % filePath
#####################################################################################
# Uncomment all 3 lines to run this script
# featureMatrixGeneratorObj = SparseMatrixGenerator(Resource.UniTrainMatrixFilePath, Resource.UniTestMatrixFilePath,
#                                                   Resource.INDEX_NAME, Resource.TYPE_NAME)
# featureMatrixGeneratorObj.__LoadFeatures__(Resource.FeatureNameToIdMapFilePath)
# featureMatrixGeneratorObj.__GenerateFeatureMatrixFromEmailCorpus__(Resource.INDEX_NAME, Resource.TYPE_NAME)

