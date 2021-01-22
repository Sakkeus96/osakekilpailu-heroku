# -*- coding: utf-8 -*-
import yfinance as yf
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date,timedelta,datetime

# Hakee datan yahoo financesta jokaiselle kuukaudelle
def datan_haku(yritysten_nimet, start, end, salkun_arvot = (3000, 3000)): 
    yritykset = []
    nimet = []
    # Haetaan data yahoo financesta
    for nimi, tikkeri in yritysten_nimet.items():
        yritys = yf.Ticker(tikkeri)
        nimet.append(nimi)
        yritykset.append(yritys)
    # Tallennetaan Dataframeen indeksiksi halutut päivämäärät
    historia = yritykset[0].history(start=start, end=end)
    mun_data = pd.DataFrame(index=historia.index)
    topin_data = pd.DataFrame(index=historia.index)
    # Käydään yhtiöt läpi ja tallennetaan historia tiedot
    for i, yhtiö in enumerate(yritykset[:3]):
        historia = yhtiö.history(start=start, end=end)
        osakkeiden_lkm = salkun_arvot[0]/3/historia[0:1].Close.values[0]
        mun_data[nimet[i]] = historia.Close * osakkeiden_lkm
    for i, yhtiö in enumerate(yritykset[3:]):
        historia = yhtiö.history(start=start, end=end)
        osakkeiden_lkm = salkun_arvot[1]/3/historia[0:1].Close.values[0]
        topin_data[nimet[i+3]] = historia.Close * osakkeiden_lkm
    return mun_data, topin_data

# Luo graafit
def graafit(mun_data, topin_data, kuukausi):
    # Vertailu indeksi
    indeksi = yf.Ticker("^OMXH25").history(start="2020-11-20", end=date.today() + timedelta(days=1))
    indeksi = indeksi.Close
    indeksi = indeksi/indeksi.iloc[0]*3000
    start_eka="2020-11-19" 
    end_eka="2020-12-19"
    start_toka = "2020-12-18"
    end_toka = "2021-01-16"
    start_kolmas = "2021-01-15"
    end_kolmas = date.today() + timedelta(days=1)
    if kuukausi == 1:
        indeksi = indeksi.loc[start_eka:end_eka]
        mun_data = mun_data.iloc[:-1].dropna(how='all', axis=1)
        topin_data = topin_data.iloc[:-1].dropna(how='all', axis=1)
    elif kuukausi == 2:
        indeksi = indeksi.loc[start_toka:end_toka]
        mun_data = mun_data.iloc[1:-1].dropna(how='all', axis=1)
        topin_data = topin_data.iloc[1:-1].dropna(how='all', axis=1)
    elif kuukausi == 3:
        indeksi = indeksi.loc[start_kolmas:end_kolmas]
        mun_data = mun_data.iloc[1:].dropna(how='all', axis=1)
        topin_data = topin_data.iloc[1:].dropna(how='all', axis=1)
    # Koko salkkujen arvo
    fig1, ax = plt.subplots(figsize=(20,10))
    ax.plot(mun_data.sum(axis=1).index,mun_data.sum(axis=1).values)
    ax.plot(topin_data.sum(axis=1).index,topin_data.sum(axis=1).values)
    ax.plot(indeksi)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(["Sakun salkku", "Topin salkku", "OMX Helsinki 25 \n(suhteutettu sal-\nkun kokoon)"], fontsize=17)
    ax.tick_params('x', labelrotation=45)
    ax.set_ylabel("Salkun arvo", fontsize=20)
    ax.grid()
    ax.set_title("Salkkujen arvo", fontsize=20)
    # Yksittäiset yhtiöt mun salkussa
    fig2, ax = plt.subplots(figsize=(20,10))
    ax.plot(mun_data)
    ax.legend(mun_data.columns, fontsize=17)
    ax.tick_params('x', labelrotation=45)
    ax.set_ylabel("Yhtiöiden arvot salkussa", fontsize=20)
    ax.grid()
    ax.set_title("Sakun salkun yhtiöiden arvot", fontsize=20)
    # Yksittäiset yhtiöt topin salkussa
    fig3, ax = plt.subplots(figsize=(20,10))
    ax.plot(topin_data)
    ax.legend(topin_data.columns, fontsize=17)
    ax.tick_params('x', labelrotation=45)
    ax.set_ylabel("Yhtiöiden arvot salkussa", fontsize=20)
    ax.grid()
    ax.set_title("Topin salkun yhtiöiden arvot", fontsize=20)
    return fig1, fig2, fig3

