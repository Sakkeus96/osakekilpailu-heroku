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
    mun_osinko = 0
    topin_osinko = 0

    # Käydään yhtiöt läpi ja tallennetaan historia tiedot
    for i, yhtiö in enumerate(yritykset[:3]):
        historia = yhtiö.history(start=start, end=end)
        historia = historia.dropna()
        osakkeiden_lkm = salkun_arvot[0]/3/historia[0:1].Close.values[0]
        osinko = historia[historia.Dividends > 0]
        if not osinko.empty:
            mun_osinko += osinko.Dividends.iloc[0]*osakkeiden_lkm
        mun_data[nimet[i]] = historia.Close * osakkeiden_lkm
        mun_data = mun_data.loc[~mun_data.index.duplicated()]
    for i, yhtiö in enumerate(yritykset[3:]):
        historia = yhtiö.history(start=start, end=end)
        historia = historia.dropna()
        osakkeiden_lkm = salkun_arvot[1]/3/historia[0:1].Close.values[0]
        osinko = historia[historia.Dividends > 0]
        if not osinko.empty:
            topin_osinko += osinko.Dividends.iloc[0]*osakkeiden_lkm
        topin_data[nimet[i+3]] = historia.Close * osakkeiden_lkm
        topin_data = topin_data.loc[~topin_data.index.duplicated()]
    return mun_data, topin_data, mun_osinko, topin_osinko

