######################################################################################
# Jelinek-Mercer model
######################################################################################



class JelinekMercer:
    #############   Constructor   #########################################
    def __init__(self):
        print "JelinekConst`"
        self._lambda = .8

    #############   dt for Jelinek Mercer ########################################
    def __CalculateDtForJelinekMercer__(self, tf, docLength, summationOfTFCompliment, summationOfTotalLengthCompliment):
        foregroundProbability = self._lambda * (tf/docLength)
        backgroundProbability = (1-self._lambda)* (summationOfTFCompliment/summationOfTotalLengthCompliment)

        result = foregroundProbability + backgroundProbability
        # if result == 0:
        #     print tf, docLength, summationOfTFCompliment, summationOfTotalLengthCompliment
        #     print "foreground: ", foregroundProbability, "background: ", backgroundProbability

        return result

######################################################################################
# END
######################################################################################