import os
import cv2
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator

yellowplates_dir = 'yellowplate'
whiteplates_dir = 'whiteplate'

def load_images_and_labels(directory):
    images = []
    labels = []
    for filename in os.listdir(directory):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            img_path = os.path.join(directory, filename)
            image = cv2.imread(img_path)
            image = cv2.resize(image, (128, 64))  # Resize to a standard size
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
            images.append(image)
            labels.append(filename.split('.')[0])
    return np.array(images), np.array(labels)

yellow_images, yellow_labels = load_images_and_labels(yellowplates_dir)
white_images, white_labels = load_images_and_labels(whiteplates_dir)

images = np.concatenate((yellow_images, white_images), axis=0)
labels = np.concatenate((yellow_labels, white_labels), axis=0)

images = images / 255.0  # Normalize to 0-1

# Convert labels into one-hot encoding
char_set = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
num_classes = len(char_set)

# Map each character in the label to an integer
def label_to_onehot(label, max_length=7):
    onehot = np.zeros((max_length, num_classes))
    for i, char in enumerate(label):
        if char in char_set:
            index = char_set.index(char)
            onehot[i, index] = 1
    return onehot

onehot_labels = np.array([label_to_onehot(label) for label in labels])

X_train, X_test, y_train, y_test = train_test_split(images, onehot_labels, test_size=0.2, random_state=42)

# Build the CNN model
def build_model():
    model = models.Sequential()
    model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=(64, 128, 1)))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(64, (3, 3), activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(128, (3, 3), activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Flatten())
    model.add(layers.Dense(128, activation='relu'))
    model.add(layers.Dropout(0.5))
    
    # Output layer
    model.add(layers.Dense(7 * num_classes))
    model.add(layers.Reshape((7, num_classes)))
    model.add(layers.Softmax(axis=-1))

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

model = build_model()

# Image data generator for augmentation
datagen = ImageDataGenerator(
    rotation_range=10,
    width_shift_range=0.1,
    height_shift_range=0.1,
    shear_range=0.1,
    zoom_range=0.1,
    horizontal_flip=False
)

X_train = X_train.reshape(-1, 64, 128, 1)
X_test = X_test.reshape(-1, 64, 128, 1)

# Train the model
history = model.fit(datagen.flow(X_train, y_train, batch_size=32),
                    validation_data=(X_test, y_test),
                    epochs=20,
                    steps_per_epoch=len(X_train) // 32)

# Evaluate the model
test_loss, test_acc = model.evaluate(X_test, y_test)
print(f'Test accuracy: {test_acc}')

model.save('number_plate_cnn_model.keras')

loaded_model = tf.keras.models.load_model('number_plate_cnn_model.keras')

def predict_number_plate(model, image_path):
    # Load and preprocess the image
    image = cv2.imread(image_path)
    image = cv2.resize(image, (128, 64))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = image / 255.0  # Normalize
    image = image.reshape(1, 64, 128, 1)
    
    prediction = model.predict(image)
    
    # Convert the one-hot encoded output to characters
    plate = ''
    for i in range(7):
        char_index = np.argmax(prediction[0][i])
        plate += char_set[char_index]
    
    return plate

# Test the loaded model on a new image
new_image_path = 'img/detected_number_plate.jpg'
predicted_plate = predict_number_plate(loaded_model, new_image_path)
print(f'Predicted number plate: {predicted_plate}')
