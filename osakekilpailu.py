# -*- coding: utf-8 -*-
import yfinance as yf
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date,timedelta 

# Nimetään yhtiöt sitä varten, että saadaan sarakkeet Dataframeen
nimet = ["Rovio", "Sampo", "Telia", "Leaddesk", "Efecte", "Gofore"]

def datan_haku():  
    # Haetaan yahoo financesta tiedot
    rovio = yf.Ticker("ROVIO.HE")
    sampo = yf.Ticker("SAMPO.HE")
    telia = yf.Ticker("TELIA1.HE")
    leaddesk = yf.Ticker("LEADD.HE")
    efecte = yf.Ticker("EFECTE.HE")
    gofore = yf.Ticker("GOFORE.HE")
    # Haetaan alla olevalta aikaväliltä historia data ja tallennetaan Dataframeen indeksiksi päivämäärät
    historia = rovio.history(start="2020-12-18", end=date.today() + timedelta(days=1))
    mun_data = pd.DataFrame(index=historia.index)
    topin_data = pd.DataFrame(index=historia.index)
    # Käydään yhtiöt läpi ja tallennetaan historia tiedot
    for i, yhtiö in enumerate([rovio, sampo, telia]):
        historia = yhtiö.history(start="2020-12-18", end=date.today() + timedelta(days=1))
        osakkeiden_lkm = 3129.315/3/historia[0:1].Close.values[0]
        mun_data[nimet[i]] = historia.Close * osakkeiden_lkm
    for i, yhtiö in enumerate([leaddesk, efecte, gofore]):
        historia = yhtiö.history(start="2020-12-18", end=date.today() + timedelta(days=1))
        osakkeiden_lkm = 3105.793/3/historia[0:1].Close.values[0]
        topin_data[nimet[i+3]] = historia.Close * osakkeiden_lkm
    return mun_data, topin_data

def perus_graafit(mun_data, topin_data):
    fig, ax = plt.subplots(3, figsize=(13,20))
    ax[0].plot(mun_data.sum(axis=1).index,mun_data.sum(axis=1).values)
    ax[0].plot(topin_data.sum(axis=1).index,topin_data.sum(axis=1).values)
    ax[0].legend(["Sakun salkku", "Topin salkku"])
    ax[0].tick_params('x', labelrotation=45)
    ax[0].set_ylabel("Salkun arvo")
    ax[0].grid()
    ax[0].set_title("Salkkujen arvo")
    ax[1].plot(mun_data)
    ax[1].legend(nimet[:3])
    ax[1].tick_params('x', labelrotation=45)
    ax[1].grid()
    ax[1].set_title("Sakun salkun yhtiöiden arvot")
    ax[2].plot(topin_data)
    ax[2].legend(nimet[3:])
    ax[2].tick_params('x', labelrotation=45)
    ax[2].grid()
    ax[2].set_title("Topin salkun yhtiöiden arvot")
    return fig

def main():
    st.title("Mun ja Topin osakekilpailu")
    st.markdown("""
    Ohjelman tarkoituksena on laskea minun ja Topin osakekilpailun tulos
    ohjelman ajohetkellä
                """)
    mun_data, topin_data = datan_haku()
    fig = perus_graafit(mun_data, topin_data)
    st.pyplot(fig)
    
    mun_data["Salkun arvo"] = mun_data.sum(axis=1)
    mun_data["Nousu/lasku kk alusta %"] = (mun_data["Salkun arvo"]/3129.315 - 1)*100
    mun_data["Nousu/lasku kisan alusta %"] = (mun_data["Salkun arvo"]/3000 - 1)*100
    topin_data["Salkun arvo"] = topin_data.sum(axis=1)
    topin_data["Nousu/lasku kk alusta %"] = (topin_data["Salkun arvo"]/3105.793 - 1)*100
    topin_data["Nousu/lasku kisan alusta %"] = (topin_data["Salkun arvo"]/3000 - 1)*100
    
    st.markdown("""
    Mun salkun data
                """)
    st.dataframe(mun_data)
    st.markdown("""
    Topin salkun data
                """)
    st.dataframe(topin_data)
    
main()