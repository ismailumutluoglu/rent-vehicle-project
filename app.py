import streamlit as st
from datetime import datetime
from vehicle import CarRent, BikeRent, Customer

# --- Para Birimi & Fiyat Sabitleri ---
CURRENCY = "USD"
CURRENCY_SYMBOL = "$"
CAR_HOURLY = 10
CAR_DAILY = CAR_HOURLY * 0.8 * 24          # 192
BIKE_HOURLY = 5
BIKE_DAILY = BIKE_HOURLY * 0.7 * 24        # 84
CAR_DISCOUNT_THRESHOLD = 2
BIKE_DISCOUNT_THRESHOLD = 4
DISCOUNT_RATE = 20


def fmt(amount: float, prec: int = 2) -> str:
    return f"{CURRENCY_SYMBOL} {amount:.{prec}f} {CURRENCY}"


st.set_page_config(page_title="Rent A Car Demo", page_icon="🚗", layout="wide")


def init_state():
    if 'bike_shop' not in st.session_state:
        st.session_state.bike_shop = BikeRent(100)
        st.session_state.car_shop = CarRent(10)
        st.session_state.customer = Customer()
        st.session_state.initial_bike_stock = st.session_state.bike_shop.stock
        st.session_state.initial_car_stock = st.session_state.car_shop.stock
        st.session_state.revenue = 0.0
        st.session_state.events = []  # {time, action, vehicle, qty, bill}


init_state()

bike_shop = st.session_state.bike_shop
car_shop = st.session_state.car_shop
customer = st.session_state.customer

st.title("🚗🛵 Araç Kiralama (Streamlit Arayüz)")
# st.caption("Demo amaçlı basit stok & kiralama simülasyonu. (Saatlik=1, Günlük=2 kodları)")

