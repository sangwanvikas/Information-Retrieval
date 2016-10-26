#######################################################################################
# OkapiTF
#######################################################################################

class OkapiTF:

    ########################################################
    def __init__(self):
        self._alpha = .5
        self._beta = 1.5

    ############################  DT for OKAPI TF and OKAPI IDF  #######################
    def __CalculateDtForOneTermInOneDocuments__(self, termFrequencyArg, lengthOfDocArg, avgDDocumentLength):
        if avgDDocumentLength >0:
            return termFrequencyArg/(termFrequencyArg + self._alpha +(self._beta * (lengthOfDocArg/ avgDDocumentLength)))
        else:
            print "No document found with this term"


#######################################################################################
#END
#######################################################################################