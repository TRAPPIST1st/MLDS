from keras.datasets import mnist
import matplotlib.pyplot as plt
from keras import  utils
from keras.models import Sequential
from keras.layers import Dense
import numpy as np

(X_train, y_train), (X_test, y_test) = mnist.load_data()
 
print('Training data shape : ', X_train.shape, y_train.shape)
print('Testing data shape : ', X_test.shape, y_test.shape)
 
plt.imshow(X_train[9], cmap= plt.get_cmap('gray'))
 
print(X_train[9])
 
num_train_images = X_train.shape[0]
num_test_images = X_test.shape[0]
image_height = X_train.shape[1]
image_width = X_train.shape[2]
print(num_train_images, image_height, image_width, image_height*image_width)
X_train_reshape = X_train.reshape(num_train_images, image_height*image_width).astype('float32')
print(X_train_reshape.shape)
X_test_reshape = X_test.reshape(num_test_images, image_height*image_width).astype('float32')
print(X_test_reshape.shape)
 
X_train_reshape[9]

X_train_normalize = X_train_reshape/255
X_test_normalize = X_test_reshape/255
print(X_train_normalize[9])

print(y_train[9])

y_train_onehot = utils.to_categorical(y_train)
y_test_onehot = utils.to_categorical(y_test)
print(y_train_onehot[9])
print(y_train_onehot.shape)
 
model = Sequential()
model.add(Dense(700, input_dim=image_height*image_width, activation='relu'))
model.add(Dense(10, activation='softmax'))
print(model.summary())


EPOCHS = 20
 
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
 
history = model.fit(X_train_normalize, y_train_onehot, validation_data=(X_test_normalize, y_test_onehot), epochs=EPOCHS, batch_size=250, verbose=2)

def plot (h):
    LOSS = 0; ACCURACY = 1
    training = np.zeros((2,EPOCHS))
    testing = np.zeros((2,EPOCHS))
    training[LOSS] = h.history['loss']
    testing[LOSS] = h.history['val_loss']
    training[ACCURACY] = h.history['accuracy']
    testing[ACCURACY] = h.history['val_accuracy']
   
    epochs = range(1, EPOCHS+1)
    fig, axs = plt.subplots(1,2, figsize=(15,5))
    for i, label in zip((LOSS, ACCURACY), ('loss', 'accuracy')):
        axs[i].plot(epochs, training[i], 'b-', label='Training '+label)
        axs[i].plot(epochs, testing[i], 'y-', label='Testing '+label)
        axs[i].set_title('Training and Testing '+label)
        axs[i].set_xlabel('Epochs')
        axs[i].set_ylabel(label)
        axs[i].legend()
    plt.show()
plot(history)

print(X_test_normalize[1040].shape)
plt.imshow(X_test[1040], cmap= plt.get_cmap('gray'))
np.round(model.predict(X_test_normalize[[1040]]))