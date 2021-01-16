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
def perus_graafit(mun_data, topin_data):
    # Salkkujen kokoarvo
    indeksi = yf.Ticker("^OMXH25").history(start="2020-11-19", end=date.today() + timedelta(days=1))
    indeksi = indeksi.Close
    indeksi = indeksi/indeksi.iloc[0]*3000
    fig1, ax = plt.subplots(figsize=(25,10))
    ax.plot(mun_data.sum(axis=1).index,mun_data.sum(axis=1).values)
    ax.plot(topin_data.sum(axis=1).index,topin_data.sum(axis=1).values)
    ax.plot(indeksi)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(["Sakun salkku", "Topin salkku", "OMX Helsinki 25 \n(suhteutettu sal-\nkun kokoon)"], fontsize=17)
    #ax.legend(["Sakun salkku", "Topin salkku", "OMX Helsinki 25 \n(suhteutettu salkun kokoon)"])
    ax.tick_params('x', labelrotation=45)
    ax.set_ylabel("Salkun arvo")
    ax.grid()
    ax.set_title("Salkkujen arvo")
    # Yksittäiset yhtiöt mun salkussa
    fig2, ax = plt.subplots(figsize=(25,10))
    ax.plot(mun_data)
    ax.legend(mun_data.columns, fontsize=17)
    ax.tick_params('x', labelrotation=45)
    ax.grid()
    ax.set_title("Sakun salkun yhtiöiden arvot")
    # Yksittäiset yhtiöt topin salkussa
    fig3, ax = plt.subplots(figsize=(25,10))
    ax.plot(topin_data)
    ax.legend(topin_data.columns, fontsize=17)
    ax.tick_params('x', labelrotation=45)
    ax.grid()
    ax.set_title("Topin salkun yhtiöiden arvot")
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

# Värjää taulukon numeroita
def taulukon_värjäys(val):
    color = 'red' if val < 0 else 'green'
    return 'color: %s' % color

# Värjää kuukauden vaihtumisen
def kuukauden_alotuksen_värjäys(s):
    if s.name in [datetime(2020, 12, 18), datetime(2021, 1, 15)]:
        return ['background-color: lightsalmon']*2
    else:
        return ['background-color: white']*2
    
def main():
    st.title("Mun ja Topin osakekilpailu")
    st.markdown("""
    Ohjelman tarkoituksena on laskea minun ja Topin osakekilpailun tulos
    ohjelman ajohetkellä
                """)
    mun_data, topin_data = data_taulukoiden_luonti()
    fig1, fig2, fig3 = perus_graafit(mun_data, topin_data)
    st.pyplot(fig1)
    st.pyplot(fig2)
    st.pyplot(fig3)
    
    # Muokataan mun data siistimpään muotoon
    styler_map = {'Nousu/lasku kk alusta %': "{:.2%}", 'Nousu/lasku kisan alusta %': "{:.2%}"}
    sarakkeet = mun_data.columns
    mun_data = mun_data[~mun_data.index.duplicated(keep='first')]
    topin_data = topin_data[~topin_data.index.duplicated(keep='first')]
    mun_data["Salkun arvo"] = mun_data.sum(axis=1)
    mun_data = mun_data.drop(sarakkeet, axis=1)
    mun_data["Nousu/lasku kisan alusta %"] = (mun_data["Salkun arvo"]/3000 - 1)
    mun_data = mun_data.style\
        .applymap(taulukon_värjäys, subset=pd.IndexSlice[:, ["Nousu/lasku kisan alusta %"]])\
        .apply(kuukauden_alotuksen_värjäys, axis=1)\
        .format("{:.2f} €", subset=["Salkun arvo"])\
        .format(styler_map)
    sarakkeet = topin_data.columns
    topin_data["Salkun arvo"] = topin_data.sum(axis=1)
    topin_data = topin_data.drop(sarakkeet, axis=1)
    topin_data["Nousu/lasku kisan alusta %"] = (topin_data["Salkun arvo"]/3000 - 1)
    topin_data = topin_data.style\
        .applymap(taulukon_värjäys, subset=pd.IndexSlice[:, ["Nousu/lasku kisan alusta %"]])\
        .apply(kuukauden_alotuksen_värjäys, axis=1)\
        .format("{:.2f} €", subset=["Salkun arvo"])\
        .format(styler_map)\

    st.markdown("""
    Mun salkun data. Värjätyt rivit ovat päiviä jolloinka uudet yhtiöt valitaan
                """)
    st.dataframe(mun_data)
    st.markdown("""
    Topin salkun data. Värjätyt rivit ovat päiviä jolloinka uudet yhtiöt valitaan
                """)
    st.dataframe(topin_data)
    
main()