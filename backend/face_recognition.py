# backend/face_recognition.py
import cv2
import numpy as np
import json
from deepface import DeepFace
from config import EMBEDDING_MODEL, SIMILARITY_THRESHOLD
from db import SessionLocal
from models import FaceEmbedding, Persona
from sqlalchemy import select

_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detect_faces(gray_frame, min_size=80):
    return _cascade.detectMultiScale(gray_frame, scaleFactor=1.2, minNeighbors=5, minSize=(min_size, min_size))

def crop_face(frame, box, margin=10):
    x, y, w, h = box
    h_, w_ = frame.shape[:2]
    x0 = max(0, x - margin)
    y0 = max(0, y - margin)
    x1 = min(w_, x + w + margin)
    y1 = min(h_, y + h + margin)
    return frame[y0:y1, x0:x1]

def compute_embedding(bgr_face):
    rgb = cv2.cvtColor(bgr_face, cv2.COLOR_BGR2RGB)
    try:
        rep = DeepFace.represent(rgb, model_name=EMBEDDING_MODEL, enforce_detection=False)
        if not rep:
            return None
        return rep[0]['embedding']
    except Exception as e:
        print("Error computing embedding:", e)
        return None

def cosine_similarity(a, b):
    a = np.array(a, dtype=np.float32)
    b = np.array(b, dtype=np.float32)
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)

def find_best_match(empresa_id, embedding):
    session = SessionLocal()
    try:
        stmt = select(FaceEmbedding).join(Persona, FaceEmbedding.person_id == Persona.id).where(Persona.empresa_id == empresa_id)
        embeddings = session.execute(stmt).scalars().all()
        best = (None, 0.0)
        for fe in embeddings:
            try:
                emb_db = json.loads(fe.embedding)
            except Exception:
                continue
            sim = cosine_similarity(embedding, emb_db)
            if sim > best[1]:
                best = (fe.person_id, sim)
        return best
    finally:
        session.close()