# Luo dataframet
def data_taulukoiden_luonti():
    ensimmäisen_kk_osakkeet = {"Fsecure":"FSC1V.HE", "Tokmanni":"TOKMAN.HE", 
                               "Fortum":"FORTUM.HE", "Suominen":"SUY1V.HE", 
                               "Kamux":"KAMUX.HE", "Vincit":"VINCIT.HE"}
    toisen_kk_osakkeet = {"Rovio":"ROVIO.HE", "Sampo":"SAMPO.HE", 
                          "Telia":"TELIA1.HE", "Leaddesk":"LEADD.HE", 
                          "Efecte":"EFECTE.HE", "Gofore":"GOFORE.HE"}
    kolmannen_kk_osakkeet = {"Nordea":"NDA-FI.HE", "Nokia":"NOKIA.HE", 
                             "UPM":"UPM.HE", "Kamux":"KAMUX.HE", 
                             "Solteq":"SOLTEQ.HE", "Tokmanni":"TOKMAN.HE"}
    # Kunkin kuukauden aloitus ja lopetus
    start_eka="2020-11-19" 
    end_eka="2020-12-19"
    start_toka = "2020-12-18"
    end_toka = "2021-01-16"
    start_kolmas = "2021-01-15"
    end_kolmas = date.today() + timedelta(days=1)
    # Ekan kuukauden data
    mun_data_eka, topin_data_eka = datan_haku(ensimmäisen_kk_osakkeet, start_eka, end_eka)
    mun_salkun_arvo = mun_data_eka.sum(axis=1).iloc[-1]
    topin_salkun_arvo = topin_data_eka.sum(axis=1).iloc[-1]
    # Tokan kuukauden data
    mun_data_toka, topin_data_toka = datan_haku(toisen_kk_osakkeet, start_toka, end_toka, (mun_salkun_arvo, topin_salkun_arvo))
    mun_salkun_arvo = mun_data_toka.sum(axis=1).iloc[-1]
    topin_salkun_arvo = topin_data_toka.sum(axis=1).iloc[-1]
    # Kolmannen kuukauden data
    mun_data_kolmas, topin_data_kolmas = datan_haku(kolmannen_kk_osakkeet, start_kolmas, end_kolmas, (mun_salkun_arvo, topin_salkun_arvo))
    koko_mun_data = pd.concat([mun_data_eka, mun_data_toka, mun_data_kolmas])
    koko_topin_data = pd.concat([topin_data_eka, topin_data_toka, topin_data_kolmas])
    return koko_mun_data, koko_topin_data

def kuukauden_valinta(mun_data, topin_data, kuukausi):
    start_eka="2020-11-19" 
    end_eka="2020-12-19"
    start_toka = "2020-12-18"
    end_toka = "2021-01-16"
    start_kolmas = "2021-01-15"
    end_kolmas = date.today() + timedelta(days=1)
    if kuukausi == 1:
        mun_data = mun_data.loc[start_eka:end_eka]
        topin_data = topin_data.loc[start_eka:end_eka]
    elif kuukausi == 2:
        mun_data = mun_data.loc[start_toka:end_toka]
        topin_data = topin_data.loc[start_toka:end_toka]
    elif kuukausi == 3:
        mun_data = mun_data.loc[start_kolmas:end_kolmas]
        topin_data = topin_data.loc[start_kolmas:end_kolmas]
    return mun_data, topin_data

# Värjää taulukon numeroita
def taulukon_värjäys(val):
    color = 'red' if val < 0 else 'green'
    return 'color: %s' % color

# Värjää kuukauden vaihtumisen
def kuukauden_alotuksen_värjäys(s):
    if s.name in [datetime(2020, 11, 19), datetime(2020, 12, 18), datetime(2021, 1, 15)]:
        return ['background-color: lightsalmon']*3
    else:
        return ['background-color: white']*3
    
