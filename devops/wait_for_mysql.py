import socket, time, sys

HOST, PORT = "mysql", 3306
RETRIES = 90

for i in range(RETRIES):
    s = socket.socket()
    s.settimeout(1.5)
    try:
        s.connect((HOST, PORT))
        s.close()
        print("DB OK, arrancando FastAPI")
        sys.exit(0)
    except Exception as e:
        print(f"[{i+1}/{RETRIES}] Esperando DB... {e}")
        time.sleep(2)

print("DB NO RESPONDE a tiempo")
sys.exit(1)
