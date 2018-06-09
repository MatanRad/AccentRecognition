from keras.utils import np_utils
from keras.models import Sequential, load_model
import keras.layers.recurrent
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.normalization import BatchNormalization
from keras.layers.convolutional import Convolution1D, MaxPooling1D, Conv2D, MaxPooling2D


def LSTM(input_shape, nb_classes, counts=[64,64], dropout=0.25, optimizer='adam', loss='categorical_crossentropy'):
    model = Sequential()

    for ind, c in enumerate(counts):
        ret_seq = not (ind == len(counts)-1)

        if ind == 0:
            model.add(keras.layers.recurrent.LSTM(c, input_shape=input_shape, stateful=False, return_sequences=ret_seq))
        else:
            model.add(keras.layers.recurrent.LSTM(c, stateful=False, return_sequences=ret_seq))

    model.add(Dropout(dropout))

    # squash output onto number of classes in probability space
    model.add(Dense(nb_classes, activation='softmax'))

    model.compile(loss=loss, optimizer=optimizer, metrics=["accuracy"])

    return model


def Conv1D_2_class(input_shape, nb_classes, nb_filter=64, dropout=0.25, optimizer='rmsprop', loss='binary_crossentropy'):
    model = Sequential()

    filter_length_1 = 50
    filter_length_2 = 25

    if nb_classes !=2:
        raise Exception("Number classes must be 2!")

    model.add(Convolution1D(nb_filter=nb_filter,
                            filter_length=filter_length_1,
                            input_shape=input_shape,
                            border_mode='valid',
                            activation='relu'
                            ))
    model.add(BatchNormalization())
    model.add(Convolution1D(nb_filter=nb_filter,
                            filter_length=filter_length_2,
                            border_mode='same',
                            activation='relu'
                            ))
    model.add(BatchNormalization())
    model.add(MaxPooling1D(pool_length=2))
    model.add(Convolution1D(nb_filter=nb_filter,
                            filter_length=filter_length_2,
                            border_mode='same',
                            activation='relu'
                            ))
    model.add(BatchNormalization())
    model.add(MaxPooling1D(pool_length=2))
    model.add(Flatten())
    model.add(Dropout(dropout))
    model.add(Dense(nb_classes))
    model.add(Activation('softmax'))

    model.compile(loss=loss, optimizer=optimizer, metrics=["accuracy"])

    return model

def cifar10_net(input_shape, nb_classes, optimizer='rmsprop', loss='binary_crossentropy'):
    activ = "relu"
    model = Sequential()
    model.add(Conv2D(32, (3, 3), padding='same',
                     input_shape=input_shape))
    model.add(Activation(activ))
    model.add(Conv2D(32, (3, 3)))
    model.add(Activation(activ))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Conv2D(64, (3, 3), padding='same'))
    model.add(Activation(activ))
    model.add(Conv2D(64, (3, 3)))
    model.add(Activation(activ))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(512))
    model.add(Activation(activ))
    model.add(Dropout(0.5))
    model.add(Dense(nb_classes))
    model.add(Activation('softmax'))

    # initiate RMSprop optimizer
    opt = keras.optimizers.rmsprop(lr=0.0001, decay=1e-6)

    # Let's train the model using RMSprop
    model.compile(loss=loss,
                  optimizer=opt,
                  metrics=['accuracy'])
    return model