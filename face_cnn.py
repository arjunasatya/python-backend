import os
import cv2
import numpy as np
import tensorflow as tf
from mtcnn.mtcnn import MTCNN

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'cnn_face_model.h5')
model = tf.keras.models.load_model(MODEL_PATH)

# label_map menyesuaikan class_indices dari training
label_map = {
    0: "aldi",
    1: "devan",
    2: "juna",
    3: "rudi",
}

IMG_SIZE = (128, 128)

# Inisialisasi MTCNN
detector = MTCNN()

def detect_and_recognize_faces(file_bytes):
    """
    Mendeteksi wajah menggunakan MTCNN, kemudian memproses wajah untuk pengenalan dengan CNN.
    Mengembalikan dictionary:
    {
      "recognized": True/False,
      "box": [x, y, width, height] (bounding box),
      "label": "predicted_label"
    }
    """
    # Ubah bytes menjadi array NumPy, lalu decode ke gambar menggunakan OpenCV
    img_array = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if img is None:
        return {"recognized": False, "box": None, "label": "Invalid image"}

    # Konversi BGR ke RGB (MTCNN memerlukan RGB)
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Deteksi wajah menggunakan MTCNN
    results = detector.detect_faces(rgb_img)
    if len(results) == 0:
        return {"recognized": False, "box": None, "label": "No face detected"}

    # Ambil deteksi wajah pertama
    result = results[0]
    bounding_box = result['box']  # format: [x, y, width, height]
    x, y, width, height = bounding_box
    # Pastikan koordinat tidak negatif
    x = max(0, x)
    y = max(0, y)

    # Crop area wajah
    face = rgb_img[y:y+height, x:x+width]
    # Resize ke ukuran input model
    face_resized = cv2.resize(face, IMG_SIZE)
    # Normalisasi gambar (skala 0-1)
    face_normalized = face_resized.astype('float32') / 255.0
    # Bentuk input: (1, 128, 128, 3)
    face_input = np.expand_dims(face_normalized, axis=0)

    # Prediksi dengan model CNN
    preds = model.predict(face_input)
    idx = np.argmax(preds[0])
    predicted_label = label_map.get(idx, "unknown")

    # Di sini, kita kembalikan recognized sebagai True
    # Dan perbandingan dengan username dapat dilakukan di endpoint Flask
    return {
        "recognized": True,
        "box": bounding_box,
        "label": predicted_label
    }