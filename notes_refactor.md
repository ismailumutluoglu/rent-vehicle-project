# Refactor Öneri Notları (Derin)

Bu dosya; mevcut kodu incelerken tespit edilen olası refaktör adımlarının teknik kırılımını içerir.

## 1. Sorun Noktaları

- Fatura hesaplama tek metoda (VehicleRent.returnVehicle) sıkışmış durumda.
- Brand (car/bike) branching kod tekrarı yaratıyor.
- Zaman hesaplamasında `seconds` kullanımı gün aşımı durumlarını eksik yapabilir.
- `Customer` sadece tek bir aktif kiralama tutuyor (bisiklet ve araba ayrı state alanları ile). Çok sayıda kiralama senaryosu zor.
- İş mantığı ile kullanıcı etkileşimi (input) kısmen iç içe.

## 2. Hedef Model Taslağı

```python
class Rental:
    def __init__(self, vehicle_type: str, count: int, basis: int, start: datetime):
        self.vehicle_type = vehicle_type  # car / bike
        self.count = count
        self.basis = basis  # 1=hourly 2=daily
        self.start = start

class Inventory:
    def __init__(self):
        self._stocks = { 'car': 10, 'bike': 100 }
    def reserve(self, t, n): ...
    def release(self, t, n): ...

class PricingRegistry:
    strategies = { }
    @classmethod
    def register(cls, name, strat): cls.strategies[name]=strat
    @classmethod
    def price(cls, name, hours, basis, count): return cls.strategies[name].compute(hours,basis,count)
```

## 3. Adım Adım Refactor Planı

1. `returnVehicle` içindeki fiyat/miktar hesap kodunu ayrı saf fonksiyonlara taşı.
2. Araç bazlı sabitleri (hourly rate, discount threshold, discount rate) sabitler modülüne çıkar.
3. `Customer` içinde bisiklet/araba alanları yerine `self.active_rentals: list[Rental]` kullan.
4. Fatura hesaplama: `generate_bill(rental: Rental, now: datetime) -> float`.
5. Testleri ekle (happy path + edge: negatif qty, aşırı qty, iki kiralama vs.).
6. CLI/Streamlit adaptasyonu: yeni API'yi kullanacak şekilde güncelle.

## 4. Edge Case Listesi

- 0 veya negatif adet.
- Stoktan fazla istek.
- İade edilmeyen kiralama için tekrar iade isteği.
- Çok kısa (örn. 10 saniye) kiralama – oransal fiyat.
- Büyük saat farkı (24h üzeri) – daily oran doğru hesaplanmalı.

## 5. Örnek Saf Faturalama Fonksiyonu

```python
from dataclasses import dataclass

def compute_period_hours(start, end):
    return (end - start).total_seconds() / 3600

def price_hourly(hours, rate):
    return hours * rate

def price_daily(hours, daily_rate):
    return (hours / 24) * daily_rate
```

## 6. Test Örneği Taslağı

```python
import datetime as dt
from pricing import compute_bill

def test_discount_applied():
    start = dt.datetime.now() - dt.timedelta(hours=5)
    rental = Rental('car', 2, 1, start)
    bill = compute_bill(rental, dt.datetime.now())
    assert bill < 2 * 5 * 10  # %20 indirim
```

## 7. Sonraki Olasılıklar

- Persistans (SQLite veya JSON dosya)
- REST API (FastAPI) + frontend
- Kullanıcı kimliği & birden fazla müşteri

---

Bu doküman öğrenim amaçlıdır; uygulama ölçeklendikçe güncellenmelidir.
