# backend/notify_whatsapp.py
import os, time, tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse

_driver = None
_profile_dir = os.path.abspath("./wa_profile")  # carpeta donde se guarda sesión

def init_driver(profile_dir=None, visible=True):
    global _driver, _profile_dir
    if profile_dir:
        _profile_dir = profile_dir
    if _driver is not None:
        return _driver

    options = Options()
    # no usar headless (WhatsApp Web bloquea headless)
    if not visible:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
    # persistir sesión
    os.makedirs(_profile_dir, exist_ok=True)
    options.add_argument(f"--user-data-dir={_profile_dir}")
    options.add_argument("--profile-directory=Default")
    # otras opciones
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # iniciar driver (webdriver-manager descarga chromedriver)
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.set_window_size(1024, 800)
    driver.get("https://web.whatsapp.com")
    # esperar a que la página cargue; si es primera vez, el usuario debe escanear QR
    try:
        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.ID, "pane-side"))
        )
    except Exception:
        # puede fallar si el selector cambia; al menos esperar unos segundos
        time.sleep(10)
    _driver = driver
    return _driver

def send_whatsapp_message(phone_number: str, text: str, image_bytes: bytes = None):
    """
    phone_number: en formato internacional sin +, e.g. '573001234567'
    text: texto a enviar
    image_bytes: opcional bytes de imagen (JPEG)
    """
    try:
        driver = init_driver()
    except Exception as e:
        print("No se pudo inicializar driver whatsapp:", e)
        return False

    # preparar la url para abrir el chat con texto pre-completado
    quoted = urllib.parse.quote(text)
    url = f"https://web.whatsapp.com/send?phone={phone_number}&text={quoted}"
    driver.get(url)

    try:
        # esperar a que el input de texto esté listo (o el botón enviar)
        send_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='compose-btn-send']"))
        )
        # si hay imagen que anexar, usar input[type=file]
        if image_bytes:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            tmp.write(image_bytes)
            tmp.flush()
            tmp.close()
            # botón adjuntar (paperclip)
            try:
                attach_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "span[data-testid='clip']"))
                )
                attach_btn.click()
            except Exception:
                pass
            # input file
            try:
                file_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
                )
                file_input.send_keys(tmp.name)
                # esperar que aparezca el send de la imagen y pulsarlo
                send_img_btn = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[@data-icon='send']"))
                )
                send_img_btn.click()
            except Exception as e:
                print("Error al adjuntar imagen:", e)
            finally:
                try:
                    os.unlink(tmp.name)
                except Exception:
                    pass
        else:
            # si no hay imagen, simplemente click en enviar (ya viene el texto prellenado)
            send_btn.click()
        # pequeño delay para que se envíe
        time.sleep(1.5)
        return True
    except Exception as e:
        # si no encuentra el compose btn, intento enviar con Enter en cuadro de texto
        try:
            input_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab]"))
            )
            input_box.send_keys(Keys.ENTER)
            time.sleep(1)
            return True
        except Exception as e2:
            print("Error enviando mensaje WA:", e, e2)
            return False
