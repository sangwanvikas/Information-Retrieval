from sets import Set
####################################################################################################

InputDirCompletePath = "C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW6/input/"
qrelFilePath = InputDirCompletePath + "qrels.adhoc.51-100.AP89.txt"

####################################################################################################
HW1_OutputFor1000Docs = "C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW6/HW1_OutputFor1000Docs"
HW1_OutputFor1000DocsIDF = "C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW6/HW1_OutputFor1000Docs/IDF/"
Idf54= HW1_OutputFor1000DocsIDF + "54.txt"

# ##################################################################################################
HW6OutputDir = "C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW6/output/"
FeatureFilePath = HW6OutputDir + "Feature_Matrix.txt"
TrainedTrecResultFilePath = HW6OutputDir + "Trained_Trec_Result.txt"
SortedTrainedTrecResultFilePathLR = HW6OutputDir + "LR_Sorted_Trained_Trec_Result.txt"
SortedTrainedTrecResultFilePathDT = HW6OutputDir + "DT_Sorted_Trained_Trec_Result.txt"

TestingTrecResultFilePath = HW6OutputDir + "Testing_Trec_Result.txt"
SortedTestingTrecResultFilePathLR = HW6OutputDir + "LR_Sorted_Testing_Trec_Result.txt"
SortedTestingTrecResultFilePathDT = HW6OutputDir + "DT_Sorted_Testing_Trec_Result.txt"

# ##################################################################################################
allQueryIds =['60', '61', '62', '89', '64', '68', '80', '93', '85', '87', '77', '98', '71', '91', '100', '95', '94', '97', '99', '59', '58', '54', '57', '56', '63']
# Decision Tree - For trained Avg Precision .3662, for testing .4937
# QIdsForTestingDT = ['63','54','57','56','58']
QIdsForTestingDT =['94','95','97','99','100']
QIdsForTrainingDT = list(Set(allQueryIds) - Set(QIdsForTestingDT))

# Decision Tree - For trained Avg Precision .8256, for testing .4130
QIdsForTestingLR =['56', '57', '64', '71', '99']

# # Linear Regression - For training Avg Precision : .3512, for testing .4615
# QIdsForTestingLR = ['94','95','97','99','100']
QIdsForTrainingLR = list(Set(allQueryIds) - Set(QIdsForTestingLR))
# print QIdsForTraining