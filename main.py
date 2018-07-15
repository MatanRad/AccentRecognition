import dataset_loader as dl
import models
import numpy as np
import keras.utils
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

def add_one_to_shape(x):
    shape = list(x.shape)
    shape.append(1)
    shape = tuple(shape)
    return x.reshape(shape)

# load our dataset and pre-process
countries = ["usa", "saudi arabia"]
native_langs = ["english", "arabic"]
x, y = dl.load_dataset_file("us_sa_100.pickle", "./wav", countries, native_langs, sr=8000, num_splits=100, num_secs=30,
                     equal_labels=True)
y = np.array(y)

# split our data into train and test sets.
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25)

# print sets sizes
print("Num Train: %d" % x_train.shape[0])
print("Num Test: %d" % x_test.shape[0])

# calc num classes
num_classes = np.unique(y_train).shape[0]

# convert labels into one-hot labels
y_train_hot = keras.utils.to_categorical(y_train, num_classes)
y_test_hot = keras.utils.to_categorical(y_test, num_classes)

# define our model
# model = models.LSTM((59, 13), 2)
model = models.Conv1D_2_class((59, 13), 2)

# train our model.
model.fit(x_train, y_train_hot, epochs=30, batch_size=512, validation_data=(x_test, y_test_hot))
# save model
model.save("us_ar.h5")

# evaluate and print results on test set
print(model.evaluate(x_test, y_test_hot))

# generate classification report for classes.
y_pred = model.predict_classes(x_test)
print(classification_report(y_test, y_pred))
