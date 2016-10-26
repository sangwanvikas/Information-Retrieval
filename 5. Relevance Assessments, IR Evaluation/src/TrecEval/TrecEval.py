#########################################################################
# 1. First, sort docIDS per queryID by score.

# 2. Then for each query compute
#   2.1 R-precision - Value of recall and precision at the rank where they are equal,
#   2.2 Average Precision - Mean of the precision@k scores for every rank containing a relevant document,
#   2.3 nDCG,
#   2.4 precision@k and recall@k,
#   2.5 and F1@k - F combines both recall and precision, so systems that favor are penalized for whichever is low.
#   2.6 F1 - harmonic mean of precision and recall
#  (k=5,10, 20, 50, 100).

# 3. Run your treceval on HW1 runs with the qrel provided to confirm that it gives the same values as the provided treceval.
# 4. Create a precision-recall plot.
#########################################################################

import sys, math
import os.path
import csv

sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW5/src/Resource')
sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW5/src/Utility')
import Resource, Utility
from collections import Counter


class TrecEval:
    NoOfDocs = 1000
    def __init__(self, inputArguments):
        # print "TrecEval c'tor"
        self.utility = Utility.Utility()

        # 1. Process Arguments, Verify and load variables
        self._inputArguments = inputArguments
        self._isMinusQ = False
        self._qrelCompleteFileName = ""
        self._resultCompleteFileName = ""

        self.__ValidateInputArguments__()

        # print self._isMinusQ
        # print self._qrelCompleteFileName
        # print self._resultCompleteFileName

        # 2. Load qrel and result dictionaries
        self._num_rel = {}
        # {{"150901": {"docId1": 0 / 1, "docId1": 0 / 1}, {"150901": {"docId1": 0 / 1, "docId1": 0 / 1}}}
        self._qrelDictTopicToDocRel = {}
        # {{"150901": {"docId1": 0 / 1 / 2, "docId1": 0 / 1 / 2}, {"150901": {"docId1": 0 / 1 / 2, "docId1": 0 / 1 / 2}}}
        self._originalQrelDictTopicToDocRel = {}
        # [
        # (45, [('AP890711-0107', 100.47551447868), ('AP890629-0125', 2.47396397272)]),
        # (91, [('AP890711-0107', 200000.4755144787), ('AP890629-0125', 1.47396397272)])
        # ]

        self._trecListTopicCommaTuplesOfDocCommaScore = []

        self.__LoadQrelFile__(self._qrelCompleteFileName)
        self.__LoadTrecFile__(self._resultCompleteFileName)

        # 2.1
        self._avgNdcg = 0.0
        self._ndcg = {}
        # self.__Calculate_NDCG__()

        self._avgNdcg,  self._ndcg = self.__CalculateNdcgDict__()

        #3. Process  Trec data
        self._prec_list_Dict = {}
        self._rec_list_Dict = {}
        self._f_list_Dict = {}

        # for each topic
        self._avg_Prec = 0
        self._final_recall = 0

        self._num_topic = 0

        self._num_ret = 0
        self._num_rel_ret = 0
        self._sum_prec = 0

        self._r_prec = 0
        self._recalls = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        self._prec_at_recall = []
        self._cutoffs = [5, 10, 15, 20, 30, 100, 200, 500, 1000]
        # self._cutoffs = [1, 5, 10, 15, 20, 30, 100, 200]
        self._prec_at_cutoff = []
        self._recall_at_cutoff = []
        self._f_at_cutoff = []

        self._total_num_rel = 0
        self._total_num_rel_ret = 0
        self._total_num_ret = 0
        self._sum_prec_at_recall = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self._sum_prec_at_cutoff = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self._sum_recall_at_cutoff = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self._sum_f_at_cutoff = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        self._sum_avg_prec =0
        self._sum_r_prec = 0

        self._avg_prec_at_recall = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self._avg_prec_at_cutoff = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self._avg_recall_at_cutoff = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self._avg_f_at_cutoff= [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self._mean_avg_prec =0
        self._avg_r_prec = 0

        self.__ProcessTrecData__()

    ################################################################################
    def __ValidateInputArguments__(self):
        print 'Number of arguments:', len(self._inputArguments), 'arguments.'
        # print 'Argument List:', str(self._inputArguments)

        if len(self._inputArguments) < 3 or len(self._inputArguments) > 5:
            print "Illegal number of arguments passed."
            print "Usage:  trec_eval [-q] <qrel_file> <trec_file>\n\n"
            exit()

        if self._inputArguments[0] != Resource.TrecEvalText:
            print "Illegal trec_eval filename passed."
            exit()

        if self._inputArguments[1] == Resource.MinusQText and len(self._inputArguments) == 4:
            self._isMinusQ = True

        if len(self._inputArguments) == 4 and self._inputArguments[1] != Resource.MinusQText:
            print "2nd argument must be either -q or don't provide it from command line."
            exit()


        if self._isMinusQ == True:
             self._qrelCompleteFileName = self._inputArguments[2]
        else:
             self._qrelCompleteFileName = self._inputArguments[1]

        isQrelFileFound =  self.__isFileFound__( self._qrelCompleteFileName)
        if isQrelFileFound == False:
            print  self._qrelCompleteFileName, "--> Qrel file does not exist. Please check second last argument!"
            exit()

        if self._isMinusQ == True:
            self._resultCompleteFileName = self._inputArguments[3]
        else:
            self._resultCompleteFileName = self._inputArguments[2]

        isResultlFileFound =  self.__isFileFound__( self._resultCompleteFileName)
        if isResultlFileFound == False:
            print self._resultCompleteFileName, "--> Result file does not exist. Please check last argument!"
            exit()

    ################################################################################
    def __isFileFound__(self, fileCompletePath):
        return os.path.isfile(fileCompletePath)

    ################################################################################
    def __LoadQrelFile__(self, qrelFileCompletePath):
        with open(qrelFileCompletePath, "r+") as handle:
            for line in handle:
                aQrelLine = line.split(" ")
                topic = int(aQrelLine[0])
                docId = aQrelLine[2]
                rel = int(aQrelLine[3])
                originalRel = int(aQrelLine[3])
                if rel > 0:
                    rel = 1
                docIdToRel = {}
                docIdToOriginalRel = {}

                docIdToRel[docId] = rel
                docIdToOriginalRel[docId] = originalRel


                if self._qrelDictTopicToDocRel.has_key(topic):
                    self._qrelDictTopicToDocRel[topic].update(docIdToRel)
                    self._originalQrelDictTopicToDocRel[topic].update(docIdToOriginalRel)
                    self._num_rel[topic] = self._num_rel[topic] + rel
                else:
                    self._qrelDictTopicToDocRel[topic] = docIdToRel
                    self._originalQrelDictTopicToDocRel[topic] = docIdToOriginalRel
                    self._num_rel[topic] = rel

        # print "Total topics in qrel file ", len(self._qrelDictTopicToDocRel)
        # i = 0
        # for key, value in self._qrelDictTopicToDocRel.iteritems():
        #     i += 1
        #     print i, "topic : ", key , "... docs", len(self._qrelDictTopicToDocRel[key]), "dfff", self._num_rel[key]
        #
        # print "-----------------------------------------", "__LoadQrelFile__"

    ################################################################################
    def __LoadTrecFile__(self, resultFileCompletePath):
        trecTopicToDocScoreDict = {}
        with open(resultFileCompletePath, "r+") as handle:

            for line in handle:
                aResultLine = line.split(" ")
                topic = int(aResultLine[0])
                docId = aResultLine[2]
                score = float(aResultLine[4])
                docIdToScore = {}

                docIdToScore[docId] = score

                if trecTopicToDocScoreDict.has_key(topic):
                    trecTopicToDocScoreDict[topic].update(docIdToScore)
                else:
                    trecTopicToDocScoreDict[topic] = docIdToScore

            tempTrecTopicToDocScoreTuple = sorted(trecTopicToDocScoreDict.items(), key=lambda x:x[0])
            for item in tempTrecTopicToDocScoreTuple:
                topic, docIdToScoreValue = item
                docIdCommaScoreOrderedByValue =   sorted(docIdToScoreValue.items(), key=lambda x:x[1], reverse = True)

                i =0
                tempDocIdCommaScoreOrderedByValue = []
                for item in docIdCommaScoreOrderedByValue:
                    i += 1
                    if i <= TrecEval.NoOfDocs:
                        tempDocIdCommaScoreOrderedByValue.append(item)
                newTupe = (topic, tempDocIdCommaScoreOrderedByValue)
                self._trecListTopicCommaTuplesOfDocCommaScore.append(newTupe)


        # print "Total topics in RESULT file ", len(trecTopicToDocScoreDict)
        # i = 0
        # for topic, TuplesOfDocCommaScore in self._trecListTopicCommaTuplesOfDocCommaScore:
        #     i += 1
        #     print i, "topic : ", topic , "... docs", len(TuplesOfDocCommaScore)

        # print "-----------------------------------------", "__LoadTrecFile__"

    ################################################################################
    def __ProcessTrecData__(self):
        for topic, TuplesOfDocCommaScore in self._trecListTopicCommaTuplesOfDocCommaScore:
            self.__ReloadDataStructure__()
            if not self._num_rel.has_key(topic):
                continue
            # ----------------------------------
            self._num_topic += 1
            href = TuplesOfDocCommaScore
            # -------- for each document in Trc file (IDF file) ---------------------
            self._num_ret = 0
            for docId, rel in href:
                self._num_ret += 1

                if self._qrelDictTopicToDocRel[topic].has_key(docId):
                    rel = self._qrelDictTopicToDocRel[topic][docId]
                    self._sum_prec =  (self._sum_prec + (rel * (1 + self._num_rel_ret)) / float(self._num_ret))

                    self._num_rel_ret  = self._num_rel_ret + rel

                self._prec_list_Dict[self._num_ret] = self._num_rel_ret / float(self._num_ret)

                self._rec_list_Dict[self._num_ret] = self._num_rel_ret / float(self._num_rel[topic])
                denominator = self._prec_list_Dict[self._num_ret] + self._rec_list_Dict[self._num_ret]
                if denominator == 0:
                    self._f_list_Dict[self._num_ret] = 0
                else:
                    self._f_list_Dict[self._num_ret] = 2 * self._prec_list_Dict[self._num_ret] * self._rec_list_Dict[self._num_ret] / denominator

                if  self._num_ret >= TrecEval.NoOfDocs :
                    print self._num_ret
                    break

            self._avg_prec = self._sum_prec / self._num_rel[topic]
            # -------Avg. Precision & Final recall -------------------

            self._avg_Prec = self._sum_prec / float(self._num_rel[topic])
            self._final_recall = self._num_rel_ret / self._num_rel[topic]

            # --------Update remaining precision and recall list --------
            # if all relevant are seen till 150, then update Precision and recall for remianing 50
            i = self._num_ret + 1
            while  i <= TrecEval.NoOfDocs:
                self._prec_list_Dict[i] = self._num_rel_ret / i
                self._rec_list_Dict[i] = self._final_recall
                denominator = self._prec_list_Dict[i] + self._rec_list_Dict[i]
                if denominator == 0:
                    self._f_list_Dict[self._num_ret] = 0
                else:
                    self._f_list_Dict[self._num_ret] = 2 * self._prec_list_Dict[i] * self._rec_list_Dict[i] / denominator
                i = i + 1

            # --------Precision, Recall, F1 @ cut off--------------------------
            for cutOffValue in self._cutoffs:
                self._prec_at_cutoff.append(self._prec_list_Dict[cutOffValue])
                self._recall_at_cutoff.append(self._rec_list_Dict[cutOffValue])
                self._f_at_cutoff.append(self._f_list_Dict[cutOffValue])

            # -------R Precision---------------------------
            if (self._num_rel[topic] > self._num_ret):
                self._r_prec =self._num_rel_ret/float(self._num_rel[topic])
            else:
                int_num_rel = int(self._num_rel[topic])
                frac_num_rel = float(self._num_rel[topic] - int_num_rel)

                if frac_num_rel > 0:
                     self._r_prec = float(1 - frac_num_rel) * self._rec_list_Dict[int_num_rel] + \
                                    frac_num_rel * self._prec_list_Dict[int_num_rel+1]
                else:
                    self._r_prec =  self._prec_list_Dict[int_num_rel]

            #------- Interpolated precisions -------------
            max_prec = 0
            for x in reversed(range(1, 201)):
                if (self._prec_list_Dict[x] > max_prec):
                    max_prec = self._prec_list_Dict[x]
                else:
                    self._prec_list_Dict[x] = max_prec

            #------ Precision @ recall levels-----------
            i = 1
            for recall in self._recalls:
                while (i <= TrecEval.NoOfDocs and  self._rec_list_Dict[i] < recall):
                    i = i + 1

                if (i <= TrecEval.NoOfDocs):
                    self._prec_at_recall.append(self._prec_list_Dict[i])
                else:
                    self._prec_at_recall.append(0)

            # ---------- Update running sums for overall state -----

            self._total_num_rel += self._num_rel[topic]
            self._total_num_rel_ret  += self._num_rel_ret
            self._total_num_ret  += self._num_ret
            # ---------- Update sums for Precision, Recall, F1 @ cut off -----
            i = 0
            for cutoff in self._cutoffs:
                self._sum_prec_at_cutoff[i] = self._sum_prec_at_cutoff[i] + self._prec_at_cutoff[i]
                self._sum_recall_at_cutoff[i] = self._sum_recall_at_cutoff[i] + self._recall_at_cutoff[i]
                self._sum_f_at_cutoff[i] = self._sum_f_at_cutoff[i] + self._f_at_cutoff[i]
                i += 1

            i = 0
            for recall in self._recalls:
                self._sum_prec_at_recall[i] = self._sum_prec_at_recall[i] + self._prec_at_recall[i]
                i += 1

            self._sum_avg_prec += self._avg_prec
            self._sum_r_prec += self._r_prec

             # ---------- Calculate summary/Avg. state for Precision, Recall, F1 @ cut off----------
            i = 0
            for cutoff in self._cutoffs:
                self._avg_prec_at_cutoff[i] = self._sum_prec_at_cutoff[i] / float(self._num_topic)
                self._avg_recall_at_cutoff[i] = self._sum_recall_at_cutoff[i] / float(self._num_topic)
                self._avg_f_at_cutoff[i] = self._sum_f_at_cutoff[i] / float(self._num_topic)
                i += 1

            i = 0
            for recall in self._recalls:
                self._avg_prec_at_recall[i] = (self._sum_prec_at_recall[i] / float(self._num_topic))
                i += 1

            self._mean_avg_prec = self._sum_avg_prec / self._num_topic
            self._avg_r_prec = self._sum_r_prec / self._num_topic

            # -------- Print details for every query --------
            if self._isMinusQ:
                self.__PrintEval__( topic,  self._num_ret,  self._num_rel[topic],  self._num_rel_ret,
                                    self._prec_at_recall, self._avg_Prec,  self._prec_at_cutoff,
                                    self._recall_at_cutoff, self._avg_f_at_cutoff, self._r_prec, self._ndcg[topic])

            self.__SavePrecisionRecallAtKInCSV__(self._prec_list_Dict,self._rec_list_Dict, topic, Resource.HW1Output)

        # ------Final query----------------------
        self.__PrintEval__(self._num_topic,  self._total_num_ret,  self._total_num_rel,  self._total_num_rel_ret,
                           self._avg_prec_at_recall,  self._mean_avg_prec,  self._avg_prec_at_cutoff,
                           self._avg_recall_at_cutoff, self._avg_f_at_cutoff, self._avg_r_prec, self._avgNdcg)

        # self.__SavePrecisionRecallAtKInCSV__(self._avg_prec_at_cutoff,
        #                                      self._avg_recall_at_cutoff,
        #                                      "Avg_BM25_Prec_Recall",
        #                                      Resource.HW1Output)


        # print "-----------------------------------------", "__ProcessTrecData__"

    ################################################################################
    def __ReloadDataStructure__(self):
        self._prec_list_Dict = {}
        self._rec_list_Dict = {}

        # for each topic
        self._avg_Prec = 0
        self._final_recall = 0

        self._num_ret = 0
        self._num_rel_ret = 0
        self._sum_prec = 0

        self._r_prec = 0
        self._prec_at_recall = []
        self._prec_at_cutoff = []

    ################################################################################
    def __PrintEval__(self, qid, num_ret, num_rel, num_rel_ret,
                      prec_at_recall, avg_Prec, prec_at_cutoff,
                      recall_at_cutoff, f_at_cutoff, r_prec, ndcg):
        print "************************************************************"
        print "Queryid (Num):    %d\n" % qid

        print "Total number of documents over all queries"
        print "    Retrieved:    %d" % num_ret
        print "    Relevant:     %d" % num_rel
        print "    Rel_ret:      %d\n" % num_rel_ret

        print "Interpolated Recall - Precision Averages:"
        print "    at 0.00       %.4f" % prec_at_recall[0]
        print "    at 0.10       %.4f" % prec_at_recall[1]
        print "    at 0.20       %.4f" % prec_at_recall[2]
        print "    at 0.30       %.4f" % prec_at_recall[3]
        print "    at 0.40       %.4f" % prec_at_recall[4]
        print "    at 0.50       %.4f" % prec_at_recall[5]
        print "    at 0.60       %.4f" % prec_at_recall[6]
        print "    at 0.70       %.4f" % prec_at_recall[7]
        print "    at 0.80       %.4f" % prec_at_recall[8]
        print "    at 0.90       %.4f" % prec_at_recall[9]
        print "    at 1.00       %.4f\n" % prec_at_recall[10]

        print "Average precision (non-interpolated) for all rel docs(averaged over queries)"
        print "                  %.4f" % avg_Prec
        print "Precision:"
        print "  At    5 docs:   %.4f" % prec_at_cutoff[0]
        print "  At   10 docs:   %.4f" % prec_at_cutoff[1]
        print "  At   15 docs:   %.4f" % prec_at_cutoff[2]
        print "  At   20 docs:   %.4f" % prec_at_cutoff[3]
        print "  At   30 docs:   %.4f" % prec_at_cutoff[4]
        print "  At  100 docs:   %.4f" % prec_at_cutoff[5]
        print "  At  200 docs:   %.4f" % prec_at_cutoff[6]
        print "  At  500 docs:   %.4f" % prec_at_cutoff[7]
        print "  At 1000 docs:   %.4f\n" % prec_at_cutoff[8]

        print "Recall:"
        print "  At    5 docs:   %.4f" % recall_at_cutoff[0]
        print "  At   10 docs:   %.4f" % recall_at_cutoff[1]
        print "  At   15 docs:   %.4f" % recall_at_cutoff[2]
        print "  At   20 docs:   %.4f" % recall_at_cutoff[3]
        print "  At   30 docs:   %.4f" % recall_at_cutoff[4]
        print "  At  100 docs:   %.4f" % recall_at_cutoff[5]
        print "  At  200 docs:   %.4f" % recall_at_cutoff[6]
        print "  At  500 docs:   %.4f" % recall_at_cutoff[7]
        print "  At 1000 docs:   %.4f\n" % recall_at_cutoff[8]

        print "F1:"
        print "  At    5 docs:   %.4f" % f_at_cutoff[0]
        print "  At   10 docs:   %.4f" % f_at_cutoff[1]
        print "  At   15 docs:   %.4f" % f_at_cutoff[2]
        print "  At   20 docs:   %.4f" % f_at_cutoff[3]
        print "  At   30 docs:   %.4f" % f_at_cutoff[4]
        print "  At  100 docs:   %.4f" % f_at_cutoff[5]
        print "  At  200 docs:   %.4f" % f_at_cutoff[6]
        print "  At  500 docs:   %.4f" % f_at_cutoff[7]
        print "  At 1000 docs:   %.4f\n" % f_at_cutoff[8]

        print "R-Precision (precision after R (= num_rel for a query) docs retrieved):"
        print "    Exact:        %.4f\n" % r_prec

        print "Avergae nDCG value "
        print "                  %.4f\n" % ndcg

    ################################################################################
    def __SavePrecisionRecallAtKInCSV1__(self, prec_dict, recall_dict, topic, filePath):
        completeFilePath = filePath + str(topic) + ".csv"
        # print completeFilePath
        precDIff = 1 - prec_dict[1]
        recallDiff = 1 - recall_dict[len(recall_dict) - 1]

        tempPrecDict = {}
        tempRecallDict = {}

        for key, value   in prec_dict.iteritems():
            tempPrecDict[key] = prec_dict[key] +  precDIff
            tempRecallDict[key] = recall_dict[key] +  recallDiff

        with open(completeFilePath, 'wb') as csvfile:
            fieldnames = ['Precision', 'Recall']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for x in range(1, len(tempPrecDict)):
                if x > 1:
                    if tempPrecDict[x] > tempPrecDict[x-1]:
                        tempPrecDict[x] = tempPrecDict[x-1]

                writer.writerow({'Precision': tempPrecDict[x], 'Recall': tempRecallDict[x]})
            csvfile.close()

    def __SavePrecisionRecallAtKInCSV__(self, prec_dict, recall_dict, topic, filePath):
        completeFilePath = filePath + str(topic) + ".csv"
        # print completeFilePath
        precDIff = 1 - prec_dict[1]
        recallDiff = 1 - recall_dict[len(recall_dict) - 1]

        tempPrecDict = {}
        tempRecallDict = {}

        for key, value   in prec_dict.iteritems():
            tempPrecDict[key] = prec_dict[key] +  precDIff
            tempRecallDict[key] = recall_dict[key] +  recallDiff

        with open(completeFilePath, 'wb') as csvfile:
            fieldnames = ['Precision', 'Recall']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for x in range(1, len(tempPrecDict)):
                # if x > 1:
                #     if tempPrecDict[x] > tempPrecDict[x-1]:
                #         tempPrecDict[x] = tempPrecDict[x-1]

                writer.writerow({'Precision': tempPrecDict[x], 'Recall': tempRecallDict[x]})
            csvfile.close()

    def __GetnormalizedArray__(self, array):
        result = []
        maxValue = max(array)
        minValue = min(array)
        for value in array:
            x = (value - minValue)/(maxValue - minValue)
            result.append(x)
            print value, x

        return result

    ################################################################################
    def __GetDcgValue__(self, relevances):
        dcg = 0
        for x in range(0, len(relevances)):
            if x == 0:
                dcg = relevances[x]
            else:
                dcg += relevances[x]/float(math.log(x+1, 2))
        return dcg

    #*****************************************
    def __GetNdcgValue__(self, dcgValueForTopicId, sortedRelevancesForTopicId):
        dcg = float(self.__GetDcgValue__(sortedRelevancesForTopicId))
        if float(dcg) == 0.0:
            return 0.0
        ndcg = dcgValueForTopicId/float(dcg)

        return ndcg

    #*****************************************
    def __GetRelavanceForQueryAndDoc__(self, queryId, docId):
        if not self._originalQrelDictTopicToDocRel.has_key(queryId):
            return 0

        docIdToRelavanceValueDict = self._originalQrelDictTopicToDocRel[queryId]

        if not docIdToRelavanceValueDict.has_key(docId):
            return 0

        return docIdToRelavanceValueDict[docId]

    #*****************************************
    def __CalculateNdcgDict__(self):
        queryIdToRelavanceList = {}
        for queryId, tupleDocIdCommaScore in self._trecListTopicCommaTuplesOfDocCommaScore:
             if not queryIdToRelavanceList.has_key(queryId):
                 queryIdToRelavanceList[queryId] = []

             for docId, resultScore in tupleDocIdCommaScore:
                 rel = self.__GetRelavanceForQueryAndDoc__(queryId, docId)
                 queryIdToRelavanceList[queryId].append(rel)

        dcgDict = {}
        ndcgDict = {}
        sumNdcg = 0
        topicIdCount = 0
        for queryId, relevanceList in queryIdToRelavanceList.iteritems():
            dcgDict[queryId] = 0
            dcgDict[queryId] = self.__GetDcgValue__(relevanceList)
            sortedList = sorted(relevanceList, reverse=True)
            ndcgDict[queryId] = 0
            ndcgDict[queryId] = self.__GetNdcgValue__(dcgDict[queryId], sortedList)

            topicIdCount += 1
            sumNdcg += ndcgDict[queryId]

        return sumNdcg/topicIdCount, ndcgDict

#########################################################################
# END
#########################################################################

# HW 1
# RUN TRECEVAL.PY
# cd C:\Users\vikas\Dropbox\CS6200_V_Sangwan\HW5\src\TrecEval
# python TrecEval.py qrels.adhoc.51-100.AP89.txt OkapiBM25.txt
# CSV files are created in is saved in 'C:\Users\vikas\Dropbox\CS6200_V_Sangwan\HW5\output\HW1' path

# Plot GRAPH
# cd C:\Users\vikas\Dropbox\CS6200_V_Sangwan\HW5\src\R>
# & 'C:\Program Files\R\R-3.3.1\bin\x64\Rscript.exe' .\HW1Plotter.R

# ---------Real trec eval--------------
#  cd C:\Users\vikas\Dropbox\CS6200_V_Sangwan\HW1\output>
# C:\Strawberry\perl\bin\perl.exe trec_eval.pl qrels.adhoc.51-100.AP89.txt OkapiBM25.txt

obj = TrecEval(sys.argv)
