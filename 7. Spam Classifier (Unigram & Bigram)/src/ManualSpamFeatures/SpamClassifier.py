#######################################################################################
# 1. Load feature matrices for training and testing data.
# 2. Load list of labels for training and testing data.
# 3. Using 'Train' queries static matrix, train a learner to computer a model relating
#    labels to the features on TRAIN set.
# 4. Test the trained model on training set of data.
# 5. Test the trained model on testing set of data.
#######################################################################################

import os, sys, pickle
from numpy import array
from sklearn import tree
from sklearn import feature_selection
from sklearn.metrics import accuracy_score

from sklearn.linear_model import LogisticRegression

currDirPath = os.path.abspath(os.curdir)
os.chdir("..")
srcDirPath =  os.path.abspath(os.curdir)

sys.path.append(srcDirPath +"/Resource")
sys.path.append(srcDirPath+"/ElasticSearchManager")

import Resource
######################################################################################
class SpamClassifier:
    def __init__(self, trainingMatrixFilePath, trainLabelsFilePath, testingMatrixFilePath, testLabelsFilePath):
        print "Loading spam words form a file.."
        self._feature_terms = self.__GetSpamWordsList__(Resource.ManualSpamWordsFilePath)
        print  self._feature_terms
        print "Total number of spam words loaded ", len(self._feature_terms)
        #  -----------------------------------------------------------

        print "Loading emailId to real label mapping for TRAIN.."
        self._train_emailId_to_label = self.__Load__(Resource.TrainEmailIdToLabelFilePath)

        print "Loading emailId to real label mapping for TEST..\n"
        self._test_emailId_to_label = self.__Load__(Resource.TestEmailIdToLabelFilePath)
        #  -----------------------------------------------------------

        self._featureName_To_CoeffScore = {}
        # {
        #     'inmail.1':[0, 0, 0, 0, 1.076837]},
        #     'inmail.10':[0.34139505, 0, 0.38573068, 0.53888994, 0]
        # }
        self._train_FeatureMatrix = {}
        # [0, 0, 1, 0] where 1 is SPAM and 0 is HAM
        self._train_labels = []
        print "Loading training features matrix..."
        self._train_FeatureMatrix = self.__Load__(trainingMatrixFilePath)
        print "Loading labels for training data...\n"
        self._train_labels = self.__Load__(trainLabelsFilePath)

        self._test_FeatureMatrix = {}
        self._test_labels = {}
        print "Loading testing features matrix..."
        self._test_FeatureMatrix = self.__Load__(testingMatrixFilePath)
        print "Loading labels for testing data...\n"
        self._test_labels = self.__Load__(testLabelsFilePath)

        self._emailFileNameToSpamOrHamMap = self.__LoadFileNameToSpamOrHamMapping__(Resource.SpamIdentifierMapFilePath)

    def __GetSpamWordsList__(self, filePath):
        spamWords = []
        with open(filePath, 'r') as handle:
            for line in handle:
                spamWords.append(line.strip('\n'))
        return spamWords


    def __GetTrainingSampleAndTrainingLabels__(self, trainingMatrix):
        return trainingMatrix.values(), trainingMatrix.keys()

    def __TrainAndPredict__(self):
        #  Train
        print "Training feature matrix for Split-Train..\n"
        trainingSampleList, emailIdsForTrainingList = self.__GetTrainingSampleAndTrainingLabels__(self._train_FeatureMatrix)
        decision_model = self.__Train__(array(trainingSampleList),array(self._train_labels))

        # ----------------------------------------------------------------------------------------------------
        # Predict for Training feature matrix
        # print "Perform prediction for Training data.."
        # self.__CalculateAndStorePredictiont__(Resource.SortedTrainedTrecResultFilePath,
        #                                       emailIdsForTrainingList,
        #                                       decision_model,
        #                                       trainingSampleList,
        #                                       self._train_labels,
        #                                       self._train_emailId_to_label)
        # print "Total # emails in Trained Sample -> ", len(emailIdsForTrainingList)
        # print "Result for Training Queires saved in -> ", Resource.SortedTrainedTrecResultFilePath
        # print "\n"

        # ----------------------------------------------------------------------------------------------------
        # Predict for Testing feature matrix
        print "Perform prediction for testing data.."
        testingSamples, emailIdsForTesting  = self.__GetTrainingSampleAndTrainingLabels__(self._test_FeatureMatrix)
        self.__CalculateAndStorePredictiont__(Resource.SortedTestingTrecResultFilePath,
                                              emailIdsForTesting,
                                              decision_model,
                                              testingSamples,
                                              self._test_labels,
                                              self._test_emailId_to_label)
        print "Total # emails in testing Sample -> ", len(emailIdsForTesting)
        print "Result for Training Queires saved in -> ", Resource.SortedTestingTrecResultFilePath
        print "\n"

    def __Train__(self, x, y):
        decision_model = LogisticRegression()
        decision_model.fit(x, y)

        transformed_value = feature_selection.f_classif(x,y)

        spamFeatureCoeffs = transformed_value[0]
        for x in range(len(spamFeatureCoeffs)):
            self._featureName_To_CoeffScore[self._feature_terms[x]] = spamFeatureCoeffs[x]

        return decision_model

    def predict(self, lr_model, x):
        prediction = lr_model.predict(x)
        return prediction

    def  GetProbabilities(self, lr_model,x):
         return lr_model.predict_proba(x)

    def __CalculateAndStorePredictiont__(self, filePath, emailIds, decision_model, samples, testOrTrainLabels, emailIdToRealLabel):
        predicted_result = self.predict(decision_model, samples)
        probScores = self.GetProbabilities(decision_model, samples)
        # -------------------------------------------------------
        # accuracyScore = accuracy_score(decision_model.predict(samples), testOrTrainLabels)
        # print "REAL Accuracy SCORE ", accuracyScore

        emailIdToProbabilityScore = {}
        emailIdToPredictedLabel = {}
        for x in range(len(probScores)):
            emailIdToProbabilityScore[emailIds[x]] = float(probScores[x][1])
            emailIdToPredictedLabel[emailIds[x]] = predicted_result[x]

        emailIdCommaScoreList = sorted(emailIdToProbabilityScore.items(), key=lambda x: x[1], reverse=True)

        counter = 0
        with open(Resource.Top50ManualSpamEmails, 'w') as handle:
            i = -1
            for emailId, score in emailIdCommaScoreList:
                i += 1
                aline = str(i) + " " + str(emailId) + " " + str(score) + " " + str(emailIdToRealLabel[emailId]) + " "  \
                        +str(emailIdToPredictedLabel[emailId]) + "\n"

                if str(emailIdToRealLabel[emailId]) == str(emailIdToPredictedLabel[emailId]):
                    counter += 1
                else:
                    print emailId

                handle.write(aline)
                if i == 49:
                    break
        print "Percentage Calculated ", (counter*100)/float(50)
        # ---------------------------------------------------------------------------------

        self.__GetSortAndSortedQidByDocScore__(filePath, emailIds, predicted_result)

    def __GetSortAndSortedQidByDocScore__(self, filePath, emailIds, scores):
        # {
        #     'inmail.1': 0,
        #     'inmail.6754': 1,
        #     'inmail.1000': 1
        # }
        emailIdToResultingLabelDict = {}

        for i in range(0, len(emailIds)):
            emailId = emailIds[i]
            score = int(scores[i])
            emailIdToResultingLabelDict[emailId] = score

        count=0
        with open(filePath, "w") as handle:
            data = sorted(emailIdToResultingLabelDict.items(), key=lambda x: x[1], reverse=True)
            for emailId, resultLabel in data:
                count += 1
                aLine = str(count) + " " + emailId + " " +  str(resultLabel) + " " + "EXP" + "\n"
                handle.write(aLine)

    def __Load__(self, filePath):
        with open(filePath, 'r') as handle:
            return pickle.load(handle)

    def __LoadFileNameToSpamOrHamMapping__(self, spamIdentifierMapFilePath):
        fileNameToSpamOrHamMapping = {}
        with open(spamIdentifierMapFilePath, 'r') as handle:
            for aLine in handle:
                # aLine -> spam ../data/inmail.1
                SpamOrHam, relativeFilePath = aLine.split(' ')
                fileName = (relativeFilePath.split('/')[-1]).strip('\n')
                fileNameToSpamOrHamMapping[fileName] = SpamOrHam

        return fileNameToSpamOrHamMapping

    def __SortAndDumpSpamWords__(self):
        sortedPredictedMap = sorted(self._featureName_To_CoeffScore.items(), key=lambda x: x[1], reverse=True)
        with open(Resource.Top50ManualSpamWords, 'w') as handle:
            i = -1
            for spamWord, score in sortedPredictedMap:
                i += 1
                aLine = str(i) + " " + spamWord + " " + str(score) + " " + "\n"
                handle.write(aLine)
        print sortedPredictedMap

###################################################################################################
spamClassfierObj = SpamClassifier(Resource.TrainMatrixFilePath,  Resource.TrainLabelsFilePath,
                                        Resource.TestMatrixFilePath, Resource.TestLabelsFilePath)

spamClassfierObj.__TrainAndPredict__()

spamClassfierObj.__SortAndDumpSpamWords__()