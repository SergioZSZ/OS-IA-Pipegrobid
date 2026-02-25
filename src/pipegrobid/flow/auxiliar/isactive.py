import requests, time

def is_active_api(url:str ) -> bool:
    start = time.time()

    while time.time() - start < 30:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
                pass
        time.sleep(5)
    
    return False