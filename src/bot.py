import requests
from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.update import Update
import schedule
import time
import threading
from db import   favori_urun_ekle_db, favorileri_goster_db, favori_sil_db, tum_favori_urunleri_getir
from scrapper import trendyol_fiyat_cek, fiyat_kontrolu

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

def fiyat_kontrolu(urun_link):
    yeni_fiyat, urun_id = trendyol_fiyat_cek(urun_link)  
    
    if yeni_fiyat is None:
        return None, urun_id

    return yeni_fiyat, urun_id   

from db import favori_urun_ekle_db, favorileri_goster_db, favori_sil_db, tum_favori_urunleri_getir, favori_fiyat_guncelle_db

def fiyat_guncelle(context: CallbackContext):
    """Favori ürünlerin fiyatlarını güncelle ve değişiklik varsa bildirim gönder."""
    tum_favoriler = tum_favori_urunleri_getir()
    for urun in tum_favoriler:
        kullanici_id, urun_id, urun_link, mevcut_fiyat = urun
        yeni_fiyat, _ = fiyat_kontrolu(urun_link)
        
        if yeni_fiyat is not None and yeni_fiyat != mevcut_fiyat:
            # Fiyat değişikliği var, bildirim gönder
            fiyat_degisimi = yeni_fiyat - mevcut_fiyat
            emoji = "📉" if fiyat_degisimi < 0 else "📈"
            mesaj = (
                f"🔔 **Fiyat Değişikliği Bildirimi**:\n"
                f"🔗 **Ürün Linki**: {urun_link}\n"
                f"💰 **Eski Fiyat**: {mevcut_fiyat:.2f} TL\n"
                f"{emoji} **Yeni Fiyat**: {yeni_fiyat:.2f} TL\n"
                f"🔄 **Fark**: {abs(fiyat_degisimi):.2f} TL ({emoji})"
            )
            context.bot.send_message(chat_id=kullanici_id, text=mesaj, parse_mode='Markdown')
            
            # Fiyatı veritabanında güncelle
            favori_fiyat_guncelle_db(kullanici_id, urun_id, yeni_fiyat)
            # Fiyatı veritabanında güncelle
            # favori_fiyat_guncelle_db(kullanici_id, urun_id, yeni_fiyat)  # Bu fonksiyonu implement etmeniz gerekebilir

API_TOKEN = '7723288845:AAG8VEessGMqrV2H78Wlzibtm9y3PV2ET2Y'

def start(update: Update, context: CallbackContext):
    """Botun başlangıç mesajı"""
    update.message.reply_text('Merhaba! Bu bot ile favori ürünlerinizin fiyatlarını takip edebilirsiniz.')

def help_command(update: Update, context: CallbackContext):
    """Kullanıcıya yardım mesajı gönder"""
    help_text = (
        "Bu botun kullanabileceğiniz komutlar:\n\n"
        "📦 **/favori_ekle [ürün_linki]** - Ürün favorilere ekle\n"
        "📋 **/favoriler** - Favori ürünleri göster\n"
        "📋 **/tum_favoriler** - Tüm favori ürünleri göster\n"
        "🗑️ **/favori_sil [ürün_linki]** - Ürün favorilerden sil (ürün linkini kullanarak silin)\n"
        "🔄 **/fiyat_guncelle** - Fiyatları güncelle\n\n"
        "🔍 **Olası sorunlar:**\n"
        "Eğer bir ürünün fiyatı doğru şekilde alınmıyorsa, lütfen ürün linkini kontrol edin veya tekrar deneyin."
    )
    update.message.reply_text(help_text)

def favori_ekle(update: Update, context: CallbackContext):
    """Favori ürünü ekle ve fiyat güncelleme işini başlat"""
    kullanici_id = update.message.chat.id
    if len(context.args) < 1:
        update.message.reply_text("Lütfen ürün linkini belirtin.")
        return

    urun_link = context.args[0]  
    
    # Fiyat kontrolü ve alma işlemi
    yeni_fiyat, urun_id = fiyat_kontrolu(urun_link)
    
    if yeni_fiyat is None:
        update.message.reply_text("Fiyat bilgisi alınamadı. Lütfen ürün linkini kontrol edin.")
        return
    
    # Favori ürünü veritabanına ekleyin
    favori_urun_ekle_db(kullanici_id, urun_id, urun_link, yeni_fiyat)
    
    update.message.reply_text(
        f"✅ **Favori Ürün Eklendi**:\n"
        f"🔗 **Ürün Linki**: ({urun_link})\n"
        f"💰 **Mevcut Fiyat**: {yeni_fiyat} TL."
    )

def favoriler(update: Update, context: CallbackContext):
    """Favori ürünleri göster"""
    kullanici_id = update.message.chat.id
    favoriler_listesi = favorileri_goster_db(kullanici_id)
    if favoriler_listesi:
        mesaj = "📋 **Favori Ürünleriniz**:\n"
        for urun in favoriler_listesi:
            mesaj += (
                f"🔗 **Ürün Linki**: ({urun[2]})\n"
                f"💰 **Mevcut Fiyat**: {urun[3]} TL\n\n"
            )
        update.message.reply_text(mesaj)
    else:
        update.message.reply_text("🚫 Favori ürün listeniz boş.")

def tum_favori_urunler(update: Update, context: CallbackContext):
    """Tüm favori ürünleri göster"""
    tum_favoriler = tum_favori_urunleri_getir()
    if tum_favoriler:
        mesaj = "📋 **Tüm Favori Ürünler**:\n"
        for urun in tum_favoriler:
            mesaj += (
                f"🔗 **Ürün Linki**: ({urun[2]})\n"
                f"💰 **Mevcut Fiyat**: {urun[3]} TL\n\n"
            )
        update.message.reply_text(mesaj)
    else:
        update.message.reply_text("🚫 Hiç favori ürün bulunamadı.")

def favori_sil(update: Update, context: CallbackContext):
    """Favori ürünü sil"""
    kullanici_id = update.message.chat.id
    if len(context.args) < 1:
        update.message.reply_text("Lütfen silmek istediğiniz ürün linkini belirtin.")
        return
    
    urun_link = context.args[0]
    urun_id = urun_link.split('/')[-1]  # Ürün ID'sini linkten çıkar
    favori_sil_db(kullanici_id, urun_id)
    update.message.reply_text(f"✅ **Favori Ürün Silindi**:\n🔗 **Ürün Linki**: ({urun_link})")

def fiyat_guncelle_thread():
    """Fiyat güncellemelerini belirli bir aralıkta kontrol et"""
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    """Botun ana fonksiyonu"""
    updater = Updater(API_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("favori_ekle", favori_ekle))
    dp.add_handler(CommandHandler("favoriler", favoriler))
    dp.add_handler(CommandHandler("tum_favoriler", tum_favori_urunler))
    dp.add_handler(CommandHandler("favori_sil", favori_sil))

    # Fiyat güncellemelerini saatlik olarak ayarla
    updater.job_queue.run_repeating(fiyat_guncelle, interval=3600, first=0)

    # Fiyat güncellemelerini kontrol eden thread başlat
    threading.Thread(target=fiyat_guncelle_thread, daemon=True).start()

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()