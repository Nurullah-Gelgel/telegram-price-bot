# Telegram Fiyat İzleme Botu

Bu proje, kullanıcıların belirli ürünlerin fiyatlarını izleyebileceği bir Telegram botu oluşturmaktadır.

## Özellikler
- **Fiyat Kontrolü**: Kullanıcılar, belirli ürünlerin fiyatlarını kontrol edebilir.
- **Bildirim Gönderimi**: Fiyat düştüğünde kullanıcıya bildirim gönderilir.
- **Kullanıcı Dostu Arayüz**: Telegram üzerinden kolay erişim.
- **Otomatik Güncelleme**: Belirli aralıklarla fiyat kontrolü.
- **Veri Kaydetme**: Kullanıcıların izlediği ürünler veritabanında saklanır.

## Kurulum
1. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
2. Botunuzu Telegram'da oluşturun ve `API_TOKEN` ile değiştirin.
3. Botu çalıştırın:
   ```bash
   python src/bot.py
   ```

## Kullanım
- `/favori_ekle <urun_id> <urun_link> <mevcut_fiyat>` komutunu kullanarak ürün ekleyin.
