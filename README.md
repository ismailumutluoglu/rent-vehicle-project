# 🚗🛵 Vehicle Rental (OOP Demo)

Bu depo; basit bir araç kiralama senaryosu (bisiklet & araba) üzerinden Python’da Nesne Yönelimli Programlama (OOP) kavramlarını izole ve anlaşılır bir model ile göstermeyi amaçlayan küçük bir çalışma alanıdır.  
Amaç: Tek bir monolit uygulama geliştirmekten çok; sınıf hiyerarşisi, sorumluluk ayrımı, durum yönetimi, davranışın alt sınıflarda farklılaştırılması ve faturalama (hesaplama) mantığının nasıl şekillendirilebileceğini örneklemek.

---

## 🎯 Genel Bakış

Uygulama; kullanıcıdan terminal üzerinden etkileşim alarak:

- Stok görüntüleme
- Saatlik veya günlük kiralama
- Araç iade & fatura hesaplama
- Çoklu araçta indirim uygulama

akışlarını yönetir.

Kod iki ana parçadan oluşur:

- `vehicle.py` : OOP model (üst/alt sınıflar + müşteri)
- (ör: `main.py`) : Menü döngüsü ve kullanıcı etkileşimi

---

## 🧱 Sınıf Sorumlulukları

| Sınıf         | Rol                                  | Öne Çıkan Noktalar                                                          |
| ------------- | ------------------------------------ | --------------------------------------------------------------------------- |
| `VehicleRent` | Üst sınıf (genel kiralama davranışı) | Stok, zaman damgası, saatlik/günlük kiralama, fatura üretiminde ortak süreç |
| `CarRent`     | Araba için alt sınıf                 | Ek indirim metodu (`discount`) – genişletilebilir fiyatlandırma noktası     |
| `BikeRent`    | Bisiklet için alt sınıf              | Şimdilik farklı davranış eklenmemiş – sade kalıtım örneği                   |
| `Customer`    | Kullanıcı oturumu / kiralama durumu  | Seçilen araç sayıları, kiralama zamanı & türü, iade talebi üretimi          |

---

## 🧩 OOP Öğeleri Nasıl Kullanılıyor?

- Kalıtım (Inheritance): `CarRent` ve `BikeRent`, `VehicleRent` davranışını tekrar etmeden temel işlevleri devralır.
- Durum Yönetimi: Kiralama zamanı (`rentalTime_x`), temeli ve araç adedi müşteri nesnesi seviyesinde tutulur; mağaza stokları sınıf örneklerinde tutulur.
- Polimorfizm (Potansiyel): Farklı araç türleri için hesap mantığı genişletilebilir (ör: ileride `ScooterRent` eklendiğinde aynı arayüz korunabilir).
- Encapsulation (Basit Düzey): Doğrudan attribute kullanımı var; daha ileri düzey versiyonda property veya özel (private benzeri) alanlar eklenebilir.
- Ayrık Sorumluluk (Separation of Concerns): UI (terminal menüsü) ile iş modeli (`vehicle.py`) birbirinden ayrılmış durumda.

---

## 💰 Fiyatlandırma & İndirim Mantığı (Özet)

| Araç     | Saatlik | Günlük (Formülü)                           | Çoklu Kiralama İndirimi |
| -------- | ------- | ------------------------------------------ | ----------------------- |
| Araba    | 10 $    | `10 * 8/10 * 24` (günlük indirimli çarpan) | 2+ araçta %20           |
| Bisiklet | 5 $     | `5 * 7/10 * 24`                            | 4+ bisiklette %20       |

Fatura süresi:  
`rentalPeriod = now - rentalTime`  
Saatlik: `rentalPeriod.seconds / 3600`  
Günlük: `rentalPeriod.seconds / (3600 * 24)`

Not: Süre tam saat/gün değilse oransal ücret hesaplanır (yuvarlama yapılmaz).

---

## ▶️ Çalıştırma

```bash
git clone https://github.com/ismailumutluoglu/oop-python.git
cd oop-python
python main.py
```

Python 3.9+ yeterlidir (standart kütüphane dışında bağımlılık yok).

---

## 🖥 Örnek Terminal Akışı

```
***** Vehicle Rental Shop*****
A. Bike Menu
B. Car Menu
Q. Exit

Enter choice: a
****** BIKE MENU*****
1. Display available bikes
2. Request a bike on hourly basis $ 5
3. Request a bike on daily basis $ 84
4. Return a bike
5. Main Menu
6. Exit

Enter choice: 2
How many bikes would you like to rent? 3
Rented a 3 vehicle for hourly at 2025-09-07 08:50:10.123456
----------------
Thank you for using the vehicle rental shop
```

---

## 🧪 Tasarım Notları (Gözlemler & İyileştirme Fırsatları)

| Konu               | Mevcut Durum                                | İyileştirme Önerisi                           |
| ------------------ | ------------------------------------------- | --------------------------------------------- |
| Faturalama         | Tek metot içinde marka bazlı koşullar       | Strateji / ayrı fiyatlandırma sınıfı          |
| Zaman Ölçümü       | `datetime.now()` + `seconds`                | `timedelta.total_seconds()` kullanımı         |
| Kullanıcı Girdisi  | `input()` doğrudan model katmanına yakın    | UI katmanını tamamen ayırma                   |
| Büyüme             | Araç türü eklemek manuel koşul gerektiriyor | Polimorfik `calculate_bill()` metodu          |
| İndirim            | Sabit kural                                 | Esnek indirim zinciri (Chain / Policy)        |
| Test Edilebilirlik | Doğrudan I/O var                            | Saf mantık fonksiyonları faktörize edilebilir |
| Veri Doğrulama     | Negatif/0 kontroller var                    | Özel exception sınıfları ile ayrıştırma       |

