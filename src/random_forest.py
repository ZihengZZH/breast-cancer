import os
import numpy as np
import pandas as pd
import pickle
import datetime
import matplotlib.pyplot as plt
from smart_open import smart_open
from multiprocessing import cpu_count, Pool
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from src.utility import load_data_clinical
from src.utility import load_data_RNASeq


NO_TREES = 500
MAX_FEATURES = 0.25
CRITERION = 'entropy'
NO_JOBS = cpu_count() * 3
MODEL_PATH = './models/models_random_forest/'
MODEL_LIST_PATH = './models/models_random_forest/model_list.txt'


def save_model(forest, forest_name):
    # para forest: RF model to be saved
    # para forest_name: name of the RF model
    model_name = forest_name
    if os.path.isdir(MODEL_PATH + model_name):
        print("\nmodel %s already existed" % model_name)
    else:
        os.mkdir(MODEL_PATH + model_name)
        with smart_open(MODEL_PATH + model_name + '/model.sav', 'wb') as save_path:
            pickle.dump(forest, save_path)
        # readme file
        readme_notes = np.array(["This %s model is trained on %s" % (model_name, str(datetime.datetime.now()))])
        np.savetxt(MODEL_PATH + model_name + '/readme.txt', readme_notes, fmt="%s")
        # add model names to the list for further load
        with smart_open(MODEL_PATH + 'model_list.txt', 'a+') as f:
            f.write(MODEL_PATH + model_name + '\n')


def load_model(model_no):
    # para model_no:
    with smart_open(MODEL_LIST_PATH, 'rb', encoding='utf-8') as model_list:
        for line_no, line in enumerate(model_list):
            if line_no == model_no - 1:
                model_path = str(line).replace('\n', '')
                with smart_open(model_path + '/model.sav', 'rb') as f:
                    forest = pickle.load(f)
                break
    return forest


def draw_important_feature(forest, data):
    # para forest: RF model to draw important features
    n_features = data.shape[1]
    feature_names = list(data.columns.values)
    importances = forest.feature_importances_
    print("\nFeature ranking:")
    indices = np.argsort(importances)[::-1]
    # only output top 50 important features
    for f in range(50):
        print("%d. feature %d %s (%f)" % (f+1, indices[f], feature_names[indices[f]], importances[indices[f]]))
    

def run_random_forest(load=False, model_no=1):
    # para load: whether or not to load pre-trained model
    # para model_no: if load, which model to load
    data_RNASeq_labels = load_data_RNASeq()
    data_RNASeq_labels = data_RNASeq_labels.drop(columns=['gene'])

    data_labels = data_RNASeq_labels['label']
    data_RNASeq = data_RNASeq_labels.drop(columns=['label'])

    # train/test split 
    print("\nsplitting the training/test dataset ...")
    X_train, X_test, y_train, y_test = train_test_split(data_RNASeq, data_labels)

    if load:
        forest = load_model(model_no)
    else:
        print("\ntraining a Random Forest classifier ...")
        forest = RandomForestClassifier(n_estimators=NO_TREES, random_state=0, max_features=MAX_FEATURES, criterion=CRITERION, n_jobs=NO_JOBS)
        forest_name = "n_estimators=%s,max_features=%s,criterion=%s,n_jobs=%s" % (NO_TREES, MAX_FEATURES, CRITERION, NO_JOBS)

        forest.fit(X_train, y_train)

        print("\ntraining DONE.\n\nsaving the RF classifier ...")
        save_model(forest, forest_name)

    print("\ntesting the Random Forest classifier ...\n")
    print("Accuracy on training set: %.3f" % forest.score(X_train, y_train))
    print("Accuracy on test set: %.3f" % forest.score(X_test, y_test))


    