# Luo graafit
def graafit(mun_data, topin_data, kuukausi):
    # Vertailu indeksi
    indeksi = yf.Ticker("^OMXH25").history(start="2020-11-20", end=date.today() + timedelta(days=1))
    indeksi = indeksi.Close
    indeksi = indeksi/indeksi.iloc[0]*3000
    # Kuukausi muokkaukset TÄMÄ VAIKUTTAA VAAN INDEKSIIN
    ostot_ja_myynnit = [("2020-11-19","2020-12-19"), ("2020-12-18","2021-01-16"), ("2021-01-15","2021-02-16"), ("2021-02-15","2021-03-15"), ("2021-03-15","2021-04-15"),
                    ("2021-04-15","2021-05-15"), ("2021-05-14","2021-06-14"), ("2021-06-15","2021-07-14"), ("2021-07-15","2021-08-16"), ("2021-08-16","2021-09-20"),
                    ("2021-09-20","2021-10-18"), ("2021-10-18","2021-11-15"), ("2021-11-15","2021-12-15"), ("2021-12-15","2022-01-14"), ("2022-01-14",date.today() + timedelta(days=1))]
    pituus = len(ostot_ja_myynnit)
    if kuukausi <= pituus:
        indeksi = indeksi.loc[ostot_ja_myynnit[kuukausi - 1][0]:ostot_ja_myynnit[kuukausi - 1][1]]
        mun_data = mun_data.iloc[:, (kuukausi - 1)*3:kuukausi*3]
        topin_data = topin_data.iloc[:, (kuukausi - 1)*3:kuukausi*3]

    # Koko salkkujen arvo
    fig1, ax = plt.subplots(figsize=(20,10))
    mun_data_summa = mun_data.sum(axis=1)
    ka = mun_data.mean(axis=1)
    mask = mun_data_summa > ka*6-500
    mun_data_summa[mask] = mun_data_summa[mask]/2
    topin_data_summa = topin_data.sum(axis=1)
    ka = topin_data.mean(axis=1)
    mask = topin_data_summa > ka*6-500
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
    ax.legend(mun_data.columns, fontsize=17, ncol=int(sarakkeiden_määrä/3), loc='upper center', bbox_to_anchor=(0.5, -0.1),
          fancybox=True, shadow=True)
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
    ax.legend(topin_data.columns, fontsize=17, ncol=int(sarakkeiden_määrä/3), loc='upper center', bbox_to_anchor=(0.5, -0.1),
          fancybox=True, shadow=True)
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
    seitsemännen_kk_osakkeet = {"Verkkokauppa":"VERK.HE", "Nordea":"NDA-FI.HE", 
                             "TietoEvry":"TIETO.HE", "Tokmanni":"TOKMAN.HE", 
                             "Vincit":"VINCIT.HE", "Tecnotree":"TEM1V.HE"}
    kasi_kk_osakkeet = {"Elisa":"ELISA.HE", "Keskob":"KESKOB.HE", 
                             "Rovio":"ROVIO.HE", "Innofactor":"IFA1V.HE", 
                             "Leaddesk":"LEADD.HE", "Tecnotree":"TEM1V.HE"}
    ysi_kk_osakkeet = {"Kamux":"KAMUX.HE", "Nokia":"NOKIA.HE", 
                             "Terveystalo":"TTALO.HE", "Enersense International":"ESENSE.HE", 
                             "Gofore":"GOFORE.HE", "Metsä Board":"METSB.HE"}
    kymppi_kk_osakkeet = {"Pihlajalinna":"PIHLIS.HE", "Rovio":"ROVIO.HE", 
                             "Terveystalo":"TTALO.HE", "Trainers House":"TRH1V.HE", 
                             "Tecnotree":"TEM1V.HE", "Stockmann":"STOCKA.HE"}
    ykstoista_kk_osakkeet = {"Avidly":"AVIDLY.HE", "Rovio":"ROVIO.HE", 
                             "Nokia":"NOKIA.HE", "Tecnotree":"TEM1V.HE", 
                             "Trainers House":"TRH1V.HE", "Avidly1":"AVIDLY.HE"}
    kakstoista_kk_osakkeet = {"Kamux":"KAMUX.HE", "Stockmann":"STOCKA.HE", 
                             "Tokmanni":"TOKMAN.HE", "Avidly":"AVIDLY.HE", 
                             "Tecnotree":"TEM1V.HE", "Trainers House":"TRH1V.HE"}
    kolmetoista_kk_osakkeet = {"Sampo":"SAMPO.HE", "Fiskars":"FSKRS.HE", 
                             "Tokmanni":"TOKMAN.HE", "Tecnotree":"TEM1V.HE", 
                             "Citycon":"CTY1S.HE", "Innofactor":"IFA1V.HE"}
    neljätoista_kk_osakkeet = {"Nordea":"NDA-FI.HE", "TietoEvry":"TIETO.HE", 
                             "Tokmanni":"TOKMAN.HE", "Tecnotree":"TEM1V.HE", 
                             "Avidly":"AVIDLY.HE", "Stockmann":"STOCKA.HE"}
    viidestoista_kk_osakkeet = {"Nordea":"NDA-FI.HE", "Nokia":"NOKIA.HE", 
                             "Nokian renkaat":"TYRES.HE", "Rapala":"RAP1V.HE", 
                             "Avidly":"AVIDLY.HE", "Revenio":"REG1V.HE"}

    osakelista = [ensimmäisen_kk_osakkeet, toisen_kk_osakkeet, kolmannen_kk_osakkeet, neljännen_kk_osakkeet, viidennen_kk_osakkeet, 
                    kuudennen_kk_osakkeet, seitsemännen_kk_osakkeet, kasi_kk_osakkeet, ysi_kk_osakkeet, kymppi_kk_osakkeet, ykstoista_kk_osakkeet, 
                    kakstoista_kk_osakkeet, kolmetoista_kk_osakkeet, neljätoista_kk_osakkeet, viidestoista_kk_osakkeet]
                             

    # Kunkin kuukauden aloitus ja lopetus
    # Kuukausi muokkaukset
    ostot_ja_myynnit = [("2020-11-19","2020-12-19"), ("2020-12-18","2021-01-16"), ("2021-01-15","2021-02-16"), ("2021-02-15","2021-03-16"), ("2021-03-15","2021-04-16"),
                        ("2021-04-15","2021-05-15"), ("2021-05-14","2021-06-15"), ("2021-06-15","2021-07-15"), ("2021-07-15","2021-08-17"), ("2021-08-16","2021-09-21"),
                        ("2021-09-20","2021-10-19"), ("2021-10-18","2021-11-16"), ("2021-11-15","2021-12-16"), ("2021-12-15","2022-01-15"), ("2022-01-14",date.today() + timedelta(days=1))]
    
    salkun_arvo_mun = 3000
    salkun_arvo_topin = 3000
    mun_koko_data = pd.DataFrame()
    topin_koko_data = pd.DataFrame()
    for laskuri, pari in enumerate(ostot_ja_myynnit):
        data_mun, data_topin, osinko_mun, osinko_topin = datan_haku(osakelista[laskuri], pari[0], pari[1], (salkun_arvo_mun, salkun_arvo_topin))
        salkun_arvo_mun = data_mun.sum(axis=1).iloc[-1] + osinko_mun
        salkun_arvo_topin = data_topin.sum(axis=1).iloc[-1] + osinko_topin
        mun_koko_data = pd.concat([mun_koko_data, data_mun], axis=1)
        topin_koko_data = pd.concat([topin_koko_data, data_topin], axis=1)

    return mun_koko_data, topin_koko_data

