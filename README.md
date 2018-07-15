# Accent Recognition

## Introduction

Our bachelor's degree final project.
A simple accent recognition system using neural networks and the Keras (and TF) foundations

## Requirements
This repository is built on top of Python 3.6 and uses _Keras_ and _TensorFlow_ as the foundations for all machine learning operations.
_Scipy_ and _SKlearn_ are also used for various data preprocessing techniques.

All modules required by this repository are listed in the [requirements.txt](https://github.com/MatanRad/AccentRecognition/blob/master/requirements.txt) file in this repository.
The modules can be automatically installed using _pip_ and _bash/batch_ as follows:
~~~~~bash
pip install -r requirements.txt
~~~~~

##### Please note that if GPU access is available, it is recommended to install the GPU version of tensorflow: https://www.tensorflow.org/install/

## General Overview
The data used for this dataset is the [Speech Accent Archive](http://accent.gmu.edu/) (can also be found at [Kaggle](https://www.kaggle.com/rtatman/speech-accent-archive)).

In order to use the data with the provided code, all .mp3 file need to be converted into .wav files.
This can be done using [FFmpeg](https://www.ffmpeg.org/) and the following bash/batch scripts:

**_Bash:_**
~~~~~~~~bash
    for i in *.mp3; do ffmpeg -i "$i" -vn -acodec pcm_s16le -ac 1 -ar 16000 -ac 1 -f wav "wav/${i%.*}.wav"; done
~~~~~~~~

**_Batch:_**
~~~~~~~~bat
FOR /F "tokens=*" %G IN ('dir /b *.mp3') DO ffmpeg -i "%G" -vn -acodec pcm_s16le -ac 1 -ar 16000 -ac 1 -f wav "wav/%~nG.wav"
~~~~~~~~

After data has been converted to .wav format our code is ready to be executed.
###### All Parameters (such as file paths) in our code will generally be at the top.

## How To Run
In order to train a network on accents, run _main.py_ after setting the correct parameters and paths in it. (Add _speakers_all.csv_ from the dataset to the same folder as this file).
To configure which accents to use, edit the "_countires_" parameter and the "*native_langs*" so that each country is a name of a country as in the original dataset. And each item in *native_langs* is an array of native languages we want to use.

For example, for training on American vs Mandarin and Cantonese (combined) we can do:
~~~~python
countries = ["usa", "china"]
native_langs = ["english", "mandarin", "cantonese"]
~~~~

The main file will save the network after it's finished training.
In order to run the live website demo, modify all required values in _server.py_ (e.g. port number, path to network file, etc.) and run it.
Then connect to:

```url
    http://localhost:<port number>/
```

## Files
The files and their uses are listed here:
- _dataset_loader.py_ - Module for loading the data from file and pre-proccessing it. Contains the code to load files and put them in our required formats.
- _main.py_ - Our main file for training a neural net on the data. This code should be easy to modify for other models and datasets.
- _models.py_ - Contains a few examples of various NN models.
- _server.py_ - The server for running our live demo website.
- _streaming_manager.py_ - Class for handling live audio data from live website demo.

Each of these files contains its own comments on what each code-section in that file does.