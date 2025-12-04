import xlwings as xw
from typing import Union

# =========================================================
# PROFESYONEL BORDRO KONSTANTLARI (2025 MODELLENMİŞ)
# =========================================================

# NOT: Bu oranlar 2025 yılına göre modellenmiş yaklaşık değerlerdir.
SGK_ISCI_PAYI = 0.14
ISSIZLIK_SIGORTASI_ISCI_PAYI = 0.01
DAMGA_VERGISI_ORAN = 0.00759
ASGARI_BRUT_2025 = 26005.50

# 2025 YILI GELİR VERGİSİ DİLİMLERİ (Kümülatif Matrah ve Oranlar)
# DİKKAT: Veri güncel bir kaynaktan modellenmelidir!
VERGI_DILIMLERI = [
    (110000, 0.15),  # 15%
    (230000, 0.20),  # 20%
    (870000, 0.27),  # 27%
    (3000000, 0.35), # 35%
    (float('inf'), 0.40) # 40%
]


# =========================================================
# YARDIMCI FONKSİYONLAR
# =========================================================

def ASGARI_ISTISNA_KONTROL(brut_ucret: float, kesinti_tipi: str) -> float:
    """Asgari Ücretin GV ve DV istisnasını kontrol eder."""
    # Basitlik için sadece Brüt Asgari Ücretin kendisine eşit olma durumunu kontrol ederiz.
    if brut_ucret == ASGARI_BRUT_2025:
        if kesinti_tipi == "GV" or kesinti_tipi == "DV":
            return 0.0
    return 1.0


def HESAPLA_GELIR_VERGISI(vergi_matrahi_aylik: float, kümülatif_matrah_eski: float) -> tuple:
    """
    Kümülatif matraha göre aylık Gelir Vergisi ve yeni kümülatif matrahı hesaplar.
    """
    vergi = 0.0
    kümülatif_matrah_yeni = kümülatif_matrah_eski
    matrah_kalan = vergi_matrahi_aylik

    for limit, oran in VERGI_DILIMLERI:
        
        # Önceki dilimden kalan matrahı çıkar.
        matrah_dilim_baslangici = limit - vergi_matrahi_aylik
        
        # Eğer yeni kümülatif matrah hala mevcut dilimin altındaysa, hesaplamaya devam et.
        if kümülatif_matrah_eski < limit:
            
            # Bu dilimde vergilenecek matrah ne kadar?
            bu_dilimdeki_matrah_kapasitesi = limit - kümülatif_matrah_eski
            
            # Matrahımız bu dilimi dolduruyor mu?
            vergilenecek_matrah = min(matrah_kalan, bu_dilimdeki_matrah_kapasitesi)
            
            vergi += vergilenecek_matrah * oran
            kümülatif_matrah_yeni += vergilenecek_matrah
            matrah_kalan -= vergilenecek_matrah
        
        if matrah_kalan <= 0:
            break
            
    return round(vergi, 2), kümülatif_matrah_yeni


def GET_BRUT_NET_DETAIL(brut_ucret: float, kümülatif_matrah_eski: float) -> tuple:
    """Tek bir ay için tüm kesintileri ve kümülatif matrahı hesaplar."""
    
    # 1. SGK ve İşsizlik Kesintileri
    gv_istisna_faktoru = ASGARI_ISTISNA_KONTROL(brut_ucret, "GV")
    dv_istisna_faktoru = ASGARI_ISTISNA_KONTROL(brut_ucret, "DV")
    
    sgk_primi = brut_ucret * SGK_ISCI_PAYI
    issizlik_primi = brut_ucret * ISSIZLIK_SIGORTASI_ISCI_PAYI
    
    # 2. Vergi Matrahı
    vergi_matrahi_aylik = brut_ucret - (sgk_primi + issizlik_primi)
    
    # 3. Gelir ve Damga Vergisi
    damga_vergisi = brut_ucret * DAMGA_VERGISI_ORAN * dv_istisna_faktoru
    gelir_vergisi_tutari, kümülatif_matrah_yeni = HESAPLA_GELIR_VERGISI(
        vergi_matrahi_aylik * gv_istisna_faktoru, # GV istisnası uygulanmış matrah
        kümülatif_matrah_eski
    )
    
    # 4. Net Hesaplama
    toplam_kesinti = sgk_primi + issizlik_primi + gelir_vergisi_tutari + damga_vergisi
    net_ucret = brut_ucret - toplam_kesinti
    
    return net_ucret, sgk_primi, issizlik_primi, gelir_vergisi_tutari, damga_vergisi, kümülatif_matrah_yeni


# =========================================================
# ANA TETİKLEYİCİ FONKSİYON (RUNPYTHON)
# =========================================================

def main_bordro():
    """Excel butonuna basıldığında (RunPython) çalışır, kümülatif bordro hesaplar."""
    try:
        wb = xw.Book.caller()
        sheet = wb.sheets[0]
        
        # Girişleri Al
        mode = str(sheet.range("A1").value).strip().upper()
        aylik_ucret_giris = sheet.range("A2").value
        
        if not mode or not aylik_ucret_giris or aylik_ucret_giris <= 0:
            sheet.range("C1").value = "HATA: Lütfen A1/A2 hücrelerini geçerli doldurun."
            sheet.range("A5").clear_contents()
            return

        # Başlangıç değişkenleri
        kümülatif_matrah = 0.0
        aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", 
                 "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        
        # DASHBOARD BAŞLIĞI
        sonuclar = [["Ay", "Brüt Ücret", "Net Ücret", "SGK Primi", "İşsizlik Primi", "Gelir Vergisi", "Damga Vergisi"]]

        # 12 AYLIK DÖNGÜ
        for ay in aylar:
            # Mode'a göre Brüt ücreti belirle (NET modunda brüt tahmini kullanılır)
            if mode == "BRÜT" or mode == "BRUT":
                brut_m = aylik_ucret_giris
            elif mode == "NET":
                # NET'ten brüt'e tahmini (basit iterasyon bu kadar karmaşık bir modelde hatalı sonuç verebilir)
                brut_m = aylik_ucret_giris * 1.35 # Basit katsayı ile başlangıç
            else:
                 raise ValueError("Mod (A1) Geçersiz.")


            # Ayrıntılı Hesaplama
            net_m, sgk, issizlik, gv, dv, kümülatif_matrah = GET_BRUT_NET_DETAIL(brut_m, kümülatif_matrah)
            
            sonuclar.append([ay, round(brut_m, 2), round(net_m, 2), round(sgk, 2), round(issizlik, 2), round(gv, 2), round(dv, 2)])
        
        # Çıktıyı A5 hücresine yaz
        sheet.range("A5").clear_contents()
        sheet.range("A5").value = sonuclar
        sheet.range("A5").expand().autofit()
        
        sheet.range("C1").value = "Profesyonel Bordro Başarıyla Hesaplandı!"
        sheet.range("C1").api.Font.Color = 0x008000 # Yeşil

    except Exception as e:
        sheet.range("C1").value = f"KRİTİK HATA: Hesaplama başarısız. Detay: {e}"
        sheet.range("C1").api.Font.Color = 0x0000FF # Kırmızı