def kuukauden_valinta(mun_data, topin_data, kuukausi):
    # Kuukausi muokkaukset
    ostot_ja_myynnit = [("2020-11-19","2020-12-19"), ("2020-12-18","2021-01-16"), ("2021-01-15","2021-02-15"), ("2021-02-15","2021-03-15"), ("2021-03-15","2021-04-15"),
                        ("2021-04-15","2021-05-15"), ("2021-05-14","2021-06-14"), ("2021-06-15","2021-07-14"), ("2021-07-15","2021-08-16"), ("2021-08-16","2021-09-20"),
                        ("2021-09-20","2021-10-18"), ("2021-10-18","2021-11-15"), ("2021-11-15","2021-12-15"), ("2021-12-15","2022-01-14"), ("2022-01-14",date.today() + timedelta(days=1))]
    pituus = len(ostot_ja_myynnit)
    if kuukausi <= pituus:
        mun_data = mun_data.loc[ostot_ja_myynnit[kuukausi - 1][0]:ostot_ja_myynnit[kuukausi - 1][1]]
        topin_data = topin_data.loc[ostot_ja_myynnit[kuukausi - 1][0]:ostot_ja_myynnit[kuukausi - 1][1]]
    else:
        mun_data = mun_data.loc[ostot_ja_myynnit[0][0]:ostot_ja_myynnit[pituus - 1][1]]
        topin_data = topin_data.loc[ostot_ja_myynnit[0][0]:ostot_ja_myynnit[pituus - 1][1]]
    return mun_data, topin_data

# Värjää taulukon numeroita
def taulukon_värjäys(val):
    color = 'red' if val < 0 else 'green'
    return 'color: %s' % color

# Värjää kuukauden vaihtumisen
def kuukauden_alotuksen_värjäys(s):
    # Kuukausi muokkaukset
    if s.name in [datetime(2020, 11, 19), datetime(2020, 12, 18), datetime(2021, 1, 15), datetime(2021, 2, 15), datetime(2021, 3, 15), 
                datetime(2021, 4, 15), datetime(2021, 5, 14), datetime(2021, 6, 15), datetime(2021, 7, 15), datetime(2021, 8, 16), datetime(2021, 9, 20),
                datetime(2021, 10, 18), datetime(2021, 11, 15), datetime(2021, 12, 15), datetime(2022, 1, 14)]:
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
    kuukausi = st.slider("Valitse näytettävä kuukausi. Viimeinen = kaikki kuukaudet", 1, 16, 16)
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
    ka = mun_data.mean(axis=1)
    mask = mun_data_summa > ka*6-500
    mun_data_summa[mask] = mun_data_summa[mask]/2
    mun_kehitys["Salkun arvo"] = mun_data_summa
    mun_kehitys["Muutos kisan alusta"] = (mun_kehitys["Salkun arvo"]/3000 - 1)
    topin_kehitys = pd.DataFrame()
    topin_data_summa = topin_data.sum(axis=1)
    ka = topin_data.mean(axis=1)
    mask = topin_data_summa > ka*6-500
    topin_data_summa[mask] = topin_data_summa[mask]/2
    topin_kehitys["Salkun arvo"] = topin_data_summa
    topin_kehitys["Muutos kisan alusta"] = (topin_kehitys["Salkun arvo"]/3000 - 1)
    # Kuukausi muokkaukset
    ajat = ["2020-11-19", "2020-12-18", "2021-01-15", "2021-02-15", "2021-03-15", 
            "2021-04-15", "2021-05-14", "2021-06-15", "2021-07-15", "2021-08-16", "2021-09-20", 
            "2021-10-18", "2021-11-15", "2021-12-15","2022-01-14", date.today() + timedelta(days=1)]
    if kuukausi > 1 and kuukausi < len(ajat):
        mun_kehitys["Muutos kk alusta"] = (mun_kehitys["Salkun arvo"]/mun_kehitys.loc[ajat[kuukausi - 1]]["Salkun arvo"] - 1)
        topin_kehitys["Muutos kk alusta"] = (topin_kehitys["Salkun arvo"]/topin_kehitys.loc[ajat[kuukausi - 1]]["Salkun arvo"] - 1)
    else:
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