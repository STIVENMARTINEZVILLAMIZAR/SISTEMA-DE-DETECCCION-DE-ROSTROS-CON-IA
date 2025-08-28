# 🧑‍💻 Sistema de Detección de Rostros con IA

Este proyecto implementa un sistema de **detección y reconocimiento facial** utilizando **Flask**, **OpenCV**, **DeepFace** y **MySQL**.  
El sistema permite registrar personas, almacenar sus embeddings faciales y verificar accesos en tiempo real mediante cámara web.  

---

## 📌 Características
- Detección facial en tiempo real con **OpenCV**.  
- Reconocimiento facial mediante **DeepFace** y modelo `Facenet512`.  
- Persistencia en **MySQL** (almacenamiento de usuarios, eventos y embeddings).  
- Interfaz web desarrollada en **Flask** con **Bootstrap**.  
- Gestión de sesiones con **Flask-Session**.  
- Envío de notificaciones vía **WhatsApp** (opcional).  

---

## 🗂️ Estructura del Proyecto

SISTEMA-DE-DETECCCION-DE-ROSTROS-CON-IA/
<br>
│── backend/
<br>
│ ├── init.py
<br>
│ ├── app.py
<br>
│ ├── config.py
<br>
│ ├── auth.py
<br>
│ ├── detection.py
<br>
│ ├── face_recognition.py
<br>
│ ├── models.py
<br>
│ ├── routes_people.py
<br>
│ ├── routes_events.py
<br>
│ └── notify_whatsapp.py
│<br>
│── database/
<br>
│ └── schema.sql
│<br>
│── static/
<br>
│ ├── css/
<br>
│ └── img/
│<br>
│── templates/
<br>
│ ├── index.html
<br>
│ ├── login.html
<br>
│ ├── dashboard.html
<br>
│ └── register.html
│<br>
│── venv/ # Entorno virtual (ignorado en git)
<br>
│── requirements.txt # Dependencias del proyecto
<br>
│── README.md # Documentación
<br>
│── .gitignore # Archivos a ignorar en git
<br>

---
 **AUTORES**

- STIVEN MARTINEZ VILLAMIZAR
- ELVER BELTRAN ROJAS
---

## ⚙️ Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/sistema-detector-rostros.git
cd sistema-detector-rostros