def main():
    st.title("Mun ja Topin osakekilpailu")
    st.header("Kilpailun idea")
    st.markdown("""
        Idea on valita kuukauden välein 3 osaketta Helsingin pörssistä, joiden uskoo menestyvän parhaiten siinä kuussa. Salkun
        alkupääoma on 3000 euroa ja kuhunkin osakkeeseen sijoitetaan sama summa aina kuukauden alussa. 
    """)
    st.header("Ohjelman toiminta")
    st.markdown("""
        Ohjelman tarkoituksena on laskea minun ja Topin osakekilpailun tulos
        ohjelman ajohetkellä. Kilpailua voidaan tarkastella kuukausi tasolla tai koko kilpailun tasolla.
    """)
    kuukausi = st.slider("Valitse näytettävä kuukausi. Viimeinen = kaikki kuukaudet", 1, 4, 4)
    mun_data, topin_data = data_taulukoiden_luonti()
    mun_data, topin_data = kuukauden_valinta(mun_data, topin_data, kuukausi)
    fig1, fig2, fig3 = graafit(mun_data, topin_data, kuukausi)
    st.header("Tilanne graafeina")
    st.pyplot(fig1)
    st.pyplot(fig2)
    st.pyplot(fig3)
    
    # Muokataan dataa taulukoita varten
    sarakkeet = mun_data.columns
    mun_data = mun_data[~mun_data.index.duplicated(keep='first')]
    topin_data = topin_data[~topin_data.index.duplicated(keep='first')]
    mun_data["Salkun arvo"] = mun_data.sum(axis=1)
    mun_data = mun_data.drop(sarakkeet, axis=1)
    mun_data["Muutos kisan alusta"] = (mun_data["Salkun arvo"]/3000 - 1)
    sarakkeet = topin_data.columns
    topin_data["Salkun arvo"] = topin_data.sum(axis=1)
    topin_data = topin_data.drop(sarakkeet, axis=1)
    topin_data["Muutos kisan alusta"] = (topin_data["Salkun arvo"]/3000 - 1)
    if kuukausi == 1:
        mun_data["Muutos kk alusta"] = mun_data["Muutos kisan alusta"]
        topin_data["Muutos kk alusta"] = topin_data["Muutos kisan alusta"]
    if kuukausi == 2:
        mun_data["Muutos kk alusta"] = (mun_data["Salkun arvo"]/mun_data.loc["2020-12-18"]["Salkun arvo"] - 1)
        topin_data["Muutos kk alusta"] = (topin_data["Salkun arvo"]/topin_data.loc["2020-12-18"]["Salkun arvo"] - 1)
    if kuukausi == 3:
        mun_data["Muutos kk alusta"] = (mun_data["Salkun arvo"]/mun_data.loc["2021-01-15"]["Salkun arvo"] - 1)
        topin_data["Muutos kk alusta"] = (topin_data["Salkun arvo"]/topin_data.loc["2021-01-15"]["Salkun arvo"] - 1)
    if kuukausi == 4:
        mun_data["Muutos kk alusta"] = mun_data["Muutos kisan alusta"]
        topin_data["Muutos kk alusta"] = topin_data["Muutos kisan alusta"]
    # Muokataan taulukoiden tyyliä
    styler_map = {'Muutos kisan alusta': "{:.2%}", 'Salkun arvo': "{:.2f} €", "Muutos kk alusta": "{:.2%}"}
    mun_data = mun_data.style\
        .applymap(taulukon_värjäys, subset=pd.IndexSlice[:, ["Muutos kisan alusta", "Muutos kk alusta"]])\
        .apply(kuukauden_alotuksen_värjäys, axis=1)\
        .format(styler_map)
    topin_data = topin_data.style\
        .applymap(taulukon_värjäys, subset=pd.IndexSlice[:, ["Muutos kisan alusta", "Muutos kk alusta"]])\
        .apply(kuukauden_alotuksen_värjäys, axis=1)\
        .format(styler_map)\

    st.header("Salkkujen arvot ja niiden kehitys")
    st.markdown("Värjätyt rivit ovat päiviä jolloinka uudet yhtiöt valitaan")
    column_1, column_2 = st.beta_columns(2)
    with column_1:
        st.markdown("""Mun salkun data.""")
        st.dataframe(mun_data)
    with column_2:
        st.markdown("""Topin salkun data""")
        st.dataframe(topin_data)
    
main()