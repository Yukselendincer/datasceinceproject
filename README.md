# 🛒 Instacart Market Basket Analysis

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-orange)
![Machine Learning](https://img.shields.io/badge/Machine-Learning-success)
![License](https://img.shields.io/badge/License-MIT-green)

## 📊 Proje Hakkında

Bu proje, Instacart'ın perakende veri seti üzerinde kapsamlı bir market sepet analizi gerçekleştirir. Müşteri segmentasyonu, satın alma davranışları ve churn tahmini gibi önemli iş zekası metriklerini içerir.

## 🎯 Temel Özellikler

- **📈 RFM Analizi**: Müşterileri 10 farklı segmente ayırma
- **🕒 Zaman Analizi**: Siparişlerin gün ve saat bazında dağılımı
- **🛍️ Ürün Analizi**: En popüler koridorlar ve departmanlar
- **⚠️ Churn Tahmini**: Müşteri kaybını önceden tahmin etme
- **🤖 Makine Öğrenmesi**: Random Forest ile %86 doğrulukta tahmin modeli

## 📁 Veri Seti

Instacart'ın açık veri seti kullanılmıştır:
- `orders.csv` - Sipariş bilgileri
- `products.csv` - Ürün kataloğu
- `order_products__prior.csv` - Önceki sipariş detayları
- `departments.csv` - Departman bilgileri
- `aisles.csv` - Koridor bilgileri

## 🛠️ Kullanılan Teknolojiler

- **Python 3.8+**
- **Pandas & NumPy** - Veri işleme
- **Matplotlib & Seaborn** - Görselleştirme
- **Scikit-learn** - Makine öğrenmesi
- **Jupyter Notebook** - Analiz ortamı

## 📈 Ana Bulgular

### 1. Müşteri Segmentasyonu
- **%59** müşteri daha önce aldığı ürünleri yeniden sipariş ediyor
- **10 farklı müşteri segmenti** belirlendi:
  - 🏆 Champions (%15)
  - 🤝 Loyal Customers (%22)
  - ⚠️ At Risk (%18)
  - 💤 Hibernating (%12)

### 2. Satın Alma Alışkanlıkları
- **En yoğun gün**: Cumartesi
- **En yoğun saat**: 10:00 - 16:00
- **En popüler koridor**: Fresh Fruits
- **En çeşitli departman**: Produce

### 3. Churn Analizi
- **Random Forest modeli** ile %86 doğruluk
- **En önemli faktörler**: Sipariş sıklığı ve ortalama sepet tutarı
- **SMOTE** ile model optimizasyonu

## 🚀 Kurulum ve Çalıştırma

```bash
# Repository'yi klonlayın
git clone https://github.com/Yukselendincer/datasceinceproject.git

# Dizin değiştirin
cd datasceinceproject

# Gerekli kütüphaneleri yükleyin
pip install pandas numpy matplotlib seaborn scikit-learn jupyter

# Jupyter Notebook'u başlatın
jupyter notebook
