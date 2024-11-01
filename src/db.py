import sqlite3

def create_connection():
    """Veritabanı bağlantısı oluştur"""
    conn = sqlite3.connect('favoriler.db')
    return conn

def create_table():
    """Tabloyu oluştur"""
    conn = create_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS favori_urunler
                 (kullanici_id TEXT, urun_id TEXT, urun_link TEXT, mevcut_fiyat REAL)''')
    conn.commit()
    conn.close()

def favori_urun_ekle_db(kullanici_id, urun_id, urun_link, mevcut_fiyat):
    conn = create_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO favori_urunler VALUES (?, ?, ?, ?)", (kullanici_id, urun_id, urun_link, mevcut_fiyat))
        conn.commit()
    except Exception as e:
        print(f"Error adding favorite product: {e}")
    finally:
        conn.close()

def favorileri_goster_db(kullanici_id):
    conn = create_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM favori_urunler WHERE kullanici_id = ?", (kullanici_id,))
        return c.fetchall()
    except Exception as e:
        print(f"Error fetching favorites: {e}")
        return []
    finally:
        conn.close()

def favori_sil_db(kullanici_id, urun_id):
    conn = create_connection()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM favori_urunler WHERE kullanici_id = ? AND urun_id = ?", (kullanici_id, urun_id))
        conn.commit()
    except Exception as e:
        print(f"Error deleting favorite product: {e}")
    finally:
        conn.close()

def tum_favori_urunleri_getir():
    conn = create_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM favori_urunler")
        return c.fetchall()
    except Exception as e:
        print(f"Error fetching all favorites: {e}")
        return []
    finally:
        conn.close()

def favori_fiyat_guncelle_db(kullanici_id, urun_id, yeni_fiyat):
    conn = create_connection()
    c = conn.cursor()
    try:
        c.execute("UPDATE favori_urunler SET mevcut_fiyat = ? WHERE kullanici_id = ? AND urun_id = ?", 
                  (yeni_fiyat, kullanici_id, urun_id))
        conn.commit()
    except Exception as e:
        print(f"Error updating product price: {e}")
    finally:
        conn.close()

# Tabloyu oluştur
create_table()