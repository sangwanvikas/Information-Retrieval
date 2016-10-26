######################################################################################
# Laplace Smoothing model
######################################################################################
from decimal import Decimal



class LaplaceSmoothing:
    #############  Constructor  ###############################################
    def __init__(self, _uniqeTermInCorpus):
        # V is the vocabulary size. It is the total number of unique terms in the collection.
        self._V = _uniqeTermInCorpus

    #############  dt for Laplace Smoothing    ######################################
    def __CalculateDtForLaplaceSmoothing__(self,tf, docLength):
        numerator = tf + 1
        denominator = docLength + self._V
        result = Decimal(numerator) / Decimal(denominator)

        return result