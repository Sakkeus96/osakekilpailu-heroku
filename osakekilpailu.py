# -*- coding: utf-8 -*-
import yfinance as yf
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
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
        historia = historia.dropna()
        osakkeiden_lkm = salkun_arvot[0]/3/historia[0:1].Close.values[0]
        mun_data[nimet[i]] = historia.Close * osakkeiden_lkm
        mun_data = mun_data.loc[~mun_data.index.duplicated()]
    for i, yhtiö in enumerate(yritykset[3:]):
        historia = yhtiö.history(start=start, end=end)
        historia = historia.dropna()
        osakkeiden_lkm = salkun_arvot[1]/3/historia[0:1].Close.values[0]
        topin_data[nimet[i+3]] = historia.Close * osakkeiden_lkm
        topin_data = topin_data.loc[~topin_data.index.duplicated()]
    return mun_data, topin_data

# Luo graafit
def graafit(mun_data, topin_data, kuukausi):
    # Vertailu indeksi
    indeksi = yf.Ticker("^OMXH25").history(start="2020-11-20", end=date.today() + timedelta(days=1))
    indeksi = indeksi.Close
    indeksi = indeksi/indeksi.iloc[0]*3000
    # Kuukausi muokkaukset sama päivä seuraavan kuun alkuun ja vanhan loppuun
    start_eka="2020-11-19" 
    end_eka="2020-12-19"
    start_toka = "2020-12-18"
    end_toka = "2021-01-16"
    start_kolmas = "2021-01-15"
    end_kolmas = "2021-02-16"
    start_neljäs = "2021-02-15"
    end_neljäs = "2021-03-15"
    start_viides = "2021-03-15"
    end_viides = "2021-04-15"
    start_kuudes = "2021-04-15"
    end_kuudes = date.today() + timedelta(days=1)
    # Kuukausi muokkaukset
    if kuukausi == 1:
        indeksi = indeksi.loc[start_eka:end_eka]
        mun_data = mun_data.iloc[:,:3]
        topin_data = topin_data.iloc[:,:3]
    elif kuukausi == 2:
        indeksi = indeksi.loc[start_toka:end_toka]
        mun_data = mun_data.iloc[:,3:6]
        topin_data = topin_data.iloc[:,3:6]
    elif kuukausi == 3:
        indeksi = indeksi.loc[start_kolmas:end_kolmas]
        mun_data = mun_data.iloc[:,6:9]
        topin_data = topin_data.iloc[:,6:9]
    elif kuukausi == 4:
        indeksi = indeksi.loc[start_neljäs:end_neljäs]
        mun_data = mun_data.iloc[:,9:12]
        topin_data = topin_data.iloc[:,9:12]
    elif kuukausi == 5:
        indeksi = indeksi.loc[start_viides:end_viides]
        mun_data = mun_data.iloc[:,12:15]
        topin_data = topin_data.iloc[:,12:15]
    elif kuukausi == 6:
        indeksi = indeksi.loc[start_kuudes:end_kuudes]
        mun_data = mun_data.iloc[:,15:18]
        topin_data = topin_data.iloc[:,15:18]

    # Koko salkkujen arvo
    fig1, ax = plt.subplots(figsize=(20,10))
    mun_data_summa = mun_data.sum(axis=1)
    mask = mun_data_summa > 6000
    mun_data_summa[mask] = mun_data_summa[mask]/2
    topin_data_summa = topin_data.sum(axis=1)
    mask = topin_data_summa > 6000
    topin_data_summa[mask] = topin_data_summa[mask]/2
    ax.plot(mun_data_summa.index, (mun_data_summa.values/mun_data_summa.iloc[0] - 1)*100)
    ax.plot(topin_data_summa.index, (topin_data_summa.values/topin_data_summa.iloc[0] - 1)*100)
    ax.plot((indeksi/indeksi.iloc[0] - 1)*100)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(["Sakun salkku", "Topin salkku", "OMX Helsinki 25"], fontsize=17)
    ax.tick_params('x', labelrotation=45)
    ax.set_ylabel("Salkun arvon nousu/lasku %", fontsize=20)
    ax.grid()
    ax.set_title("Salkkujen kehitys", fontsize=20)

    # Yksittäiset yhtiöt mun salkussa
    sarakkeiden_määrä = int(len(mun_data.columns))
    fig2, ax = plt.subplots(figsize=(20,10))
    for i in range(0, sarakkeiden_määrä, 3):
        yhden_kuukauden_yhtiöt = mun_data.iloc[:,i:i+3].dropna(how='all', axis=0)
        ax.plot((yhden_kuukauden_yhtiöt.div(yhden_kuukauden_yhtiöt.iloc[0]) - 1)*100)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.legend(mun_data.columns, fontsize=17, ncol=int(sarakkeiden_määrä/3))
    ax.tick_params('x', labelrotation=45)
    ax.set_ylabel("Yhtiöiden kasvu/lasku %", fontsize=20)
    ax.grid()
    ax.set_title("Sakun salkun yhtiöiden kehitys", fontsize=20)
    # Yksittäiset yhtiöt topin salkussa
    fig3, ax = plt.subplots(figsize=(20,10))
    for i in range(0, sarakkeiden_määrä, 3):
        yhden_kuukauden_yhtiöt = topin_data.iloc[:,i:i+3].dropna(how='all', axis=0)
        ax.plot((yhden_kuukauden_yhtiöt.div(yhden_kuukauden_yhtiöt.iloc[0]) - 1)*100)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.legend(topin_data.columns, fontsize=17, ncol=int(sarakkeiden_määrä/3))
    ax.tick_params('x', labelrotation=45)
    ax.set_ylabel("Yhtiöiden kasvu/lasku %", fontsize=20)
    ax.grid()
    ax.set_title("Topin salkun yhtiöiden kehitys", fontsize=20)
    return fig1, fig2, fig3

