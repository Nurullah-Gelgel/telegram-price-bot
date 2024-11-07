import os
from typing import Dict, Any

# Telegram Bot Ayarları
TELEGRAM_API_TOKEN = '7723288845:AAG8VEessGMqrV2H78Wlzibtm9y3PV2ET2Y'
TELEGRAM_GROUP_ID = '-4527800930'  # FiyatTakip grubu ID'si
PRICE_CHECK_INTERVAL = 600  # 10 dakika (saniye cinsinden)

# Veritabanı Ayarları
DB_NAME = 'favoriler.db'
DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)

# Selenium Ayarları
SELENIUM_CONFIG: Dict[str, Any] = {
    'chrome_options': [
        '--headless',
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--window-size=1920,1080',
        '--ignore-certificate-errors',
        '--ignore-ssl-errors',
    ],
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Logging Ayarları
LOGGING_CONFIG = {
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'level': 'INFO'
}

# Site-specific timeouts (saniye cinsinden)
SITE_TIMEOUTS = {
    'default': 10,
    'watsons.com.tr': 15,
    'trendyol.com': 10,
    'hepsiburada.com': 10,
    'n11.com': 10,
    'gratis.com': 10,
    'rossmann.com.tr': 10
}