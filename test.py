import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Reshape, LSTM, Bidirectional, Dense, Lambda
from tensorflow.keras.models import Model
from sklearn.model_selection import train_test_split

# Parameters
img_width, img_height = 128, 64
num_classes = len("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") + 1  # 36 characters + 1 for blank (CTC)

# Character dictionary
char_list = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

# Function to map characters to labels
def encode_label(label):
    return [char_list.index(ch) for ch in label]

# Preprocess and load images
def load_images_and_labels(directory):
    images = []
    labels = []
    for filename in os.listdir(directory):
        if filename.endswith(".png"):
            img_path = os.path.join(directory, filename)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            img = cv2.resize(img, (img_width, img_height))
            img = img / 255.0  # Normalize
            images.append(img)
            label = filename.split('.')[0]  # Assuming label is part of filename
            labels.append(encode_label(label))
    return np.array(images), labels

yellow_images, yellow_labels = load_images_and_labels('yellowplate')
white_images, white_labels = load_images_and_labels('whiteplate')

# Combine images and labels
images = np.concatenate([yellow_images, white_images])
labels = yellow_labels + white_labels

# Split into training and validation sets
X_train, X_test, y_train, y_test = train_test_split(images, labels, test_size=0.2, random_state=42)

# Input shape for the model
input_shape = (img_height, img_width, 1)

# Define the CTC loss function
def ctc_loss_lambda_func(args):
    y_pred, labels, input_length, label_length = args
    return tf.keras.backend.ctc_batch_cost(labels, y_pred, input_length, label_length)

# Build the model
inputs = Input(shape=input_shape)

# CNN layers for feature extraction
x = Conv2D(32, (3, 3), activation='relu', padding='same')(inputs)
x = MaxPooling2D(pool_size=(2, 2))(x)
x = Conv2D(64, (3, 3), activation='relu', padding='same')(x)
x = MaxPooling2D(pool_size=(2, 2))(x)

# Reshape the CNN output to feed into LSTM
new_shape = ((img_width // 4), (img_height // 4) * 64)
x = Reshape(target_shape=new_shape)(x)

# LSTM layers for sequence learning
x = Bidirectional(LSTM(128, return_sequences=True))(x)
x = Bidirectional(LSTM(128, return_sequences=True))(x)

# Fully connected layer to classify each timestep into a character
x = Dense(num_classes, activation='softmax')(x)

# Define labels, input lengths, and label lengths for CTC loss
labels = Input(name='the_labels', shape=[None], dtype='float32')
input_length = Input(name='input_length', shape=[1], dtype='int64')
label_length = Input(name='label_length', shape=[1], dtype='int64')

# CTC loss layer
ctc_loss = Lambda(ctc_loss_lambda_func, output_shape=(1,), name='ctc')([x, labels, input_length, label_length])

# Define the model
model = Model(inputs=[inputs, labels, input_length, label_length], outputs=ctc_loss)

# Compile the model with CTC loss
# Compile the model with a dummy loss, as the CTC loss is already computed in the Lambda layer
model.compile(optimizer='adam', loss={'ctc': lambda y_true, y_pred: y_pred})


# Show the model summary
model.summary()

# Train the model
# Prepare the inputs and labels for CTC loss function
y_train_padded = tf.keras.preprocessing.sequence.pad_sequences(y_train, maxlen=10, padding='post')
train_input_length = np.ones((len(X_train), 1)) * (img_width // 4)
train_label_length = np.array([len(label) for label in y_train]).reshape(-1, 1)

# Fit the model (you can add validation_data similarly)
model.fit(x=[X_train, y_train_padded, train_input_length, train_label_length],
          y=np.zeros(len(X_train)), epochs=10, batch_size=32)

# Save the model
model.save('license_plate_model.h5')

# Testing with new image
def predict_plate(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (img_width, img_height))
    img = img / 255.0
    img = np.expand_dims(img, axis=[0, -1])  # Add batch and channel dimensions
    
    # Predict
    prediction = model.predict([img, np.ones((1, 1)) * (img_width // 4)])
    
    # Decode the prediction to get the license plate
    decoded = K.ctc_decode(prediction, input_length=np.ones((1,)) * (img_width // 4))[0][0]
    out = tf.keras.backend.get_value(decoded)
    
    predicted_plate = ''.join([char_list[int(p)] for p in out[0]])
    return predicted_plate

# Example usage:
new_image_path = 'img/car_img.jpg'
predicted_label = predict_plate(new_image_path)
print(f"Predicted license plate: {predicted_label}")
