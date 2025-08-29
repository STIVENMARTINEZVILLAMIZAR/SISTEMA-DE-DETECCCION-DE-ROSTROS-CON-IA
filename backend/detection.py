import cv2, threading, time
from db import SessionLocal
from models import Evento, Persona
from face_recognition import detect_faces, crop_face, compute_embedding, find_best_match
from config import SIMILARITY_THRESHOLD

class CameraWorker:
    def __init__(self, source=0, camera_name='CAM', empresa_id=None):
        self.source = source
        self.camera_name = camera_name
        self.empresa_id = empresa_id
        self.frame = None
        self.lock = threading.Lock()
        self.running = False

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False

    def _loop(self):
        cap = cv2.VideoCapture(self.source, cv2.CAP_DSHOW)  # CAP_DSHOW evita muchos errores en Windows
        if not cap.isOpened():
            print(f"[CameraWorker] No se pudo abrir la cámara {self.source}")
            return

        while self.running:
            ok, frame = cap.read()
            if not ok:
                time.sleep(0.1)
                continue

            draw = frame.copy()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detect_faces(gray)

            session = SessionLocal()
            try:
                for (x, y, w, h) in faces:
                    face_img = crop_face(frame, (x, y, w, h))
                    emb = compute_embedding(face_img)

                    label = "Desconocido"
                    persona_id = None
                    es_desconocido = True

                    if emb is not None and self.empresa_id:
                        persona_id, sim = find_best_match(self.empresa_id, emb)
                        if persona_id and sim >= SIMILARITY_THRESHOLD:
                            es_desconocido = False
                            p = session.get(Persona, persona_id)
                            label = p.nombre if p else f"ID:{persona_id}"

                    # guardar evento
                    ev = Evento(
                        persona_id=persona_id,
                        label=label,
                        es_desconocido=es_desconocido,
                        camera=self.camera_name,
                        empresa_id=self.empresa_id
                    )
                    session.add(ev)
                    session.commit()

                    color = (0, 255, 0) if not es_desconocido else (0, 0, 255)
                    cv2.rectangle(draw, (x, y), (x+w, y+h), color, 2)
                    cv2.putText(draw, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            finally:
                session.close()

            with self.lock:
                self.frame = draw

        cap.release()

    def get_frame(self):
        with self.lock:
            return None if self.frame is None else self.frame.copy()

def mjpeg_generator(worker):
    while True:
        frame = worker.get_frame()
        if frame is None:
            time.sleep(0.05)
            continue
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