---

## 🔄 Genişletme Örneği (Yeni Araç Türü Taslağı)

```python
class ScooterRent(VehicleRent):
    HOURLY_RATE = 7
    DAILY_RATE = HOURLY_RATE * 0.75 * 24

    def pricing(self, rental_period_hours, basis, count):
        if basis == 1:
            return rental_period_hours * self.HOURLY_RATE * count
        elif basis == 2:
            return (rental_period_hours / 24) * self.DAILY_RATE * count
```

(Bunun için mevcut fatura hesaplama mantığı soyutlanmalı.)

---

## 🧭 Yol Haritası (İsteğe Bağlı)

- [ ] Faturalama mantığını sınıflardan ayır
- [ ] İndirim politikalarını modüler hale getir
- [ ] Araç türü eklemeyi otomatik tanımlanabilir yap (registry pattern)
- [ ] Test dosyaları ekle (`pytest`)
- [ ] CLI yerine argparse tabanlı komutlar
- [ ] Exception hiyerarşisi (örn: `InvalidQuantityError`)
- [ ] Dokümantasyon (kısa API referansı)
- [ ] Fiyatlandırmayı JSON / YAML yapılandırması ile dışsallaştır

---

## 🧪 Kısa Örnek: Basit Modüler Faturalama Fikri

```python
class PricingPolicy:
    def compute(self, hours: float, basis: int, count: int) -> float:
        raise NotImplementedError

class BikePricing(PricingPolicy):
    HOURLY = 5
    DAILY = HOURLY * 0.7 * 24
    def compute(self, hours, basis, count):
        return (hours * self.HOURLY if basis == 1 else (hours/24)*self.DAILY) * count
```

---

## ⚠️ Sınırlamalar

- Gerçek süre kiralama “başlangıç–bitiş” doğruluğu amaçlanmamış (örn. tam gün yuvarlama yok).
- Fiyatlandırma verisi kod içine gömülü.
- Persistans (dosya/veritabanı) yok; tüm durum runtime’da kaybolur.
- Eşzamanlılık (aynı stok üzerinde çoklu kullanıcı) ele alınmamış.

---

## 🖥 Streamlit Arayüz (Yeni)

Bu depo artık terminal menüsüne ek olarak bir web arayüz (Streamlit) içerir.

### Çalıştırma

```bash
pip install -r requirements.txt
streamlit run app.py
```

Ardından tarayıcıda otomatik açılmazsa: http://localhost:8501

### Özellikler

- Stok ve kullanım yüzdeleri (sidebar)
- Kiralama (bisiklet / araba, saatlik / günlük)
- Aktif kiralamaları görüntüleme
- İade + fatura hesaplama (indirim mantığı korunuyor)
- Anlık gelir tablosu ve zaman serisi grafiği
- Kod inceleme / öneriler sekmesi
- Uygulama durumunu sıfırlama düğmesi

### Ekran Akışı

1. Kiralama sekmesinden araç ve tür seç → Kirala
2. İade sekmesinden aracı iade et → Fatura görüntülenir → Gelir artar
3. İstatistik sekmesinde fatura zaman serisini izle
4. Kod inceleme sekmesinde mimari notlara bak

### Mimari Notu

Streamlit durumu (session_state) içinde: shop nesneleri, müşteri, başlangıç stokları ve olay (event) listesi tutulur.

---

## 🔍 Kod Kalitesi ve Geliştirme Önerilerinin Derinleştirilmesi

Aşağıdaki iyileştirmeler ileride refaktör sırasında uygulanabilir:

| Alan                 | Sorun                             | Öneri                                   |
| -------------------- | --------------------------------- | --------------------------------------- |
| Fatura Hesabı        | Tek metoda çok kural              | `PricingStrategy` sınıfları             |
| İndirim              | Sabit %20 eşik                    | `Rule` nesneleri zinciri                |
| Zaman Hesabı         | `seconds` alanı                   | `total_seconds()` kullan                |
| Girdi                | Model içinde input                | UI tamamen ayrıştır                     |
| Tekil Kiralama       | Customer aynı anda 1 tip kiralama | Çoklu kiralama listesi (Rental nesnesi) |
| Test                 | Zor (I/O karışık)                 | Pure fonksiyon extraction               |
| Magic Numbers        | 10,5 vb gömülü                    | Sabitler veya config                    |
| Uluslararasılaştırma | Sabit İngilizce çıktılar          | Dil dosyası (JSON)                      |

Örnek strateji iskeleti:

```python
class PricingStrategy:
    def compute(self, hours: float, basis: int, count: int) -> float: ...

class CarPricing(PricingStrategy):
    HOURLY = 10
    DAILY_FACTOR = 0.8 * 24
    def compute(self, hours, basis, count):
        if basis == 1:
            return hours * self.HOURLY * count
        return (hours/24) * self.HOURLY * self.DAILY_FACTOR * count
```

---

## 🧪 Hızlı Test Fikri

`returnVehicle` logiğini soyutladıktan sonra pytest ile:

```python
def test_car_daily_two_cars_discount():
    # arrange
    ...
    # act
    # assert
```

---

## ❓ SSS

- Neden Streamlit? -> Hızlı prototip, tek dosyada görsel çıktı.
- Çoklu kullanıcı? -> Şu an state paylaşımı yok; production için backend gerekir.
- Veriler kayboluyor mu? -> Evet, kalıcı depolama eklenmedi.

---

<sub>Web arayüz ilk sürüm: v0.1 (öğrenim amaçlı)</sub>