# Luo dataframet
@st.cache
def data_taulukoiden_luonti():
    # Kuukausi muokkaukset
    ensimmäisen_kk_osakkeet = {"Fsecure":"FSC1V.HE", "Tokmanni":"TOKMAN.HE", 
                               "Fortum":"FORTUM.HE", "Suominen":"SUY1V.HE", 
                               "Kamux":"KAMUX.HE", "Vincit":"VINCIT.HE"}
    toisen_kk_osakkeet = {"Rovio":"ROVIO.HE", "Sampo":"SAMPO.HE", 
                          "Telia":"TELIA1.HE", "Leaddesk":"LEADD.HE", 
                          "Efecte":"EFECTE.HE", "Gofore":"GOFORE.HE"}
    kolmannen_kk_osakkeet = {"Nordea":"NDA-FI.HE", "Nokia":"NOKIA.HE", 
                             "UPM":"UPM.HE", "Kamux":"KAMUX.HE", 
                             "Solteq":"SOLTEQ.HE", "Tokmanni":"TOKMAN.HE"}
    neljännen_kk_osakkeet = {"Sampo":"SAMPO.HE", "TietoEvry":"TIETO.HE", 
                             "Marimekko":"MEKKO.HE", "Honkarakenne":"HONBS.HE", 
                             "Ilkka-Yhtymä":"ILK2S.HE", "Incap":"ICP1V.HE"}
    viidennen_kk_osakkeet = {"Neste":"NESTE.HE", "Qt-Group":"QTCOM.HE", 
                             "Keskob":"KESKOB.HE", "Honkarakenne":"HONBS.HE", 
                             "Nixu":"NIXU.HE", "Aktia Pankki":"AKTIA.HE"}
    kuudennen_kk_osakkeet = {"UPM":"UPM.HE", "Kemira":"KEMIRA.HE", 
                             "Alma Media":"ALMA.HE", "Talenom":"TNOM.HE", 
                             "Oma säästöpankki":"OMASP.HE", "Avidly":"AVIDLY.HE"}
                             

    # Kunkin kuukauden aloitus ja lopetus
    # Kuukausi muokkaukset
    start_eka="2020-11-19" 
    end_eka="2020-12-19"
    start_toka = "2020-12-18"
    end_toka = "2021-01-16"
    start_kolmas = "2021-01-15"
    end_kolmas = "2021-02-16"
    start_neljäs = "2021-02-15"
    end_neljäs = "2021-03-16"
    start_viides = "2021-03-15"
    end_viides = "2021-04-16"
    start_kuudes = "2021-04-15"
    end_kuudes = date.today() + timedelta(days=1)

    # Kuukausi muokkaukset
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
    mun_salkun_arvo = mun_data_kolmas.sum(axis=1).iloc[-1]
    topin_salkun_arvo = topin_data_kolmas.sum(axis=1).iloc[-1]

    # Neljännen kuukauden data
    mun_data_neljäs, topin_data_neljäs = datan_haku(neljännen_kk_osakkeet, start_neljäs, end_neljäs, (mun_salkun_arvo, topin_salkun_arvo))
    mun_salkun_arvo = mun_data_neljäs.sum(axis=1).iloc[-1]
    topin_salkun_arvo = topin_data_neljäs.sum(axis=1).iloc[-1]

    # Viidennen kuukauden data
    mun_data_viides, topin_data_viides = datan_haku(viidennen_kk_osakkeet, start_viides, end_viides, (mun_salkun_arvo, topin_salkun_arvo))
    mun_salkun_arvo = mun_data_viides.sum(axis=1).iloc[-1]
    topin_salkun_arvo = topin_data_viides.sum(axis=1).iloc[-1]

    # Kuudennen kuukauden data
    mun_data_kuudes, topin_data_kuudes = datan_haku(kuudennen_kk_osakkeet, start_kuudes, end_kuudes, (mun_salkun_arvo, topin_salkun_arvo))
    koko_mun_data = pd.concat([mun_data_eka, mun_data_toka, mun_data_kolmas, mun_data_neljäs, mun_data_viides, mun_data_kuudes], axis=1)
    koko_topin_data = pd.concat([topin_data_eka, topin_data_toka, topin_data_kolmas, topin_data_neljäs, topin_data_viides, topin_data_kuudes], axis=1)
    return koko_mun_data, koko_topin_data

