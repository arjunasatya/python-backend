import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
import os

# Direktori dataset (pastikan dataset sudah berisi gambar wajah yang telah di-crop dan diresize)
DATASET_DIR = 'processed_dataset'  # Struktur folder: dataset/aldi, dataset/juna, dataset/rudi
IMG_SIZE = (128, 128)
BATCH_SIZE = 16
EPOCHS = 20

datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,  # 20% data untuk validasi
    rotation_range=10,
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=True
)

train_gen = datagen.flow_from_directory(
    DATASET_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training'
)

val_gen = datagen.flow_from_directory(
    DATASET_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation'
)

num_classes = train_gen.num_classes
print("Class indices:", train_gen.class_indices)  # Misalnya, {'aldi':0, 'juna':1, 'rudi':2}

model = Sequential([
    Conv2D(32, (3,3), activation='relu', input_shape=(IMG_SIZE[0], IMG_SIZE[1], 3)),
    MaxPooling2D((2,2)),
    Conv2D(64, (3,3), activation='relu'),
    MaxPooling2D((2,2)),
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(num_classes, activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.fit(
    train_gen,
    epochs=EPOCHS,
    validation_data=val_gen
)

model.save('cnn_face_model.h5')
print("Model berhasil disimpan ke cnn_face_model.h5")
