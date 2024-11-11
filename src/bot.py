import requests
from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.update import Update
import schedule
import time
import threading
from db import   favori_urun_ekle_db, favorileri_goster_db, favori_sil_db, tum_favori_urunleri_getir
from scrapper import PriceScraper, fiyat_cek
from config import (
    TELEGRAM_API_TOKEN, 
    PRICE_CHECK_INTERVAL,
    LOGGING_CONFIG,
    TELEGRAM_GROUP_ID
)
import logging

# Logging ayarlarını güncelle
logging.basicConfig(**LOGGING_CONFIG)
logger = logging.getLogger(__name__)

def fiyat_kontrolu(urun_link):
    yeni_fiyat, urun_id = fiyat_cek(urun_link)  
    
    if yeni_fiyat is None:
        return None, urun_id

    return yeni_fiyat, urun_id   

from db import favori_urun_ekle_db, favorileri_goster_db, favori_sil_db, tum_favori_urunleri_getir, favori_fiyat_guncelle_db

def fiyat_guncelle(context: CallbackContext):
    """Favori ürünlerin fiyatlarını güncelle ve değişiklik varsa bildirim gönder."""
    tum_favoriler = tum_favori_urunleri_getir()
    guncellenen_urun_sayisi = 0
    
    for urun in tum_favoriler:
        kullanici_id, urun_id, urun_link, mevcut_fiyat = urun
        yeni_fiyat, _ = fiyat_kontrolu(urun_link)
        
        if yeni_fiyat is not None and yeni_fiyat != mevcut_fiyat:
            guncellenen_urun_sayisi += 1
            # Sadece fiyat düştüğünde bildirim gönder
            if yeni_fiyat < mevcut_fiyat:
                fiyat_degisimi = mevcut_fiyat - yeni_fiyat
                indirim_yuzdesi = (fiyat_degisimi/mevcut_fiyat)*100
                
                # Mesajları kısalt ve URL'yi markdown formatında gönder
                kullanici_mesaji = (
                    f"🔔 Fiyat Düşüşü\n"
                    f"[Ürüne Git]({urun_link})\n"
                    f"💰 Eski: {mevcut_fiyat:.2f} TL\n"
                    f"📉 Yeni: {yeni_fiyat:.2f} TL\n"
                    f"💫 İndirim: {fiyat_degisimi:.2f} TL (%{indirim_yuzdesi:.1f})"
                )
                
                grup_mesaji = (
                    f"🔔 Fiyat Düşüşü\n"
                    f"[Ürüne Git]({urun_link})\n"
                    f"💰 Eski: {mevcut_fiyat:.2f} TL\n"
                    f"📉 Yeni: {yeni_fiyat:.2f} TL\n"
                    f"💫 İndirim: {fiyat_degisimi:.2f} TL (%{indirim_yuzdesi:.1f})"
                )
                
                try:
                    # Mesaj gönderirken disable_web_page_preview ekle
                    context.bot.send_message(
                        chat_id=kullanici_id,
                        text=kullanici_mesaji,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                    
                    context.bot.send_message(
                        chat_id=TELEGRAM_GROUP_ID,
                        text=grup_mesaji,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                    logger.info(f"Fiyat düşüşü bildirimi gönderildi - Kullanıcı: {kullanici_id}, Ürün: {urun_link}")
                except Exception as e:
                    logger.error(f"Bildirim gönderme hatası: {str(e)}")
            
            # Fiyatı veritabanında güncelle
            favori_fiyat_guncelle_db(kullanici_id, urun_id, yeni_fiyat)
    
    # Güncelleme sonucunu bildir
    if hasattr(context, 'job'):
        return  # Otomatik güncelleme ise mesaj gönderme
        
    if context.bot:
        context.bot.send_message(
            chat_id=kullanici_id,
            text=f"✅ Fiyat güncellemesi tamamlandı.\n📊 {guncellenen_urun_sayisi} üründe değişiklik tespit edildi.",
            parse_mode='Markdown'
        )

def start(update: Update, context: CallbackContext):
    """Botun başlangıç mesajı"""
    update.message.reply_text('Merhaba! Bu bot ile favori ürünlerinizin fiyatlarını takip edebilirsiniz.')

def help_command(update: Update, context: CallbackContext):
    """Kullanıcıya yardım mesajı gönder"""
    help_text = (
        "Bu botun kullanabileceğiniz komutlar:\n\n"
        "📦 **/favori_ekle [ürün_linki]** - Ürün favorilere ekle\n"
        "📋 **/favoriler** - Favori ürünleri göster\n"
        #"📋 **/tum_favoriler** - Tüm favori ürünleri göster\n"
        "🗑️ **/favori_sil [ürün_linki]** - Ürün favorilerden sil (ürün linkini kullanarak silin)\n"
  #      "🔄 **/fiyat_guncelle** - Fiyatları güncelle\n\n"
        "🔍 **Olası sorunlar:**\n"
        "Eğer bir ürünün fiyatı doğru şekilde alınmıyorsa, lütfen ürün linkini kontrol edin veya tekrar deneyin."
    )
    update.message.reply_text(help_text)

def favori_ekle(update: Update, context: CallbackContext):
    """Favori ürünü ekle ve fiyat güncelleme işini başlat"""
    try:
        if not update or not update.message:
            logger.error("Update veya message objesi bulunamadı")
            return

        kullanici_id = update.message.chat.id
        if len(context.args) < 1:
            update.message.reply_text("Lütfen ürün linkini belirtin.")
            return

        urun_link = context.args[0]
        
        # Desteklenen site kontrolü
        scraper = PriceScraper()
        scraper_instance = scraper.factory.get_scraper(urun_link)
        if not scraper_instance:
            supported_sites = ", ".join(scraper.get_supported_sites())
            update.message.reply_text(
                f"❌ Bu site desteklenmiyor.\nDesteklenen siteler: {supported_sites}"
            )
            return
        
        # Fiyat kontrolü ve alma işlemi
        yeni_fiyat, urun_id = fiyat_cek(urun_link)
        
        if yeni_fiyat is None:
            update.message.reply_text("Fiyat bilgisi alınamadı. Lütfen ürün linkini kontrol edin.")
            return
        
        # Favori ürünü veritabanına ekleyin
        favori_urun_ekle_db(kullanici_id, urun_id, urun_link, yeni_fiyat)
        
        # Site adını scraper'dan al
        site_adi = scraper_instance.get_site_name()
        update.message.reply_text(
            f"✅ **{site_adi} Ürünü Eklendi**:\n"
            f"🔗 **Ürün Linki**: ({urun_link})\n"
            f"💰 **Mevcut Fiyat**: {yeni_fiyat} TL"
        )
    except Exception as e:
        logger.error(f"Favori ekleme hatası: {str(e)}")
        if update and update.message:
            update.message.reply_text("Bir hata oluştu. Lütfen daha sonra tekrar deneyin.")

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
        update.message.reply_text(" Hiç favori ürün bulunamadı.")

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

def test_group(update: Update, context: CallbackContext):
    """Test mesajı gönder ve chat ID'yi logla"""
    chat_id = update.message.chat_id
    logger.info(f"Current chat ID: {chat_id}")
    update.message.reply_text(f"Bu sohbetin ID'si: {chat_id}")

def main():
    """Botun ana fonksiyonu"""
    updater = Updater(TELEGRAM_API_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("favori_ekle", favori_ekle))
    dp.add_handler(CommandHandler("favoriler", favoriler))
    dp.add_handler(CommandHandler("tum_favoriler", tum_favori_urunler))
    dp.add_handler(CommandHandler("favori_sil", favori_sil))
    dp.add_handler(CommandHandler("test_group", test_group))
    dp.add_handler(CommandHandler("fiyat_guncelle", fiyat_guncelle))

    # Fiyat güncellemelerini config'den al
    updater.job_queue.run_repeating(fiyat_guncelle, interval=PRICE_CHECK_INTERVAL, first=0)

    # Fiyat güncellemelerini kontrol eden thread başlat
    threading.Thread(target=fiyat_guncelle_thread, daemon=True).start()

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()