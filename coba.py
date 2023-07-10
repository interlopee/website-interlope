from re import DEBUG, sub
from app import db, Pasien
import cv2
from werkzeug.utils import secure_filename, send_from_directory
import os
import subprocess

# Inisialisasi kamera
cap = cv2.VideoCapture(0)

# Baca setiap frame dari kamera
while True:
    ret, frame = cap.read()

    # Tampilkan frame
    cv2.imshow('frame', frame)

    # Jika tombol 'q' ditekan, keluar dari loop
    key = cv2.waitKey(1)
    if key == ord(' '):
        cv2.imwrite('Hasil Gambar/image.jpg', frame)
        break

# Tutup kamera dan jendela
cap.release()
cv2.destroyAllWindows()


subprocess.run(['python', 'detect.py', '--weights', '416_batch8.pt', '--imgsz', '416', '--source', 'Hasil Gambar/image.jpg'])

img = cv2.imread('Hasil Gambar/image.jpg')
with open('Hasil Gambar/image.jpg', 'rb') as f:
    hasil_pemeriksaan = f.read()
    
id_pasien = 1
pasien = Pasien.query.filter_by(id=id_pasien).first()
pasien.hasil_pemeriksaan = hasil_pemeriksaan
db.session.commit()

