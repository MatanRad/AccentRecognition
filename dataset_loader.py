import sklearn
import numpy as np
import os
import csv
import librosa
import _pickle as pickle
from python_speech_features import mfcc


def downsample(sig, rate, outrate=8000):
    down_sig = librosa.core.resample(sig, rate, outrate, scale=True)
    down_sig = np.ceil(down_sig * np.iinfo(np.int16).max)

    return down_sig, outrate

def load_and_downsample(filename, outrate=8000, inrate=16000):
    (sig, rate) = librosa.load(filename, mono=True, sr=inrate)
    return downsample(sig, rate, outrate)

def get_standard_length(sig, n_samps=240000, sr=8000):
    normed_sig = librosa.util.fix_length(sig, int(n_samps))
    normed_sig = (normed_sig - np.mean(normed_sig)) / np.std(normed_sig)
    return normed_sig

# change total number of samps for downsampled file to n_samps by trimming or zero-padding and standardize them
def load_standard_length(filename, n_samps=240000, sr=8000):
    down_sig, rate = load_and_downsample(filename, outrate=sr)
    return get_standard_length(down_sig, n_samps, sr)

def get_files_country_dict(countries, native_langs):
    files = {}

    with open("speakers_all.csv", "r") as f:
        reader = csv.reader(f)
        header = next(reader)

        country_i = header.index("country")
        filename_i = header.index("filename")
        native_i = header.index("native_language")

        for row in reader:
            if row[country_i] in countries and row[native_i] in native_langs:
                files[row[filename_i] + ".wav"] = countries.index(row[country_i])
    return files

# for input wav file outputs (13, 2999) mfcc np array
def make_normed_split_mfcc(folder, countries, native_langs, sr=8000, num_splits=5, num_secs=30, equal_labels=False):
    lst = []
    y = []

    countries_dict = get_files_country_dict(countries, native_langs)

    #get count files per countries
    counts = [0 for _ in countries]
    for filename in os.listdir(folder):
        if filename.endswith('wav'):
            if filename in countries_dict.keys():
                counts[countries_dict[filename]] += 1

    count_added = [0 for _ in countries] #number of items added for each country
    for filename in os.listdir(folder):
        if filename.endswith('wav'):
            if not (filename in countries_dict.keys()):
                continue

            if equal_labels and count_added[countries_dict[filename]] >= np.min(counts):
                continue

            count_added[countries_dict[filename]] += 1
            print(filename)
            normed_sig = load_standard_length(os.path.join(folder, filename), sr=sr, n_samps=num_secs*sr)

            chunk = normed_sig.shape[0] / num_splits
            for i in range(num_splits - 1):
                a = normed_sig[int(i * chunk):int((i + 2) * chunk)]
                normed_mfcc_feat = mfcc(a, sr)
                normed_mfcc_feat = normed_mfcc_feat.T
                lst.append(normed_mfcc_feat)
                y.append(countries_dict[filename])

    y = np.array(y)
    lst = np.array(lst)
    lst = lst.reshape((lst.shape[0], lst.shape[2], lst.shape[1]))

    return lst, y

def load_dataset_file(file, folder, countries, native_langs, sr=8000, num_splits=5, num_secs=30, equal_labels=False):
    if os.path.isfile(file):
        with open(file, "rb") as f:
            return pickle.load(f)
    else:
        x, y = make_normed_split_mfcc(folder, countries, native_langs, sr=sr, num_splits=num_splits, num_secs=num_secs,
                                      equal_labels=equal_labels)
        with open(file, "wb") as f:
            pickle.dump((x,y), f)
        return x, y

def min_max_norm(x):
    min = np.min(x)
    max = np.max(x)
    return (x-min)/(max-min)