# Sidebar
with st.sidebar:
    st.header("Stok Durumu")
    c1, c2 = st.columns(2)
    c1.metric("Bisiklet", bike_shop.stock)
    c2.metric("Araba", car_shop.stock)

    util_bike = (st.session_state.initial_bike_stock - bike_shop.stock) / st.session_state.initial_bike_stock * 100
    util_car = (st.session_state.initial_car_stock - car_shop.stock) / st.session_state.initial_car_stock * 100
    st.progress(min(int(util_bike), 100), text=f"Bisiklet kullanım: {util_bike:.1f}%")
    st.progress(min(int(util_car), 100), text=f"Araba kullanım: {util_car:.1f}%")

    st.subheader("Gelir")
    st.metric(f"Toplam Gelir ({CURRENCY})", f"{st.session_state.revenue:.2f}")

    if st.button("Yenile"):
        st.rerun()
    st.caption("Görüntüleme anı: " + datetime.now().strftime('%H:%M:%S'))

    st.subheader(f"Fiyatlar ({CURRENCY})")
    st.markdown(
        f"""
**Bisiklet**  
• Saatlik: {CURRENCY_SYMBOL} {BIKE_HOURLY}  
• Günlük: {CURRENCY_SYMBOL} {BIKE_DAILY:.0f}

**Araba**  
• Saatlik: {CURRENCY_SYMBOL} {CAR_HOURLY}  
• Günlük: {CURRENCY_SYMBOL} {CAR_DAILY:.0f}

**İndirim**  
• {CAR_DISCOUNT_THRESHOLD}+ araba veya {BIKE_DISCOUNT_THRESHOLD}+ bisiklet kiralamalarında iade faturasında %{DISCOUNT_RATE} indirim.  
        """
    )
    st.divider()
    if st.button("Uygulama Durumunu Sıfırla"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


rent_tab, return_tab, stats_tab = st.tabs(["Kiralama", "İade", "İstatistik"])

with rent_tab:
    st.subheader("Araç Kirala")
    vtype = st.selectbox("Araç Türü", ["Bisiklet", "Araba"], key="rent_type")
    basis_label = st.radio("Kiralama Türü", ["Saatlik", "Günlük"], horizontal=True)
    basis = 1 if basis_label == "Saatlik" else 2
    qty = st.number_input("Adet", min_value=1, step=1, value=1)

    if vtype == "Bisiklet":
        hourly = BIKE_HOURLY; daily = BIKE_DAILY
    else:
        hourly = CAR_HOURLY; daily = CAR_DAILY
    st.caption(
        f"Seçilen: {vtype} | Saatlik: {CURRENCY_SYMBOL} {hourly} | Günlük: {CURRENCY_SYMBOL} {daily:.0f} | İndirim Eşiği: {'4+' if vtype=='Bisiklet' else '2+'} (%{DISCOUNT_RATE}) | Para Birimi: {CURRENCY}"
    )

    if st.button("Kirala", type="primary"):
        if vtype == "Bisiklet":
            if customer.rentalTime_b:
                st.warning("Önce mevcut bisiklet kiralamanızı iade edin.")
            elif qty > bike_shop.stock:
                st.error(f"Yeterli stok yok. Kalan: {bike_shop.stock}")
            else:
                rental_time = bike_shop.rentHourly(qty) if basis == 1 else bike_shop.rentDaily(qty)
                if rental_time:
                    customer.rentalTime_b = rental_time
                    customer.rentalBasis_b = basis
                    customer.bikes = qty
                    st.success(f"{qty} bisiklet kiralandı. Başlangıç: {rental_time.strftime('%H:%M:%S')}")
        else:
            if customer.rentalTime_c:
                st.warning("Önce mevcut araba kiralamanızı iade edin.")
            elif qty > car_shop.stock:
                st.error(f"Yeterli stok yok. Kalan: {car_shop.stock}")
            else:
                rental_time = car_shop.rentHourly(qty) if basis == 1 else car_shop.rentDaily(qty)
                if rental_time:
                    customer.rentalTime_c = rental_time
                    customer.rentalBasis_c = basis
                    customer.cars = qty
                    st.success(f"{qty} araba kiralandı. Başlangıç: {rental_time.strftime('%H:%M:%S')}")

    with st.expander("Aktif Kiralamalar"):
        if customer.rentalTime_b:
            st.info(f"Bisiklet: {customer.bikes} adet | Tür: {'Saatlik' if customer.rentalBasis_b==1 else 'Günlük'} | Başlangıç: {customer.rentalTime_b.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.write("Aktif bisiklet kiralaması yok.")
        if customer.rentalTime_c:
            st.info(f"Araba: {customer.cars} adet | Tür: {'Saatlik' if customer.rentalBasis_c==1 else 'Günlük'} | Başlangıç: {customer.rentalTime_c.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.write("Aktif araba kiralaması yok.")

with return_tab:
    st.subheader("Araç İade & Fatura")
    vtype_r = st.selectbox("İade Türü", ["Bisiklet", "Araba"], key="return_type")
    if st.button("İade Et"):
        if vtype_r == "Bisiklet":
            if not customer.rentalTime_b:
                st.warning("İade edilecek bisiklet yok.")
            else:
                bill = bike_shop.returnVehicle(customer.returnVehicle("bike"), "bike")
                if bill is not None:
                    st.session_state.revenue += bill
                    st.session_state.events.append({
                        'time': datetime.now(), 'action': 'return', 'vehicle': 'bike', 'qty': customer.bikes, 'bill': bill
                    })
                    customer.rentalBasis_b = 0; customer.rentalTime_b = 0; customer.bikes = 0
                    st.success(f"Fatura: {fmt(bill)}")
        else:
            if not customer.rentalTime_c:
                st.warning("İade edilecek araba yok.")
            else:
                bill = car_shop.returnVehicle(customer.returnVehicle("car"), "car")
                if bill is not None:
                    st.session_state.revenue += bill
                    st.session_state.events.append({
                        'time': datetime.now(), 'action': 'return', 'vehicle': 'car', 'qty': customer.cars, 'bill': bill
                    })
                    customer.rentalBasis_c = 0; customer.rentalTime_c = 0; customer.cars = 0
                    st.success(f"Fatura: {fmt(bill)}")

with stats_tab:
    st.subheader("İstatistik")
    if st.session_state.events:
        import pandas as pd
        df = pd.DataFrame([
            {'Zaman': e['time'], 'Araç': 'Bisiklet' if e['vehicle']=='bike' else 'Araba', 'Adet': e['qty'], f'Fatura ({CURRENCY})': e['bill']} for e in st.session_state.events
        ])
        st.dataframe(df, use_container_width=True)
        df_rev = df.groupby(df['Zaman'].dt.floor('min'))[f'Fatura ({CURRENCY})'].sum().reset_index()
        st.line_chart(df_rev, x='Zaman', y=f'Fatura ({CURRENCY})')
    else:
        st.info("Henüz veri yok.")

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Bisiklet Kullanım %", f"{(st.session_state.initial_bike_stock - bike_shop.stock)/st.session_state.initial_bike_stock*100:.1f}")
    with c2:
        st.metric("Araba Kullanım %", f"{(st.session_state.initial_car_stock - car_shop.stock)/st.session_state.initial_car_stock*100:.1f}")

# st.caption(f"Demo tamamlandı. Para birimi: {CURRENCY}.")
