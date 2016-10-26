##########################################################################################################
# All CONSTANTS USED THROUGHOUT THE PROJECT ARE DECLARED IN THIS FILE
##########################################################################################################

INDEX_NAME = "hw8_ap_index"
TYPE_NAME = "document"
################################################################
# i/p files path
inputDirPath = "C:/Users/vikas/Dropbox/sangwan.ea@gmail.com/hw8/input"
bm25FilePath = inputDirPath + "/OkapiBM25.txt"
QrelAdhocFilePath = inputDirPath + "/qrels.adhoc.51-100.AP89.txt"
AllQueryIdsFilePath = inputDirPath + "/all_query_ids.txt"

###############################################################
outputDirPath = "C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW8/output"
OutputDirPathForTopicModelPerQuery = outputDirPath + "/TopicModelPerQuery"
QIdToRelDocIdsMapFilePath = OutputDirPathForTopicModelPerQuery + "/qId_to_rel_documents.txt"
DocumentTermMatrixFilePath = OutputDirPathForTopicModelPerQuery + "/matrix.csv"
QIdToDocumentsTextMapFilePath = OutputDirPathForTopicModelPerQuery + "/qIs_to_documentsText.pkl"
TopicModelResultsFilePath = OutputDirPathForTopicModelPerQuery + "/TopicModelResults"

###############################################################
ClusteringOutputDirPath = outputDirPath + "/Clustering"
DocIdCommaDocTextFilePath = ClusteringOutputDirPath + "/1. docId_comma_docText.pkl"
DocTermMatrixFilePath = ClusteringOutputDirPath + "/2. doc_term_matrix.pkl"
DocTopicProbDistrFilePath = ClusteringOutputDirPath + "/3. doc_topic_distribution.pkl"
ResultsForEachClusterFilePath = ClusteringOutputDirPath + "/ResultsForEachCluster"
################################################################

INDEX_REQUEST_BODY= {
    "settings": {
    "index": {
    "max_result_window" : "85000",
    "store": {
        "type": "default"
    },
    "number_of_shards": 1,
    "number_of_replicas": 1
    },
    "analysis": {
        "analyzer": {
            "my_english": {
                "type": "english",
                "stopwords_path": "stoplist.txt",
            }
        }
    }
    }
 }
################################################################

MAPPING_BODY={
    "properties": {
      "docno": {
        "type": "string",
        "store": "true",
        "index": "not_analyzed"
      },
      "text": {
        "type": "string",
        "store": "true",
        "index": "analyzed",
        "term_vector": "with_positions_offsets_payloads",
        "analyzer": "my_english"
      }
    }
}
################################################################
REQUEST_BODY_FIND_ALL_FEATURES = {
    "size":0,
    "aggs": {
        "features": {
            "terms": {
                "field": "text",
                "size" : 0,
                "min_doc_count": 1
            }
        }
    }
}
################################################################
CorpusSize = 85000
REQUEST_BODY_FIND_TEXT_FOR_ALLDOCS = {
    "query" : {
        "match_all" : {}
    },
    "size": CorpusSize
}





################################################################

