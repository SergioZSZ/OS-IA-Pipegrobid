import requests, time

def is_active_api(url:str ) -> bool:
    start = time.time()

    while time.time() - start < 60:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
                print("Esperando a que GROBID esté listo...")
        time.sleep(5)
    
    return False