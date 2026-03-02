import streamlit as st
import os
import random
import copy
from music21 import *

# --- CONFIGURACIÓ DE STREAMLIT ---
st.set_page_config(page_title="Generador d'Estudis Harmònics", layout="centered")
st.title("🎵 Generador d'Estudis Pedagògics")

# Aquí posaries les teves funcions 'ajustar_notes' i el diccionari 'alteracions_acords' 
# (el mateix que ja tens a l'script original)

def generar_estudi_web():
    # ... (Tot el teu codi de lògica interna de music21 es manté igual) ...
    # L'únic canvi és que al final NO fem servir ruta_sortida fixa, 
    # sinó que retornem l'objecte Score de music21.
    
    # [CODI DE LA TEVA FUNCIÓ AQUÍ...]
    
    # Al final, en comptes de score_out.write(...), fem:
    return score_out

# --- INTERFÍCIE D'USUARI ---
if st.button('Generar nova lectura a vista'):
    with st.spinner('Escrivint la partitura...'):
        score = generar_estudi_web()
        
        # Guardem temporalment per a la descàrrega
        xml_data = score.write('musicxml') 
        with open(xml_data, 'rb') as f:
            st.download_button(
                label="📥 Descarregar MusicXML (per a MuseScore/Sibelius)",
                data=f,
                file_name="estudi_harmonic.musicxml",
                mime="application/vnd.recordare.musicxml+xml"
            )
        
        # --- VISUALITZACIÓ ---
        # Per visualitzar-ho a la web gratuïtament, el més fàcil és generar un fitxer .sub (un format de music21)
        # o directament mostrar el text XML si l'usuari té una extensió.
        # Però el més elegant és fer servir un component de Streamlit anomenat "streamlit-osm-display"
        st.subheader("Vista prèvia")
        st.info("Consell: Descarrega l'arxiu per veure'l amb tot el format professional a MuseScore.")
