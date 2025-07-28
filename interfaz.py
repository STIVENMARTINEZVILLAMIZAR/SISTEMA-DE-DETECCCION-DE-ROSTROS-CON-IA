import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys

# Ruta base del proyecto (ajusta si es necesario)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def ejecutar(script_name):
    path = os.path.join(BASE_DIR, script_name)
    try:
        if sys.platform.startswith('win'):
            subprocess.Popen(["python", path], shell=True)
        else:
            subprocess.Popen(["python3", path])
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo ejecutar {script_name}\n{e}")

# ---------- VENTANA PRINCIPAL ---------- #
root = tk.Tk()
root.title("Sistema de Videovigilancia con IA")
root.geometry("400x400")
root.configure(bg="#f0f0f0")

tk.Label(root, text="Menú Principal", font=("Arial", 18, "bold"), bg="#f0f0f0").pack(pady=20)

btn_registrar = tk.Button(root, text="📷 Registrar Rostro", width=25, height=2, bg="#007acc", fg="white",
                          font=("Arial", 11), command=lambda: ejecutar("registrar_rostro.py"))
btn_registrar.pack(pady=10)

btn_vigilancia = tk.Button(root, text="🛡️ Iniciar Vigilancia", width=25, height=2, bg="#28a745", fg="white",
                           font=("Arial", 11), command=lambda: ejecutar("reconocimiento.py"))
btn_vigilancia.pack(pady=10)

btn_ver = tk.Button(root, text="📁 Ver Registros", width=25, height=2, bg="#ffc107", fg="black",
                    font=("Arial", 11), command=lambda: ejecutar("visor_registros.py"))
btn_ver.pack(pady=10)

btn_salir = tk.Button(root, text="❌ Salir", width=25, height=2, bg="#dc3545", fg="white",
                      font=("Arial", 11), command=root.quit)
btn_salir.pack(pady=10)

root.mainloop()
