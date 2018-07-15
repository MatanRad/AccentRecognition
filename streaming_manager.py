import numpy as np
import dataset_loader as dl
from python_speech_features import mfcc
import wave
import models
import keras.models
import json


# A class for handle streamed audio data and respond with real time responses.
# It has a buffer that requires a certain amount of data to get backed up for classification to start.
# But if too much data is waiting to be handled. This data is being flushed to clear space for newer data.
class StreamingManager:

    # sr - sample rate
    # model_path - path of file of saved and trained keras model.
    # resp_function - a function that receives a string to reply to the client.
    # start_sec_thresh - how many seconds of data are needed to begin classification
    # reset_sec_thresh - how many seconds of data are needed to be backed up for a data flush to occur
    def __init__(self, sr, model_path, resp_func, start_sec_thresh=3, reset_sec_thresh=8):
        self.buff = []
        self.sr = sr
        self.start_thresh = start_sec_thresh
        self.reset_thresh = reset_sec_thresh
        self.model = keras.models.load_model(model_path)
        self.respond = resp_func

    # gets the number of seconds of data in the buffer
    def get_buff_secs(self):
        return len(self.buff) / self.sr

    # flushes the buffer
    def reset(self):
        self.buff = []

    # registers new data that just arrived into the buffer, and flushes, if needed.
    def register_data(self, data):
        self.buff += list(np.frombuffer(data, dtype=np.int16))
        if self.get_buff_secs() >= self.reset_thresh:
            self.reset()

        if self.get_buff_secs() >= self.start_thresh:
            self.run()

    # pops the self.start_thresh data required for classification, and converts into librosa format.
    def pop_usable(self):
        num_samples_buff = self.start_thresh * self.sr
        buff = np.array(self.buff[:num_samples_buff])
        del self.buff[:num_samples_buff]

        return buff.astype(np.float32)/0xFFFF

    # runs the classification task on data in buffer
    def run(self):
        buff = self.pop_usable()

        buff, sr = dl.downsample(buff, self.sr, outrate=8000)

        # divide data into chunks of sizes _chunk_ and pad as needed.
        chunk = 2400
        size = int(np.ceil(len(buff)/float(chunk))) * chunk

        buff = np.pad(buff, [0, size-buff.shape[0]], mode="constant")

        # convert to MFCC
        x = []
        for i in range(size//chunk-1):
            a = buff[int(i * chunk):int((i + 2) * chunk)]
            normed_mfcc_feat = mfcc(a, sr)
            normed_mfcc_feat = normed_mfcc_feat.T
            x.append(normed_mfcc_feat)
        x = np.array(x)
        x = x.reshape((x.shape[0], x.shape[2], x.shape[1]))

        # predict probabilities for each class using our Keras model.
        ys = self.model.predict(x)
        # take class with highest probability
        pred_class = np.argmax(ys, axis=1)
        # get count of appearances of each class
        un, counts = np.unique(pred_class, return_counts=True)
        # our answer is the class that appeared the most.
        y = un[np.argmax(counts)]

        class_probs = np.mean(ys, axis=0)

        # respond to the client with the selected accent and probabilities
        self.respond("%d;%s" % (y, json.dumps(class_probs.tolist())))
        print("%d, %s" % (y, str(counts)))
