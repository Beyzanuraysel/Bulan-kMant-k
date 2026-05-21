import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# =========================
# VERI SETI OKUMA
# =========================

df = pd.read_csv(r"C:\Users\Lenovo\Desktop\beyzabulanık mantık\Traffic.csv")

# =========================
# BASLIK
# =========================

st.title("🚦 Akıllı Trafik Işığı Kontrol Sistemi")
st.write("Bulanık Mantık ile Trafik Yoğunluğu Analizi")

# =========================
# VERI SETI GOSTER
# =========================

st.subheader("📊 Veri Seti Önizleme")
st.dataframe(df.head())

# =========================
# TRAFIK GRAFIGI
# =========================

st.subheader("📈 Trafik Yoğunluğu Grafiği")

numeric_columns = df.select_dtypes(include=np.number).columns

if len(numeric_columns) > 0:

    selected_column = st.selectbox(
        "Grafik için sütun seç",
        numeric_columns
    )

    fig2, ax2 = plt.subplots(figsize=(8,4))

    ax2.plot(df[selected_column].head(50))

    ax2.set_title(selected_column)

    st.pyplot(fig2)

# =========================
# BULANIK MANTIK
# =========================

trafik = ctrl.Antecedent(np.arange(0, 101, 1), 'trafik')
yaya = ctrl.Antecedent(np.arange(0, 101, 1), 'yaya')
bekleme = ctrl.Antecedent(np.arange(0, 61, 1), 'bekleme')

yesil = ctrl.Consequent(np.arange(10, 91, 1), 'yesil')

# =========================
# UYELIK FONKSIYONLARI
# =========================

trafik['dusuk'] = fuzz.trimf(trafik.universe, [0, 0, 40])
trafik['orta'] = fuzz.trimf(trafik.universe, [30, 50, 70])
trafik['yuksek'] = fuzz.trimf(trafik.universe, [60, 100, 100])

yaya['az'] = fuzz.trimf(yaya.universe, [0, 0, 40])
yaya['normal'] = fuzz.trimf(yaya.universe, [30, 50, 70])
yaya['fazla'] = fuzz.trimf(yaya.universe, [60, 100, 100])

bekleme['kisa'] = fuzz.trimf(bekleme.universe, [0, 0, 20])
bekleme['orta'] = fuzz.trimf(bekleme.universe, [15, 30, 45])
bekleme['uzun'] = fuzz.trimf(bekleme.universe, [40, 60, 60])

yesil['kisa'] = fuzz.trimf(yesil.universe, [10, 10, 35])
yesil['normal'] = fuzz.trimf(yesil.universe, [30, 50, 70])
yesil['uzun'] = fuzz.trimf(yesil.universe, [60, 90, 90])

# =========================
# KURALLAR
# =========================

rules = [

    ctrl.Rule(trafik['dusuk'] & yaya['az'] & bekleme['kisa'], yesil['kisa']),
    ctrl.Rule(trafik['orta'] & yaya['az'] & bekleme['kisa'], yesil['normal']),
    ctrl.Rule(trafik['yuksek'] & yaya['az'], yesil['uzun']),
    ctrl.Rule(trafik['yuksek'] & bekleme['uzun'], yesil['uzun']),
    ctrl.Rule(trafik['dusuk'] & yaya['fazla'], yesil['kisa']),
    ctrl.Rule(trafik['orta'] & yaya['normal'], yesil['normal']),
    ctrl.Rule(trafik['yuksek'] & yaya['fazla'], yesil['uzun']),
    ctrl.Rule(bekleme['uzun'], yesil['uzun']),
    ctrl.Rule(bekleme['kisa'] & trafik['dusuk'], yesil['kisa']),
    ctrl.Rule(trafik['orta'] & bekleme['orta'], yesil['normal']),
    ctrl.Rule(trafik['yuksek'] & bekleme['orta'], yesil['uzun']),
    ctrl.Rule(trafik['dusuk'] & bekleme['uzun'], yesil['normal']),
    ctrl.Rule(yaya['fazla'] & trafik['dusuk'], yesil['kisa']),
    ctrl.Rule(yaya['az'] & trafik['yuksek'], yesil['uzun']),
    ctrl.Rule(trafik['orta'] & yaya['fazla'] & bekleme['uzun'], yesil['uzun'])

]

# =========================
# SISTEM
# =========================

traffic_ctrl = ctrl.ControlSystem(rules)
traffic_sim = ctrl.ControlSystemSimulation(traffic_ctrl)

# =========================
# SLIDERLAR
# =========================

st.subheader("🎛 Giriş Değerleri")

trafik_input = st.slider("Trafik Yoğunluğu", 0, 100, 50)
yaya_input = st.slider("Yaya Yoğunluğu", 0, 100, 40)
bekleme_input = st.slider("Bekleme Süresi", 0, 60, 20)

# =========================
# HESAPLAMA
# =========================

if st.button("Hesapla"):

    traffic_sim.input['trafik'] = trafik_input
    traffic_sim.input['yaya'] = yaya_input
    traffic_sim.input['bekleme'] = bekleme_input

    traffic_sim.compute()

    sonuc = traffic_sim.output['yesil']

    st.success(f"🚦 Yeşil Işık Süresi: {sonuc:.2f} saniye")

    # =========================
    # AKTIF KURALLAR
    # =========================

    st.subheader("📋 Aktif Kurallar")

    for i, rule in enumerate(rules):
        st.write(f"Kural {i+1}: {rule}")

# =========================
# UYELIK FONKSIYONU GRAFIGI
# =========================

st.subheader("📉 Üyelik Fonksiyonları")

fig, ax = plt.subplots(figsize=(8,4))

for term in trafik.terms:

    ax.plot(
        trafik.universe,
        trafik[term].mf,
        label=term
    )

ax.legend()

ax.set_xlabel("Trafik")
ax.set_ylabel("Üyelik Derecesi")

st.pyplot(fig)