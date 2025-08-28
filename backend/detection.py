# backend/detection.py
import cv2, threading, time, json
from db import SessionLocal
from models import Evento, Persona, Empresa
from face_recognition import detect_faces, crop_face, compute_embedding, find_best_match
from config import CAMERA_SOURCE, SIMILARITY_THRESHOLD, DEFAULT_WHATSAPP_NUMBER
from notify_whatsapp import send_whatsapp_message
from notify_whatsapp import init_driver
from sqlalchemy import select

class CameraWorker:
    def __init__(self, source=0, camera_name='CAM1', empresa_id=None):
        try:
            self.source = int(source)
        except Exception:
            self.source = source
        self.camera_name = camera_name
        self.frame = None
        self.lock = threading.Lock()
        self.running = False
        self.empresa_id = empresa_id

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _loop(self):
        cap = cv2.VideoCapture(self.source)
        if not cap.isOpened():
            print("[CameraWorker] No se pudo abrir la cámara:", self.source)
            return

        # Inicializar driver WA en hilo aparte (no bloqueante)
        try:
            init_driver()  # abrirá navegador y pedir QR si es necesario
        except Exception as e:
            print("No se pudo inicializar WhatsApp driver:", e)

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
                    label = 'Desconocido'
                    persona_id = None
                    sim = None
                    es_desconocido = True

                    if emb is not None and self.empresa_id:
                        persona_id, sim = find_best_match(self.empresa_id, emb)
                        if persona_id and sim is not None and sim >= SIMILARITY_THRESHOLD:
                            es_desconocido = False
                            p = session.get(Persona, persona_id)
                            label = p.nombre if p else f'ID:{persona_id}'
                        else:
                            persona_id = None
                            label = 'Desconocido'

                    # snapshot bytes
                    ret, buf = cv2.imencode('.jpg', face_img)
                    snap_bytes = buf.tobytes() if ret else None

                    # Guardar evento
                    ev = Evento(persona_id=persona_id, label=label, es_desconocido=es_desconocido,
                                similarity=sim, camera=self.camera_name, snapshot=snap_bytes,
                                empresa_id=self.empresa_id)
                    session.add(ev)
                    session.commit()

                    # Enviar notificación WhatsApp si desconocido
                    if es_desconocido:
                        # obtener número de la empresa (si tiene)
                        emp = session.get(Empresa, self.empresa_id) if self.empresa_id else None
                        phone = emp.notify_phone if emp and emp.notify_phone else DEFAULT_WHATSAPP_NUMBER
                        if phone:
                            text = f"ALERTA: Rostro desconocido detectado en {self.camera_name} para empresa {self.empresa_id}"
                            # enviar en hilo para no bloquear la cámara
                            threading.Thread(target=send_whatsapp_message, args=(phone, text, snap_bytes), daemon=True).start()

                    # dibujar
                    color = (0, 255, 0) if not es_desconocido else (0, 0, 255)
                    cv2.rectangle(draw, (x, y), (x+w, y+h), color, 2)
                    cv2.putText(draw, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            except Exception as e:
                print("Error detection loop:", e)
            finally:
                session.close()

            with self.lock:
                self.frame = draw
        cap.release()

    def get_frame(self):
        with self.lock:
            return None if self.frame is None else self.frame.copy()

# mjpeg generator para /stream
def mjpeg_generator(worker):
    import time
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
