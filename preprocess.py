import os
import cv2
import numpy as np
from mtcnn.mtcnn import MTCNN

# Konfigurasi
INPUT_DIR = 'dataset'          # Folder dataset asli
OUTPUT_DIR = 'processed_dataset'  # Folder untuk menyimpan gambar yang sudah dipreproses
IMG_SIZE = (128, 128)          # Ukuran output wajah (lebar x tinggi)

# Inisialisasi MTCNN
detector = MTCNN()

def process_image(image_path, output_path):
    """
    Membaca gambar, mendeteksi wajah menggunakan MTCNN, 
    melakukan cropping, resizing, dan menyimpan hasilnya.
    """
    # Baca gambar menggunakan OpenCV
    image = cv2.imread(image_path)
    if image is None:
        print(f"[ERROR] Gagal membaca gambar: {image_path}")
        return

    # Konversi gambar dari BGR (OpenCV default) ke RGB
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Deteksi wajah dengan MTCNN
    results = detector.detect_faces(rgb_image)
    if not results:
        print(f"[INFO] Tidak ada wajah terdeteksi pada gambar: {image_path}")
        return

    # Ambil deteksi wajah pertama (jika terdapat lebih dari satu, Anda bisa memprosesnya sesuai kebutuhan)
    result = results[0]
    bounding_box = result['box']  # Format: [x, y, width, height]
    x, y, width, height = bounding_box

    # Pastikan koordinat tidak negatif
    x = max(0, x)
    y = max(0, y)

    # Crop wajah menggunakan bounding box
    face = rgb_image[y:y+height, x:x+width]

    # Resize gambar wajah ke ukuran yang diinginkan (misalnya, 128x128)
    face_resized = cv2.resize(face, IMG_SIZE)

    # Konversi kembali dari RGB ke BGR agar dapat disimpan dengan cv2
    face_bgr = cv2.cvtColor(face_resized, cv2.COLOR_RGB2BGR)

    # Simpan gambar yang telah diproses
    success = cv2.imwrite(output_path, face_bgr)
    if success:
        print(f"[INFO] Gambar telah diproses dan disimpan: {output_path}")
    else:
        print(f"[ERROR] Gagal menyimpan gambar: {output_path}")

def process_dataset(input_dir, output_dir):
    """
    Memproses seluruh gambar di dalam folder dataset dan menyimpannya ke folder output
    dengan struktur folder yang sama.
    """
    # Buat folder output jika belum ada
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Iterasi setiap subfolder (misalnya, folder label seperti 'aldi', 'juna', 'rudi')
    for label in os.listdir(input_dir):
        label_input_path = os.path.join(input_dir, label)
        if os.path.isdir(label_input_path):
            # Buat folder output untuk label tersebut
            label_output_path = os.path.join(output_dir, label)
            if not os.path.exists(label_output_path):
                os.makedirs(label_output_path)
            # Proses setiap gambar di folder label
            for filename in os.listdir(label_input_path):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_path = os.path.join(label_input_path, filename)
                    output_path = os.path.join(label_output_path, filename)
                    process_image(image_path, output_path)

if __name__ == '__main__':
    process_dataset(INPUT_DIR, OUTPUT_DIR)
