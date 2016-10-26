######################################################################################
# OKAPI BM 25
######################################################################################
import math



class OkapiBM25:
    ################################################################
    def __init__(self):
        # print "Constructor from OkapiBM25"
        self.k1 = 1.2
        self.k2 = 1000
        self.b = .5

    ###########################  DT for OKAPI TF #####################################

    def __CalculateDtForOkapiBM__(self,tf, docLength,avgDocumentLength,totalDocumentLength,
                                  NoOfDocsContainingterm,TFOfTermInQuery):
        firstNumerator = totalDocumentLength + .5
        firstDenominator = NoOfDocsContainingterm+.5
        firstValue = math.log(firstNumerator/firstDenominator)

        secondNumerator = tf + (self.k1*tf)
        secondDenominator = tf+ (self.k1*((1-self.b) + (self.b*(docLength/avgDocumentLength))))
        secondValue = secondNumerator/secondDenominator

        thirdNumeratorSecond = self.k2 * TFOfTermInQuery
        thirdNumerator = TFOfTermInQuery + thirdNumeratorSecond
        thirdDenominator = TFOfTermInQuery+self.k2
        thirdValue = thirdNumerator/thirdDenominator

        return firstValue * secondValue * thirdValue

######################################################################################
#END
######################################################################################