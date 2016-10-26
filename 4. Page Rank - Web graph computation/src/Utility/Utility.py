import pickle

class Utility:
    def __init__(self):
         a = 10

    #####################################################################
    # FILE HELPERS - PICKLE
    #####################################################################
    def __DumpDataIntoPickleFile__(self, fileCompletePath, data):
        # print "__DumpDataIntoFile__"
        with open(fileCompletePath, "wb+") as handle:
            # print "Dumping  data ..", fileCompletePath
            pickle.dump(data, handle)
            handle.close()

    def __ReadDataFromPickleFile__(self, fileCompletePath):
        # print "__ReadPickeData__"
        with open(fileCompletePath, "rb") as handle:
            # print "Reading...", fileCompletePath
            data = pickle.load(handle)
            # print "Data type : ", type(data)
            # print "Length of data : ", len(data)
            return data

    #####################################################################
    # FILE HELPERS - TEXT
    #####################################################################


    def __DumpDictDataIntoTextFile__(self, fileCompletePath, dictData):
        # print "__DumpDataIntoFile__"
        with open(fileCompletePath, "w+") as handle:
            # print "Dumping  data ..", fileCompletePath
            c = 0
            for key, value in dictData.iteritems():

                c+=1
                handle.write(str(c) + " " + str(key) + " " + str(value) + "\n")
            handle.close()

    def __DumpDictDataIntoTextFile2__(self, fileCompletePath, dictData):
        # print "__DumpDataIntoFile__"
        with open(fileCompletePath, "w+") as handle:
            # print "Dumping  data ..", fileCompletePath
            c = 0
            for key, value in dictData.iteritems():

                c+=1
                handle.write(str(key) + " " + str(value) + "\n")
            handle.close()

    def __DumpListDataIntoTextFile__(self, fileCompletePath, listData):
        # print "__DumpDataIntoFile__"
        with open(fileCompletePath, "w+") as handle:
            # print "Dumping  data ..", fileCompletePath
            c = 0
            for item in listData:
                c+=1
                handle.write(str(c) + " " + str(item) + "\n" )
            handle.close()

    def __ReadDictFromTextFile__(self, fileCompletePath):
        dataDict = {}
        with open(fileCompletePath, "r+") as handle:
            for line in handle:
                line = line.lower().strip("\n")
                dataSepBySpaceArray = line.split(" ")
                dataSepBySpaceArray = filter(None, dataSepBySpaceArray)
                if len(dataSepBySpaceArray) > 1:
                    key = dataSepBySpaceArray[1].strip("\n").lower().replace("https","http")
                    value = dataSepBySpaceArray[2:]
                    dataDict[key] = value
        return dataDict


    def __ReadListFromTextFile__(self, fileCompletePath):
        resultList = []
        with open(fileCompletePath, "r+") as handle:
            for line in handle:
                line = line.strip("\n")

                dataSepBySpaceArray = line.split(" ")
                dataSepBySpaceArray = filter(None, dataSepBySpaceArray)
                if len(dataSepBySpaceArray) > 1:
                    value = dataSepBySpaceArray[1]
                    resultList.append(value)
        return resultList

    def __DumpDictDataIntoTextFile1__(self, fileCompletePath, dictData):
        # print "__DumpDataIntoFile__"
        with open(fileCompletePath, "w+") as handle:
            # print "Dumping  data ..", fileCompletePath
            c = 0
            for key, value in dictData.iteritems():
                c+=1
                handle.write(key + " " + str(value) + "\n")
            handle.close()




