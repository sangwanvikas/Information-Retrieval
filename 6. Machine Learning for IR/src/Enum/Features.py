class FeaturesEnum:
    def __init__(self):
        print ""
        self._features = ["IDF", "JelinekMercer", "LaplaceSmoothing", "OkapiBM25", "OkapiTF"]


    def fromstring(self, str):
        k = 0
        for feature in self._features :
            k += 1
            if feature.upper() == str.upper():
                return k