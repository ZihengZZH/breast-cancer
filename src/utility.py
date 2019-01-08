import numpy as np
import pandas as pd
import sys
import statistics


data_path = './dataset/'
data_path_process= './dataset_proc/'


# load TCGA-BRCA clinical data
def load_data_clinical(proc=False, test=False):
    # para proc: whether or not to load processed clinical data
    # para test: whether or not to print key aspects
    if proc:
        data_clinical = pd.read_csv(data_path_process+'20160128-BRCA-Clinical-processed.txt', sep='\t', index_col=0)
    else:
        data_clinical = pd.read_csv(data_path+'20160128-BRCA-Clinical.txt', sep="\t", header=0, index_col=0).T

    if test:
        # samples
        no_patient, no_feature = data_clinical.shape[0], data_clinical.shape[1]
        # age data
        age = data_clinical['years_to_birth'].dropna().tolist()
        age = [int(x) for x in age]
        age_median, age_min, age_max = statistics.median(age), min(age), max(age)
        # vital status data
        vital = data_clinical['vital_status'].tolist()
        living, deceased = vital.count('0'), vital.count('1')
        # gender data
        gender = data_clinical['gender'].tolist()
        male, female = gender.count('male'), gender.count('female')
        # print key aspects 
        print("#features: %d\t#patients: %d" % (no_feature, no_patient))
        print("#living: %d\t#deceased: %d" %(living, deceased))
        print("median age: %d\tage range: %d-%d" %(age_median, age_min, age_max))
        print("#male: %d\t#female: %d" %(male, female))

    return data_clinical


# load TCGA-BRCA RNASeqGene data
def load_data_RNASeq(proc=False, test=False):
    # para proc: whether or not to load processed RNASeq data
    # para test: whether or not to print key aspects
    if proc:
        data_RNASeq = pd.read_csv(data_path_process+'20160128-BRCA-RNAseqGene-processed.txt', sep='\t', index_col=0)
    else:
        data_RNASeq = pd.read_csv(data_path+'20160128-BRCA-RNAseqGene.txt', sep='\t', header=0, index_col=0).T
        # RPKM index list
        RPKM_index_lst = [x*3+2 for x in list(range(878))]
        # RPKM partition of the RNASeq
        data_RNASeq_RPKM = data_RNASeq.iloc[RPKM_index_lst]
        # save processed data 
        save_processed_data(data_RNASeq_RPKM, data_type='RNASeq')
    
    if test:
        # features (RNA gene)
        no_sample, no_feature = data_RNASeq.shape[0], data_RNASeq.shape[1]
        # print key aspects
        print("#features: %d\t#samples: %d" % (no_feature, no_sample))

    return data_RNASeq


# save processed data to file (suitable for various data types)
def save_processed_data(data, data_type=None):
    # para data: the processed data to store
    if not data_type:
        print("\nNo data types identified")
        return
    if data_type == 'clinical':
        data.to_csv(data_path_process+'20160128-BRCA-Clinical-processed.txt', sep='\t')
        print("\nProcessed Clinical data has been successfully written to file ...")
    if data_type == 'RNASeq':
        data.to_csv(data_path_process+'20160128-BRCA-RNAseqGene-processed.txt', sep='\t')
        print("\nProcessed RNASeq data has been successfully written to file ...")
    if data_type == 'RNASeq_label':
        data.to_csv(data_path_process+'20160128-BRCA-RNAseqGene-label.txt', sep='\t')
        print("\nProcessed RNASeq with labels data has been successfully written to file ...")


# label the RNASeq data with the clinical data
def label_RNASeq_data():
    print("\nLabel the RNASeq data with the vital_status in clinical data ...")
    # load data first
    data_clinical = load_data_clinical()
    data_RNASeq = load_data_RNASeq(proc=True)
    # find the RNASeq dataframe index
    index_RNASeq = data_RNASeq.index.tolist()
    index_RNASeq = [x[:12].lower() for x in index_RNASeq]
    # drop the samples in clinical copy dataframe if there is no corresponding RNASeq data
    data_clinical_copy = data_clinical.copy()
    for index_clinical, _ in data_clinical_copy.iterrows():
        if index_clinical not in index_RNASeq:
            data_clinical_copy = data_clinical_copy.drop([index_clinical])
    
    # find the clinical dataframe index
    data_clinical_copy = data_clinical_copy.sort_index()
    index_Clinical = data_clinical_copy.index.tolist()
    index_Clinical = [index.upper() for index in index_Clinical]
    # drop the samples in RNASeq copy dataframe if there is no corresponding clinical data
    data_RNASeq_copy = data_RNASeq.copy()
    data_RNASeq_copy['label'] = pd.Series(np.zeros(data_RNASeq_copy.shape[0]), index=data_RNASeq_copy.index)
    for index_RNASeq, _ in data_RNASeq_copy.iterrows():
        if index_RNASeq[:12] not in index_Clinical:
            data_RNASeq_copy = data_RNASeq_copy.drop([index_RNASeq])
        # otherwise, label the samples 
        else:
            label = data_clinical_copy.loc[index_RNASeq[:12].lower(),:]['vital_status']
            data_RNASeq_copy.loc[index_RNASeq, 'label'] = label
    
    # save the processed data for further analysis
    save_processed_data(data_clinical_copy, data_type='clinical')
    save_processed_data(data_RNASeq_copy, data_type='RNASeq_label')
    

label_RNASeq_data()