def kuukauden_valinta(mun_data, topin_data, kuukausi):
    # Kuukausi muokkaukset
    start_eka="2020-11-19" 
    end_eka="2020-12-19"
    start_toka = "2020-12-18"
    end_toka = "2021-01-16"
    start_kolmas = "2021-01-15"
    end_kolmas = "2021-02-15"
    start_neljäs = "2021-02-15"
    end_neljäs = "2021-03-15"
    start_viides = "2021-03-15"
    end_viides = "2021-04-15"
    start_kuudes = "2021-04-15"
    end_kuudes = date.today() + timedelta(days=1)
    # Kuukausi muokkaukset
    if kuukausi == 1:
        mun_data = mun_data.loc[start_eka:end_eka]
        topin_data = topin_data.loc[start_eka:end_eka]
    elif kuukausi == 2:
        mun_data = mun_data.loc[start_toka:end_toka]
        topin_data = topin_data.loc[start_toka:end_toka]
    elif kuukausi == 3:
        mun_data = mun_data.loc[start_kolmas:end_kolmas]
        topin_data = topin_data.loc[start_kolmas:end_kolmas]
    elif kuukausi == 4:
        mun_data = mun_data.loc[start_neljäs:end_neljäs]
        topin_data = topin_data.loc[start_neljäs:end_neljäs]
    elif kuukausi == 5:
        mun_data = mun_data.loc[start_viides:end_viides]
        topin_data = topin_data.loc[start_viides:end_viides]
    elif kuukausi == 6:
        mun_data = mun_data.loc[start_kuudes:end_kuudes]
        topin_data = topin_data.loc[start_kuudes:end_kuudes]
    return mun_data, topin_data

# Värjää taulukon numeroita
def taulukon_värjäys(val):
    color = 'red' if val < 0 else 'green'
    return 'color: %s' % color

