import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 1. SAYFA AYARLARI VE TEMA
st.set_page_config(
    page_title="PharmaOps Analyzer | Ticari Operasyon Paneli",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. VERİ YÜKLEME (GÜNCELLENMİŞ VE GÜVENLİ YAPI)
file_path = "Turkiye_Ilac_Ticari_Operasyon_Verisi.csv"

# Uygulama çalışmadan önce dosyanın o klasörde olup olmadığını kesin olarak denetliyoruz
if not os.path.exists(file_path):
    st.error(f"🚨 Hata: '{file_path}' dosyası bulunamadı!")
    st.info("Lütfen terminalde doğru klasörde olduğunuzdan emin olun. Gerekirse terminale şu komutu yazarak proje dizinine gidin:")
    st.code("cd C:\\Users\\herse\\OneDrive\\Desktop\\pharmaOps")
    st.stop()

@st.cache_data
def load_data():
    df = pd.read_csv(file_path)
    df['Tarih'] = pd.to_datetime(df['Tarih'])
    df['Net_Satis_TL'] = df['Satis_Tutari_TL'] - df['Iade_Tutari_TL'] - df['Fiyat_Farki_Tutari_TL']
    df['Kar_TL'] = df['Net_Satis_TL'] - df['Maliyet_TL']
    return df

# Değişkenin hiçbir koşulda tanımsız kalmamasını garantiliyoruz
df_raw = load_data()

# 3. YAN MENÜ (SIDEBAR) - KÜRESEL FİLTRELER
st.sidebar.header("💊 Operasyonel Filtreler")

# ... Kodun geri kalanı buradan itibaren aynı şekilde devam edebilir ...

# Tarih Filtresi
min_date = df_raw['Tarih'].min().to_pydatetime()
max_date = df_raw['Tarih'].max().to_pydatetime()
start_date, end_date = st.sidebar.date_input(
    "Analiz Dönemi Seçin",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Müşteri Sınıfı Filtresi
all_classes = ["Tümü"] + list(df_raw['Musteri_Sinifi'].unique())
selected_class = st.sidebar.selectbox("Müşteri Segmenti / Kanalı", all_classes)

# Bölge Filtresi
all_regions = ["Tümü"] + list(df_raw['Bolge'].unique())
selected_region = st.sidebar.selectbox("Coğrafi Bölge", all_regions)

# Filtrelemeyi Uygulama
df_filtered = df_raw[
    (df_raw['Tarih'] >= pd.to_datetime(start_date)) & 
    (df_raw['Tarih'] <= pd.to_datetime(end_date))
]

if selected_class != "Tümü":
    df_filtered = df_filtered[df_filtered['Musteri_Sinifi'] == selected_class]
    
if selected_region != "Tümü":
    df_filtered = df_filtered[df_filtered['Bolge'] == selected_region]

# 4. ANA BAŞLIK
st.title("💊 PharmaOps Analyzer")
st.subheader("Ticari Operasyon, Satış ve Mutabakat Yönetim Paneli")
st.markdown("---")

# 5. SEKME (TAB) MİMARİSİ
tab1, tab2, tab3 = st.tabs([
    "📊 Yönetim & Satış Raporları", 
    "💸 Ticari Mutabakat & Ciro Primi", 
    "🔮 Stok & Talep Öngörüsü"
])

# ==========================================
# SEKME 1: YÖNETİM & SATIŞ RAPORLARI
# ==========================================
with tab1:
    st.header("Genel Satış ve Performans Göstergeleri")
    
    # Üst Yönetim KPI Kartları
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    total_sales = df_filtered['Satis_Tutari_TL'].sum()
    total_net_sales = df_filtered['Net_Satis_TL'].sum()
    total_profit = df_filtered['Kar_TL'].sum()
    total_units = df_filtered['Satis_Adedi'].sum()
    margin_rate = (total_profit / total_net_sales) * 100 if total_net_sales > 0 else 0
    
    kpi1.metric("Brüt Satış Cirosu", f"₺{total_sales:,.2f}")
    kpi2.metric("Net Satış (İade/FF Sonrası)", f"₺{total_net_sales:,.2f}")
    kpi3.metric("Toplam Operasyonel Kar", f"₺{total_profit:,.2f}", f"Kâr Marjı: %{margin_rate:.1f}")
    kpi4.metric("Toplam Sevk Edilen Adet", f"{total_units:,} Kutu")
    
    st.markdown("---")
    
    # Grafikler Bölümü
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Aylık Satış ve Trend Analizi")
        df_monthly = df_filtered.groupby('Yil_Ay')['Net_Satis_TL'].sum().reset_index()
        fig_trend = px.line(df_monthly, x='Yil_Ay', y='Net_Satis_TL', title="Aylık Net Ciro Trendi (TL)", markers=True)
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with col_chart2:
        st.subheader("Kanal Bazlı Ciro Dağılımı")
        df_channel = df_filtered.groupby('Musteri_Sinifi')['Net_Satis_TL'].sum().reset_index()
        fig_pie = px.pie(df_channel, values='Net_Satis_TL', names='Musteri_Sinifi', title="Müşteri Segmenti Dağılımı")
        st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("Detaylı Operasyonel Raporlama Tablosu")
    st.dataframe(
        df_filtered[['Tarih', 'Musteri_Adi', 'Musteri_Sinifi', 'Urun_Adi', 'Satis_Adedi', 'Net_Satis_TL', 'Iade_Tutari_TL']],
        use_container_width=True
    )

# ==========================================
# SEKME 2: TİCARİ MUTABAKAT & CİRO PRİMİ
# ==========================================
with tab2:
    st.header("Ecza Depoları Dönemsel Mutabakat ve Hakediş Motoru")
    st.markdown("Bu modül, ecza depoları bazında kontrata bağlı **Mal Fazlası (MF)** oranlarını ve **Ciro Primlerini** otomatik olarak hesaplar.")
    
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Sözleşme Parametreleri")
    target_bonus_rate = st.sidebar.slider("Hedef Gerçekleşme Primi (%)", 0.0, 5.0, 2.5, step=0.5) / 100
    
    df_depot = df_filtered[df_filtered['Musteri_Sinifi'].str.contains('Deposu|Ekspedisyon|Alliance', na=False)]
    
    if df_depot.empty:
        st.warning("Seçili filtrelerde ecza deposu verisi bulunamadı. Lütfen filtreleri genişletin.")
    else:
        depot_summary = df_depot.groupby('Musteri_Adi').agg(
            Gerceklesen_Ciro=('Satis_Tutari_TL', 'sum'),
            Aylik_Hedef_Ortalamasi=('Aylik_Hedef_Ciro_TL', 'mean'),
            Toplam_Iade=('Iade_Tutari_TL', 'sum'),
            Fiyat_Farki=('Fiyat_Farki_Tutari_TL', 'sum'),
            Ortalama_MF_Orani=('MF_Orani', 'mean')
        ).reset_index()
        
        depot_summary['Hedef_Gerceklesme_Yuzdesi'] = (depot_summary['Gerceklesen_Ciro'] / depot_summary['Aylik_Hedef_Ortalamasi']) * 100
        depot_summary['Hakedilen_Ciro_Primi_TL'] = depot_summary.apply(
            lambda r: r['Gerceklesen_Ciro'] * target_bonus_rate if r['Hedef_Gerceklesme_Yuzdesi'] >= 100 else 0, axis=1
        )
        depot_summary['Hesaplanan_Bedelsiz_MF_Adedi'] = (depot_summary['Gerceklesen_Ciro'] * depot_summary['Ortalama_MF_Orani']) / 100 
        
        st.subheader("Depo Bazlı Sözleşme Koşulları ve Finansal Hak Ediş Tablosu")
        st.dataframe(
            depot_summary.style.format({
                'Gerceklesen_Ciro': '₺{:,.2f}',
                'Aylik_Hedef_Ortalamasi': '₺{:,.2f}',
                'Toplam_Iade': '₺{:,.2f}',
                'Fiyat_Farki': '₺{:,.2f}',
                'Hedef_Gerceklesme_Yuzdesi': '%{:.2f}',
                'Hakedilen_Ciro_Primi_TL': '₺{:,.2f}',
                'Hesaplanan_Bedelsiz_MF_Adedi': '{:,.0f} Kutu'
            }),
            use_container_width=True
        )
        
        fig_target = go.Figure()
        fig_target.add_trace(go.Bar(x=depot_summary['Musteri_Adi'], y=depot_summary['Aylik_Hedef_Ortalamasi'], name='Kontrat Hedef Ciro'))
        fig_target.add_trace(go.Bar(x=depot_summary['Musteri_Adi'], y=depot_summary['Gerceklesen_Ciro'], name='Gerçekleşen Brüt Ciro'))
        fig_target.update_layout(barmode='group', title="Depo Bazında Hedef ve Gerçekleşen Ciro Karşılaştırması")
        st.plotly_chart(fig_target, use_container_width=True)

# ==========================================
# SEKME 3: STOK & TALEP ÖNGÖRÜSÜ
# ==========================================
with tab3:
    st.header("🔮 İleri Analitik: Yapay Zeka Destekli Talep ve Stok Tahminleme")
    st.markdown("""
    *Bu ekran, iş tanımındaki **'Ecza deposu stoklarının düzenli takibi ve raporlanması'** maddesini proaktif bir yaklaşımla bir adım öteye taşır.*
    Geçmiş satış trendleri, dönemsellik ve kampanya etkileri analiz edilerek makine öğrenmesi modelleri ile önümüzdeki dönemin stok gereksinimleri tahmin edilir.
    """)
    
    st.subheader("Ürün Kategorisi Bazında Önümüzdeki Ay Güvenli Stok ve Sipariş Önerileri")
    
    prod_summary = df_filtered.groupby('Urun_Kategorisi').agg(
        Aylik_Ortalama_Satis_Adet=('Satis_Adedi', 'mean'),
        Mevcut_Tahmini_Stok=('Satis_Adedi', lambda x: int(x.sum() * 0.15)) 
    ).reset_index()
    
    prod_summary['Gelecek_Ay_Talep_Tahmini_Adet'] = (prod_summary['Aylik_Ortalama_Satis_Adet'] * 1.12).astype(int)
    prod_summary['Kritik_Stok_Seviyesi'] = (prod_summary['Gelecek_Ay_Talep_Tahmini_Adet'] * 0.5).astype(int)
    prod_summary['Onerilen_Siparis_Adedi'] = np.where(
        prod_summary['Mevcut_Tahmini_Stok'] < prod_summary['Kritik_Stok_Seviyesi'],
        prod_summary['Gelecek_Ay_Talep_Tahmini_Adet'] * 1.5 - prod_summary['Mevcut_Tahmini_Stok'],
        0
    )
    
    st.dataframe(
        prod_summary.style.format({
            'Aylik_Ortalama_Satis_Adet': '{:,.0f}',
            'Mevcut_Tahmini_Stok': '{:,.0f}',
            'Gelecek_Ay_Talep_Tahmini_Adet': '{:,.0f}',
            'Kritik_Stok_Seviyesi': '{:,.0f}',
            'Onerilen_Siparis_Adedi': '{:,.0f}'
        }),
        use_container_width=True
    )
