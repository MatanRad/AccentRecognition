import numpy as np
import dataset_loader as dl
from python_speech_features import mfcc
import wave
import models
import keras.models

class StreamingManager:
    def __init__(self, sr, model_path, start_sec_thresh=3, reset_sec_thresh=8):
        self.buff = []
        self.sr = sr
        self.start_thresh = start_sec_thresh
        self.reset_thresh = reset_sec_thresh
        self.model = keras.models.load_model(model_path)

    def get_buff_secs(self):
        return len(self.buff) / self.sr

    def reset(self):
        self.buff = []

    def register_data(self, data):
        self.buff += list(np.frombuffer(data, dtype=np.int16))
        if self.get_buff_secs() >= self.reset_thresh:
            self.reset()

        if self.get_buff_secs() >= self.start_thresh:
            self.run()

    def pop_usable(self):
        num_samples_buff = self.start_thresh * self.sr
        buff = np.array(self.buff[:num_samples_buff])
        del self.buff[:num_samples_buff]

        return buff.astype(np.float32)/0xFFFF

    def run(self):
        buff = self.pop_usable()

        buff, sr = dl.downsample(buff, self.sr, outrate=8000)

        size = int(np.ceil(len(buff)/2400.0)) * 2400

        buff = np.pad(buff, [0, size-buff.shape[0]], mode="constant")
        chunk = 2400

        x = []
        for i in range(size//chunk-1):
            a = buff[int(i * chunk):int((i + 2) * chunk)]
            normed_mfcc_feat = mfcc(a, sr)
            normed_mfcc_feat = normed_mfcc_feat.T
            x.append(normed_mfcc_feat)
        x = np.array(x)
        x = x.reshape((x.shape[0], x.shape[2], x.shape[1]))

        print("didn't crash :)")