# Värjää kuukauden vaihtumisen
def kuukauden_alotuksen_värjäys(s):
    # Kuukausi muokkaukset
    if s.name in [datetime(2020, 11, 19), datetime(2020, 12, 18), datetime(2021, 1, 15), datetime(2021, 2, 15), datetime(2021, 3, 15), datetime(2021, 4, 15)]:
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
    # Kuukausi muokkaukset
    kuukausi = st.slider("Valitse näytettävä kuukausi. Viimeinen = kaikki kuukaudet", 1, 7, 7)
    mun_data, topin_data = data_taulukoiden_luonti()
    mun_data, topin_data = kuukauden_valinta(mun_data, topin_data, kuukausi)
    fig1, fig2, fig3 = graafit(mun_data, topin_data, kuukausi)
    st.header("Tilanne graafeina")
    st.pyplot(fig1)
    st.pyplot(fig2)
    st.pyplot(fig3)
    
    # Muokataan dataa taulukoita varten
    mun_data = mun_data[~mun_data.index.duplicated(keep='first')]
    topin_data = topin_data[~topin_data.index.duplicated(keep='first')]
    mun_kehitys = pd.DataFrame()
    mun_data_summa = mun_data.sum(axis=1)
    mask = mun_data_summa > 6000
    mun_data_summa[mask] = mun_data_summa[mask]/2
    mun_kehitys["Salkun arvo"] = mun_data_summa
    mun_kehitys["Muutos kisan alusta"] = (mun_kehitys["Salkun arvo"]/3000 - 1)
    topin_kehitys = pd.DataFrame()
    topin_data_summa = topin_data.sum(axis=1)
    mask = topin_data_summa > 6000
    topin_data_summa[mask] = topin_data_summa[mask]/2
    topin_kehitys["Salkun arvo"] = topin_data_summa
    topin_kehitys["Muutos kisan alusta"] = (topin_kehitys["Salkun arvo"]/3000 - 1)
    # Kuukausi muokkaukset
    if kuukausi == 1:
        mun_kehitys["Muutos kk alusta"] = mun_kehitys["Muutos kisan alusta"]
        topin_kehitys["Muutos kk alusta"] = topin_kehitys["Muutos kisan alusta"]
    if kuukausi == 2:
        mun_kehitys["Muutos kk alusta"] = (mun_kehitys["Salkun arvo"]/mun_kehitys.loc["2020-12-18"]["Salkun arvo"] - 1)
        topin_kehitys["Muutos kk alusta"] = (topin_kehitys["Salkun arvo"]/topin_kehitys.loc["2020-12-18"]["Salkun arvo"] - 1)
    if kuukausi == 3:
        mun_kehitys["Muutos kk alusta"] = (mun_kehitys["Salkun arvo"]/mun_kehitys.loc["2021-01-15"]["Salkun arvo"] - 1)
        topin_kehitys["Muutos kk alusta"] = (topin_kehitys["Salkun arvo"]/topin_kehitys.loc["2021-01-15"]["Salkun arvo"] - 1)
    if kuukausi == 4:
        mun_kehitys["Muutos kk alusta"] = (mun_kehitys["Salkun arvo"]/mun_kehitys.loc["2021-02-15"]["Salkun arvo"] - 1)
        topin_kehitys["Muutos kk alusta"] = (topin_kehitys["Salkun arvo"]/topin_kehitys.loc["2021-02-15"]["Salkun arvo"] - 1)
    if kuukausi == 5:
        mun_kehitys["Muutos kk alusta"] = (mun_kehitys["Salkun arvo"]/mun_kehitys.loc["2021-03-15"]["Salkun arvo"] - 1)
        topin_kehitys["Muutos kk alusta"] = (topin_kehitys["Salkun arvo"]/topin_kehitys.loc["2021-03-15"]["Salkun arvo"] - 1)
    if kuukausi == 6:
        mun_kehitys["Muutos kk alusta"] = (mun_kehitys["Salkun arvo"]/mun_kehitys.loc["2021-04-15"]["Salkun arvo"] - 1)
        topin_kehitys["Muutos kk alusta"] = (topin_kehitys["Salkun arvo"]/topin_kehitys.loc["2021-04-15"]["Salkun arvo"] - 1)
    if kuukausi == 7:
        mun_kehitys["Muutos kk alusta"] = mun_kehitys["Muutos kisan alusta"]
        topin_kehitys["Muutos kk alusta"] = topin_kehitys["Muutos kisan alusta"]

    # Muokataan taulukoiden tyyliä
    styler_map = {'Muutos kisan alusta': "{:.2%}", 'Salkun arvo': "{:.2f} €", "Muutos kk alusta": "{:.2%}"}
    mun_kehitys = mun_kehitys.style\
        .applymap(taulukon_värjäys, subset=pd.IndexSlice[:, ["Muutos kisan alusta", "Muutos kk alusta"]])\
        .apply(kuukauden_alotuksen_värjäys, axis=1)\
        .format(styler_map)
    topin_kehitys = topin_kehitys.style\
        .applymap(taulukon_värjäys, subset=pd.IndexSlice[:, ["Muutos kisan alusta", "Muutos kk alusta"]])\
        .apply(kuukauden_alotuksen_värjäys, axis=1)\
        .format(styler_map)

    # Taulukoiden renderöinti
    st.header("Salkkujen arvot ja niiden kehitys")
    st.markdown("Värjätyt rivit ovat päiviä jolloinka uudet yhtiöt valitaan")
    st.markdown("""Mun salkun data.""")
    st.dataframe(mun_kehitys)
    st.markdown("""Topin salkun data""")
    st.dataframe(topin_kehitys)
    
main()