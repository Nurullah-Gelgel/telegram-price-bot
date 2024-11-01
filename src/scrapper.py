import requests
from bs4 import BeautifulSoup
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def create_session_with_retries():
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def get_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--disable-popup-blocking')
    
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        logger.error(f"ChromeDriver başlatma hatası: {str(e)}")
        raise

def hepsiburada_fiyat_cek(urun_link):
    driver = None
    try:
        driver = get_chrome_driver()
        driver.get(urun_link)
        
        driver.implicitly_wait(10)
        
        wait = WebDriverWait(driver, 10)
        fiyat_element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "VaczsRSWR2VQmrUQGLw4"))
        )
        
        fiyat_text = fiyat_element.find_element(By.CLASS_NAME, "rNEcFrF82c7bJGqQHxht").text.strip()
        
        fiyat_text = fiyat_text.replace('TL', '').replace(' ', '').strip()
        fiyat_text = fiyat_text.replace('.', '').replace(',', '.')
        
        try:
            fiyat = float(fiyat_text)
            urun_id = urun_link.split('/')[-1].split('?')[0]
            return fiyat, urun_id
        except ValueError:
            logger.error(f"Fiyat dönüştürme hatası: {fiyat_text}")
            return None, urun_link
            
    except Exception as e:
        logger.error(f"Hepsiburada fiyat çekme hatası: {str(e)}")
        return None, urun_link
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logger.error(f"Driver kapatma hatası: {str(e)}")

def trendyol_fiyat_cek(urun_link):
    session = create_session_with_retries()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = session.get(urun_link, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        fiyat_element = soup.find('span', {'class': 'prc-dsc'})
        if not fiyat_element:
            return None, urun_link
            
        fiyat_text = fiyat_element.text.strip()
        fiyat_text = fiyat_text.replace('TL', '').replace('.', '').replace(',', '.').strip()
        
        try:
            fiyat = float(fiyat_text)
            return fiyat, urun_link.split('-p-')[1].split('?')[0]
        except (ValueError, IndexError):
            return None, urun_link
            
    except Exception as e:
        logger.error(f"Trendyol fiyat çekme hatası: {str(e)}")
        return None, urun_link

def site_kontrol(urun_link):
    if "trendyol.com" in urun_link:
        return "trendyol"
    elif "hepsiburada.com" in urun_link:
        return "hepsiburada"
    return None

def fiyat_cek(urun_link):
    site = site_kontrol(urun_link)
    if site == "trendyol":
        return trendyol_fiyat_cek(urun_link)
    elif site == "hepsiburada":
        return hepsiburada_fiyat_cek(urun_link)
    return None, urun_link

def fiyat_kontrolu(urun_link):
    yeni_fiyat, urun_id = fiyat_cek(urun_link)
    if yeni_fiyat is None:
        return None, urun_id
    return yeni_fiyat, urun_id