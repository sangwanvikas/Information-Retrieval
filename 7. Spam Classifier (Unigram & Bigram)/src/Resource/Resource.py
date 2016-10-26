
#---------------------------------------------------------------------------------------
StopWordsFilePath = "F:/IR CS6200/elasticsearch-2.3.2/elasticsearch-2.3.2/config/stoplist.txt"
InputDirectoryPath = "C:/Users/vikas/Dropbox/sangwan.ea@gmail.com/hw7/Input"
EmailDirectoryPath = InputDirectoryPath + "/trec07p/data"
SpamIdentifierMapFilePath = InputDirectoryPath + "/trec07p/full/index"
ManualSpamWordsFilePath = InputDirectoryPath + "/manual_spam_words.txt"

outputDirPath = "C:/Users/vikas/Dropbox/CS6200_V_Sangwan/HW7/output"
# ---------------------
ManualSpamOutputDirPath = outputDirPath + "/ManualSpamClassifier"
TrainMatrixFilePath = ManualSpamOutputDirPath + "/train_matrix.pkl"
TrainLabelsFilePath = ManualSpamOutputDirPath + "/train_labels.pkl"

TestMatrixFilePath = ManualSpamOutputDirPath + "/test_matrix.pkl"
TestLabelsFilePath = ManualSpamOutputDirPath + "/test_labels.pkl"
TestEmailIdToLabelFilePath = ManualSpamOutputDirPath + "/test_emailId_to_label.pkl"
TrainEmailIdToLabelFilePath = ManualSpamOutputDirPath + "/train_emailId_to_label.pkl"

Top50ManualSpamWords = ManualSpamOutputDirPath + "/top_50_manual_spam_words.pkl"
Top50ManualSpamEmails = ManualSpamOutputDirPath + "/top_50_manual_spam_emails.pkl"
# ---------------------
AllUnigramsSpamOutputPath = outputDirPath + "/AllUnigramsAsFeatures"
UniTrainMatrixFilePath = AllUnigramsSpamOutputPath + "/train_matrix.txt"
UniTrainEmailIdToSnoCommaLabelFilePath = AllUnigramsSpamOutputPath + "/train_emailId_to_Sno_label.pkl"


UniTestMatrixFilePath = AllUnigramsSpamOutputPath + "/test_matrix.txt"
FeatureNameToIdMapFilePath = AllUnigramsSpamOutputPath + "/name_id_map_features.txt"
UniTestEmailIdToSnoCommaLabelFilePath = AllUnigramsSpamOutputPath + "/test_emailId_to_Sno_label.pkl"
# ---------------------
SortedTrainedTrecResultFilePath = ManualSpamOutputDirPath + "/sorted_predict_training_data.txt"
SortedTestingTrecResultFilePath = ManualSpamOutputDirPath + "/sorted_predict_testing_data.txt"
# ---------------------
UniPredictionForTestData = AllUnigramsSpamOutputPath +"/final/test_data_predicted.txt"
Top50SpamDocFilePath = AllUnigramsSpamOutputPath + "/final/top_50_span_emails.txt"

TrainedModelFilePath = AllUnigramsSpamOutputPath + "/final/model.txt"
Top50SpamTermsFilePath = AllUnigramsSpamOutputPath + "/final/top_50_spam_terms.txt"

#---------------------------------------------------------------------------------------
# INDEX_NAME = "testspam"
# TYPE_NAME = "testemail"
INDEX_NAME = "hw7spamclassifier"
TYPE_NAME = "email"
#---------------------------------------------------------------------------------------
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
#---------------------------------------------------------------------------------------
MAPPING_BODY={
    "properties": {
     "text": {
        "type": "string",
        "store": "true",
        "index": "analyzed",
        "term_vector": "with_positions_offsets_payloads",
        "analyzer": "my_english"
      },
      "label": {
        "type": "string",
        "store": "true",
        "index": "not_analyzed"
      },
     "split":{
        "type": "string",
        "store": "true",
        "index": "not_analyzed"
      },
      "name":{
        "type": "string",
        "store": "true",
        "index": "not_analyzed"
      }
    }
}
# -----------------------------------------------------
# TF details for Part I (Manual Spam Classifier)
# -----------------------------------------------------


NGRAM_FEATURE_BODY = {
    "fields": ["label", "split"],
    "query": {
        "match_phrase": {
            "text": {
                "query": "INPUT_TERM",
                "slop": -1
            }
        }
    },
    "size": 84000
}
# -----------------------------------------------------
# TF details for Part II (All Unigrams Spam Classifier)
# -----------------------------------------------------
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

REQUEST_BODY_TERMVECTOR_FOR_DOC = {
    "_id" : "EmailDocId",
    "fields" : ["split", "label", "text"],
    "offsets" : 'false',
    "payloads" : 'false',
    "positions" : 'false',
    "term_statistics" : 'false',
    "field_statistics" : 'false'
}

print len("a ".strip())