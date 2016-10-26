import sys

sys.path.append('C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW5/src/Resource')

import Resource
from sets import Set

##########################################################
with open(Resource.QrelFilePath,"r+") as handle:
    # {'1509': {'anup': {'6c08b151f68bd4c51d2dc87ef9ae4d5d': '2', '42234fdad0fd6c5a7d2e86284fbf78d5': '1'},
    #           'vikas': {'6c08b151f68bd4c51d2dc87ef9ae4d5d': '1', '42234fdad0fd6c5a7d2e86284fbf78d5': '2'},
    #           'prv': {'6c08b151f68bd4c51d2dc87ef9ae4d5d': '0', '906ca502d8bee98de5fb07cc50d00995': '1',
    #                    '42234fdad0fd6c5a7d2e86284fbf78d5': '0'}
    #           },
    # {'1510': {'anup': {'6c08b151f68bd4c51d2dc87ef9ae4d5d': '2', '42234fdad0fd6c5a7d2e86284fbf78d5': '1'},
    #           'vikas': {'6c08b151f68bd4c51d2dc87ef9ae4d5d': '1', '42234fdad0fd6c5a7d2e86284fbf78d5': '2'},
    #           'prv': {'6c08b151f68bd4c51d2dc87ef9ae4d5d': '0', '906ca502d8bee98de5fb07cc50d00995': '1',
    #                    '42234fdad0fd6c5a7d2e86284fbf78d5': '0'}
    #           }
    # }
    authorName = Set()
    # 1. Load qrel file in to qeryIdToAssessorDict
    qeryIdToAssessorDict = {}
    for line in handle:
        aLineItmes = line.split(" ")

        queryId = aLineItmes[0].rstrip()
        assessor = aLineItmes[1].rstrip()
        docId = aLineItmes[2].rstrip()
        rel = aLineItmes[3].rstrip()

        if not qeryIdToAssessorDict.has_key(queryId):
            qeryIdToAssessorDict[queryId] = {}

        if not qeryIdToAssessorDict[queryId].has_key(assessor):
            qeryIdToAssessorDict[queryId][assessor] = {}
            authorName.add(assessor)

        qeryIdToAssessorDict[queryId][assessor].update({docId:rel})

    print qeryIdToAssessorDict
    assessors = list(authorName)
    # print assessors[0], assessors[1], assessors[2]

    # 2. Combine three documents to 1 for a queryId
    # {'15010': {'6c08b151f68bd4c51d2dc87ef9ae4d5d': 1, '42234fdad0fd6c5a7d2e86284fbf78d5': 1},
    #  '1509': {'6c08b151f68bd4c51d2dc87ef9ae4d5d': 2, '42234fdad0fd6c5a7d2e86284fbf78d5': 1}
    # }
    finalQueryIdToDocIdToRel = {}
    for queryId, AssessorTodocIdToRelDict in qeryIdToAssessorDict.iteritems():
        if not finalQueryIdToDocIdToRel.has_key(queryId):
            finalQueryIdToDocIdToRel[queryId] = {}

        for assessor, docToRelDict in AssessorTodocIdToRelDict.iteritems():
            for docId, rel in docToRelDict.iteritems():
                sum = 0
                rel = 0

                for x in range(0, len(assessors)-1):
                    sum +=  int(AssessorTodocIdToRelDict[assessors[x]][docId])
                print queryId, docId, sum

                rel = 0
                if sum==0:
                    rel = 0
                if sum == 1:
                    rel = 1
                if sum>=2:
                    rel = 2
                finalQueryIdToDocIdToRel[queryId].update({docId:rel})
            break

        print finalQueryIdToDocIdToRel

    # 3. Write into new text file
    with open(Resource.QrelFinalFilePath, 'w+') as writeHandle:
        for queryId, docIdToRelDict in finalQueryIdToDocIdToRel.iteritems():
            for docId, rel in docIdToRelDict.iteritems():
                aLine = queryId + " " + "Final" + " " + docId + " "+ str(rel) +"\n"
                writeHandle.write(aLine)