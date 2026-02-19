import requests

def is_active_api(url:str ) -> bool:
    try:
        response = requests.get(url, timeout=2)
        return True
    except requests.exceptions.RequestException:
            return False