query85TersmList = ["allegations", "measures", "against", "corrupt", "public", "officials",  "governmental", "jurisdiction", "worldwide"]
query59TersmList =[ "weather", "event", "caused", "least", "one", "fatality", "location"]
query56TersmList =["prediction", "prime", "lending", "rate", "actual"]# can
query71TersmList = ["incursions", "land", "air", "water","border","area", "country", "military", "forces", "guerrilla", "group", "based"]
query71TersmList64 =["event", "result", "politically", "motivated", "hostage", "taking"]
query71TersmList62 = ["military", "coup", "d'etat", "attempted", "successful", "country"]
query71TersmList93 = ["supporters", "National", "Rifle", "Association", "NRA", "assets"]
query71TersmList99 = ["development", "Iran", "Contra", "Affair"]
query71TersmList58 = ["rail", "strike", "ongoing"]
query71TersmList77 = ["poaching", "method", "wildlife"]
query71TersmList54 = ["signing", "contract", "preliminary", "agreement", "making", "tentative", "reservation", "launch", "commercial", "satellite"]
query71TersmList87 = ["criminal", "actions", "against", "officers", "failed", "financial", "institution"]
query71TersmList94 = ["crime", "perpetrated", "computer"]
query71TersmList100 = ["efforts", "non","communist","industrialized", "states","regulate","transfer", "tech", "goods", "dual", "technologies", "undesirable", "nations"]
query71TersmList89 = ["investment", "OPEC", "downstream"]
query71TersmList61 = ["role", "Israel", "Iran", "Contra", "Affair"]
query71TersmList95 = ["computer", "application", "crime", "solving"]
query71TersmList68 = ["studies", "unsubstantiated",  "concerns", "safety", "manufacturing", "employees", "installation", "workers", "fine", "diameter", "fibers", "insulation", "products"]
query71TersmList57 = ["MCI", "doing", "since", "Bell", "System", "breakup"]
query71TersmList97 = ["instances", "fiber", "optics", "technology", "actually", "use"]
query71TersmList98  = ["organizations",  "fiber", "optics", "equipment"]
query71TersmList60  = ["controversy", "standards", "performance", "salary", "incentive", "pay", "contrasted", "seniority", "longevity", "job"]
query71TersmList80 =  ["platform", "1988", "presidential", "candidate"]
query71TersmList63 =  ["machine", "translation"]
query71TersmList91  = ["acquisition", "u.s.", "Army", "specified", "advanced", "weapons", "systems"]
################################################################

OriginalQuery85TersmList = "Document will discuss allegations, or measures being taken against corrupt public officials of any governmental jurisdiction worldwide"
OriginalQuery59TersmList= "Document will report a type of weather event which has directly caused at least one fatality in some location"
OriginalQuery56TersmList= "Document will include a prediction about the prime lending rate, or will report an actual prime rate move"
OriginalQuery71TersmList="Document will report incursions by land, air, or water into the border area of one country by military forces of a second country or a guerrilla group based in a second country."
OriginalQuery71TersmList64="Document will report an event or result of politically motivated hostage taking."
OriginalQuery71TersmList62="Document will report a military coup detat, either attempted or successful, in any country."
OriginalQuery71TersmList93="Document must describe or identify supporters of the National Rifle Association (NRA), or its assets."
OriginalQuery71TersmList99="Document will identify a development in the Iran Contra Affair."
OriginalQuery71TersmList58="Document will predict or anticipate a rail strike or report an ongoing rail  strike."
OriginalQuery71TersmList77="Document will report a poaching method used against a certain type of wildlife."
OriginalQuery71TersmList54="Document will cite the signing of a contract or preliminary agreement, or the making of a tentative reservation, to launch a commercial satellite."
OriginalQuery71TersmList87="Document will report on current criminal actions against officers of a failed USA financial institution."
OriginalQuery71TersmList94="Document must identify a crime perpetrated with the aid of a computer."
OriginalQuery71TersmList100="Document will identify efforts by the non communist, industrialized states to regulate the transfer of high tech goods or Dual use technologies to undesirable nations."
OriginalQuery71TersmList89="Document must identify an existing or pending investment by an OPEC member state in any downstream operation."
OriginalQuery71TersmList61="Document will discuss the role of Israel in the Iran Contra Affair.   "
OriginalQuery71TersmList95="Document must describe a computer application to crime solving.   "
OriginalQuery71TersmList68="Document will report actual studies, or even unsubstantiated concerns about the safety to manufacturing employees and installation workers of fine diameter fibers used in insulation and other products.   "
OriginalQuery71TersmList57="Document will discuss how MCI has been doing since the Bell System breakup.   "
OriginalQuery71TersmList97="Document must identify instances of fiber optics technology actually in use.    "
OriginalQuery71TersmList98="Document must identify individuals or organizations which produce fiber optics equipment.   "
OriginalQuery71TersmList60="Document will describe either one or both sides of the controversy over the use of standards of performance to determine salary levels and incentive pay as contrasted with determining pay solely on the basis of seniority or longevity on the job."
OriginalQuery71TersmList80="Document will identify something about the platform of a 1988 presidential  candidate.   "
OriginalQuery71TersmList63= "Document will identify a machine translation system.   "
OriginalQuery71TersmList91="Document will identify acquisition by the USA Army of specified advanced weapons systems.   "
