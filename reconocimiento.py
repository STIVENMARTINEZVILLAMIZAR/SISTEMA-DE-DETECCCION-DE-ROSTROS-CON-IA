# reconocimiento.py
import face_recognition
import cv2
import os

# Cargar rostros conocidos
known_face_encodings = []
known_face_names = []

ruta_rostros = "rostros"

for archivo in os.listdir(ruta_rostros):
    imagen = face_recognition.load_image_file(os.path.join(ruta_rostros, archivo))
    encoding = face_recognition.face_encodings(imagen)
    
    if encoding:
        known_face_encodings.append(encoding[0])
        nombre = os.path.splitext(archivo)[0]
        known_face_names.append(nombre)

# Iniciar la cámara
cap = cv2.VideoCapture(0)

print("[INFO] Reconocimiento facial activo. Presiona 'q' para salir.")

while True:
    ret, frame = cap.read()
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Buscar todos los rostros y codificaciones en la imagen actual
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Desconocido"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

        # Escalar coordenadas a tamaño original
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Dibujar rectángulo y nombre
        color = (0, 0, 255) if "sospechoso" in name.lower() else (0, 255, 0)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    # Mostrar video
    cv2.imshow('Reconocimiento Facial', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
