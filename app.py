import streamlit as st
import json
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import math
import time

base_url = st.text_input("Zadejte adresu", placeholder="url")
if st.button("Vyhledej nabídky"):
    base_url_cleaned = base_url.replace("&page=1", "") # Později nahradit za regex

    request_response = requests.get(base_url_cleaned)
    soup = BeautifulSoup(request_response.text, "html.parser")

    pocet_nemovitosti_element = soup.find("div", {"class": "PropertiesMap_propertiesMapScroll__VtwqL"}) \
        .find("p", {"class": "form-label"}) \
        .find("span")
    pocet_nemovitosti = pocet_nemovitosti_element.text.split("\xa0")[0]
    
    pocet_stranek = math.ceil(int(pocet_nemovitosti) / 15)
    pocet_stranek_koeficient = 100 / pocet_stranek

    progress_text_seznam_nemovitosti = "Stahování seznamu nemovistostí"
    progress_bar_seznam_nemovitosti = st.progress(0, text=progress_text_seznam_nemovitosti)
    
    list_adres = []
    for i in range(1, pocet_stranek + 1):
        url = base_url_cleaned + f"&page={i}"

        request_response = requests.get(url)
        soup = BeautifulSoup(request_response.text, "html.parser")

        odkazy_elementy = soup.find("section", {"class": "Section_section__gjwvr"}) \
            .find_all("article")

        odkazy = []
        for element_odkaz in odkazy_elementy:
            odkaz = element_odkaz.find("a")
            odkazy.append(odkaz)

        for odkaz in odkazy:
            href = odkaz.get("href")
            if href:
                list_adres.append(href)
        progress_bar_seznam_nemovitosti.progress((pocet_stranek_koeficient * i) / 100, text=progress_text_seznam_nemovitosti)

    list_adres = list(set(list_adres))

    time.sleep(1)
    progress_bar_seznam_nemovitosti.empty()

    progress_text_nemovitosti = "Stahování nemovistostí"
    progress_bar_nemovitosti = st.progress(0, text=progress_text_nemovitosti)
    pocet_nemovitosti_koeficient = 100 / int(pocet_nemovitosti)

    data = []
    for i, url in enumerate(list_adres):
        request_response = requests.get(url)
        soup = BeautifulSoup(request_response.text)
        seznam_parametru = {}

        najemne = soup.find("div", {"class": "StickyBox_stickyBox__nu8sW"}) \
            .find_all("div", {"class": "ContentBox_contentBox__tD7YI"})[0] \
            .find("div", {"class": "justify-content-between"}) \
            .find_all("span")[4]
        najemne = re.sub(r'\D', '', najemne.text)
        seznam_parametru["Najemne"] = najemne

        podsekce_parametry_list = soup.find_all("div", {"class": "ParamsTable_paramsTableGroup__Flyfi"}) 

        for podsekce_parametry in podsekce_parametry_list[0:2]:
            radky_parametru = podsekce_parametry.find_all("tr")
            for radek_prametru in radky_parametru:
                popisek_parametru = radek_prametru.find("th").text
                hodnota_parametru = radek_prametru.find("td").text.replace("\xa0", " ")
                seznam_parametru[popisek_parametru] = hodnota_parametru
        
        data.append(seznam_parametru)
        progress_bar_nemovitosti.progress((pocet_nemovitosti_koeficient * (i + 1)) / 100, text=progress_text_nemovitosti)

    time.sleep(1)
    progress_bar_nemovitosti.empty()

    df = pd.DataFrame(data)
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Uložit jako CSV", data=csv, file_name="bezrealitky.csv", mime="text/csv")













