import requests
from bs4 import BeautifulSoup
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_session_with_retries():
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def trendyol_fiyat_cek(urun_link):
    urun_id = urun_link.split('/')[-1]
    url = f"https://www.trendyol.com/urun/{urun_id}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print("HTTP isteği başarısız oldu.")
        return None, urun_id
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    fiyat_element = soup.find("span", {"class": "prc-dsc"})
    if fiyat_element is None:
        print("Fiyat elemanı bulunamadı. HTML yapısını kontrol edin.")
        return None, urun_id
    
    fiyat = fiyat_element.text.strip()
    fiyat = float(fiyat.replace(' TL', '').replace('.', '').replace(',', '.'))
    
    return fiyat, urun_id

def fiyat_kontrolu(urun_link, mevcut_fiyat):
    yeni_fiyat, urun_id = trendyol_fiyat_cek(urun_link)  
    
    if yeni_fiyat is None:
        return None, urun_id

    if yeni_fiyat < mevcut_fiyat:
        return True, yeni_fiyat, urun_id
    
    return False, mevcut_fiyat, urun_id