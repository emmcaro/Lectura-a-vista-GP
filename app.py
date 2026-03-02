import streamlit as st
import streamlit.components.v1 as components  # NOU
import json  # NOU
import os
import random
import copy
import warnings
from music21 import *

warnings.filterwarnings("ignore")

# --- CONFIGURACIÓ DE STREAMLIT ---
st.set_page_config(page_title="Generador d'Estudis Harmònics", layout="centered")
st.title("🎵 Generador de Lectura a Vista")
st.write("Clica el botó per generar un nou estudi de piano a l'atzar i descarregar-lo en format MusicXML.")

# --- DICCIONARIS I FUNCIONS AUXILIARS ---
alteracions_acords = {
    'C': {'C': None, 'D': None, 'E': None, 'F': None, 'G': None, 'A': None, 'B': None},
    'Dm': {'C': None, 'D': None, 'E': None, 'F': None, 'G': None, 'A': None, 'B': None},
    'Em': {'C': None, 'D': None, 'E': None, 'F': None, 'G': None, 'A': None, 'B': None},
    'F': {'C': None, 'D': None, 'E': None, 'F': None, 'G': None, 'A': None, 'B': None},
    'G': {'C': None, 'D': None, 'E': None, 'F': None, 'G': None, 'A': None, 'B': None},
    'Am': {'C': None, 'D': None, 'E': None, 'F': None, 'G': None, 'A': None, 'B': None},
    'Bdim': {'C': None, 'D': None, 'E': None, 'F': None, 'G': None, 'A': None, 'B': None},
    'Cmaj7': {'C': None, 'D': None, 'E': None, 'F': None, 'G': None, 'A': None, 'B': None},
    'Dm7': {'C': None, 'D': None, 'E': None, 'F': None, 'G': None, 'A': None, 'B': None},
    'G7': {'C': None, 'D': None, 'E': None, 'F': None, 'G': None, 'A': None, 'B': None},
    'D7': {'C': None, 'D': None, 'E': None, 'F': 'sharp', 'G': None, 'A': None, 'B': None},
    'E7': {'C': None, 'D': None, 'E': None, 'F': None, 'G': 'sharp', 'A': None, 'B': None},
    'A7': {'C': 'sharp', 'D': None, 'E': None, 'F': None, 'G': None, 'A': None, 'B': None},
    'C7': {'C': None, 'D': None, 'E': None, 'F': None, 'G': None, 'A': None, 'B': 'flat'}
}

def ajustar_notes(pitch_obj, escala_dict):
    alteracio = escala_dict.get(pitch_obj.step, None)
    if alteracio is None:
        pitch_obj.accidental = None
    else:
        pitch_obj.accidental = pitch.Accidental(alteracio)

def mostrar_partitura(xml_bytes):
    # Convertim els bytes a text
    xml_str = xml_bytes.decode('utf-8')
    # Utilitzem json.dumps per escapar cometes i salts de línia de forma segura per a JavaScript
    xml_escapat = json.dumps(xml_str)
    
    # Codi HTML/JS que carrega OpenSheetMusicDisplay
    html_code = f"""
    <div id="osmdCanvas"></div>
    <script src="https://cdn.jsdelivr.net/npm/opensheetmusicdisplay@1.8.8/build/opensheetmusicdisplay.min.js"></script>
    <script>
      var osmd = new opensheetmusicdisplay.OpenSheetMusicDisplay("osmdCanvas", {{
        autoResize: true,
        backend: "svg",
        drawTitle: false // Amaguem el títol intern per no duplicar-lo
      }});
      
      // Carreguem l'XML generat i el dibuixem
      osmd.load({xml_escapat}).then(function() {{
        osmd.render();
      }});
    </script>
    """
    # Mostrem el bloc a Streamlit amb una alçada generosa
    components.html(html_code, height=750, scrolling=True)

# --- LÒGICA PRINCIPAL (Adaptada per a web) ---
def generar_estudi_web():
    # Busquem els arxius a la carpeta arrel del GitHub
    ruta_entrada = 'Variacions_DoMajor_60c.musicxml'
    ruta_compas7 = 'compas7.musicxml'
    
    # Comprovació de seguretat
    if not os.path.exists(ruta_entrada) or not os.path.exists(ruta_compas7):
        raise FileNotFoundError("❌ No s'han trobat els arxius .musicxml base a GitHub. Assegura't que es diuen exactament igual.")

    score_in = converter.parse(ruta_entrada)
    parts_in = score_in.getElementsByClass(stream.Part)
    compassos_dreta = list(parts_in[0].getElementsByClass(stream.Measure))
    compassos_esquerra = list(parts_in[1].getElementsByClass(stream.Measure))
    
    score_7 = converter.parse(ruta_compas7)
    parts_7 = score_7.getElementsByClass(stream.Part)
    m7_dreta = list(parts_7[0].getElementsByClass(stream.Measure))
    m7_esquerra = list(parts_7[1].getElementsByClass(stream.Measure))
    
    tonalitats = ['C', 'G', 'D', 'A', 'F', 'B-', 'E-']
    tonalitat_desti = random.choice(tonalitats)
    
    referencies = {'C':'C4', 'G':'G3', 'D':'D4', 'A':'A3', 'F':'F4', 'B-':'B-3', 'E-':'E-4'}
    itvl_transp = interval.Interval(pitch.Pitch('C4'), pitch.Pitch(referencies[tonalitat_desti]))
    shift = itvl_transp.semitones
    
    rh_min, rh_max = 55 - shift, 76 - shift
    lh_min, lh_max = 33 - shift, 50 - shift

    progressions_possibles = [
        ['C', 'Am', 'F', 'C', 'G', 'D7', 'G7', 'C'],
        ['Cmaj7', 'A7', 'Dm7', 'F', 'C', 'Dm', 'G7', 'C'],
        ['C', 'E7', 'Am', 'C7', 'F', 'Dm7', 'G7', 'C'],
        ['C', 'F', 'Bdim', 'E7', 'Am', 'D7', 'G7', 'C']
    ]
    progressio = random.choice(progressions_possibles)
    
    # === CREACIÓ DE L'ARXIU DE SORTIDA ===
    score_out = stream.Score()
    part_d = stream.Part()
    part_e = stream.Part()
    centre_previ = None 
    
    for i, acord in enumerate(progressio):
        # COMPÀS 8
        if i == 7:
            c_d, c_e = stream.Measure(number=8), stream.Measure(number=8)
            c_d.append(chord.Chord(['C4', 'E4', 'G4'], quarterLength=4.0))
            c_e.append(chord.Chord(['C2', 'C3'], quarterLength=4.0))
            c_d.rightBarline = c_e.rightBarline = bar.Barline('final')
        # COMPÀS 7
        elif i == 6:
            idx7 = random.randint(0, len(m7_dreta) - 1)
            c_d = copy.deepcopy(m7_dreta[idx7])
            c_e = copy.deepcopy(m7_esquerra[idx7])
            c_d.number = c_e.number = 7
        # COMPASSOS 1-6
        else:
            idx = random.randint(0, len(compassos_dreta) - 1)
            c_d = copy.deepcopy(compassos_dreta[idx])
            c_e = copy.deepcopy(compassos_esquerra[idx])
            c_d.number = c_e.number = i + 1
            
        for c in [c_d, c_e]:
            for cl in ['KeySignature', 'TimeSignature', 'Clef', 'SystemLayout', 'PageLayout']:
                c.removeByClass(cl)
                
        if i < 7:
            arrel_str = acord.replace('maj7','').replace('dim','').replace('m7','').replace('m','').replace('7','')
            itvl = interval.Interval(pitch.Pitch('C4'), pitch.Pitch(arrel_str + '4'))
            c_d.transpose(itvl, inPlace=True)
            c_e.transpose(itvl, inPlace=True)
            
            escala_correcta = alteracions_acords[acord]
            for compas in [c_d, c_e]:
                for element in compas.flatten().notes:
                    if element.isNote: ajustar_notes(element.pitch, escala_correcta)
                    elif element.isChord:
                        for p in element.pitches: ajustar_notes(p, escala_correcta)

            notes_d = [p for n in c_d.flatten().notes for p in (n.pitches if n.isChord else [n.pitch])]
            if notes_d:
                c_act = sum(p.ps for p in notes_d) / len(notes_d)
                if centre_previ is not None:
                    diff = centre_previ - c_act
                    if diff >= 7: [setattr(p, 'octave', p.octave + 1) for p in notes_d]
                    elif diff <= -7: [setattr(p, 'octave', p.octave - 1) for p in notes_d]
                for p in notes_d:
                    while p.ps < rh_min: p.octave += 1
                    while p.ps > rh_max: p.octave -= 1
                centre_previ = sum(p.ps for p in notes_d) / len(notes_d)

            notes_e = [p for n in c_e.flatten().notes for p in (n.pitches if n.isChord else [n.pitch])]
            if notes_e:
                while max(p.ps for p in notes_e) > lh_max: [setattr(p, 'octave', p.octave - 1) for p in notes_e]
                while min(p.ps for p in notes_e) < lh_min: [setattr(p, 'octave', p.octave + 1) for p in notes_e]

        if i == 0:
            c_d.insert(0, clef.TrebleClef()); c_d.insert(0, meter.TimeSignature('4/4')); c_d.insert(0, key.Key('C'))
            c_e.insert(0, clef.BassClef()); c_e.insert(0, meter.TimeSignature('4/4')); c_e.insert(0, key.Key('C'))
        if i == 4: c_d.insert(0, layout.SystemLayout(isNew=True))
            
        part_d.append(c_d)
        part_e.append(c_e)
        
    grup_piano = layout.StaffGroup([part_d, part_e], name='Piano', symbol='brace', barTogether=True)
    score_out.insert(0, part_d); score_out.insert(0, part_e); score_out.insert(0, grup_piano)
    
    if tonalitat_desti != 'C':
        score_out.transpose(itvl_transp, inPlace=True)
        
    for element in score_out.flatten().notes:
        element.stemDirection = 'unspecified'
        
    return score_out, tonalitat_desti, progressio

# --- INTERFÍCIE D'USUARI ---
if st.button('Generar nova lectura a vista'):
    with st.spinner('Creant la partitura...'):
        try:
            # 1. Cridem la funció principal
            score_final, tonalitat, harmonia = generar_estudi_web()
            
            # 2. Mostrem els detalls musicals a l'usuari
            st.success("✨ Estudi generat amb èxit!")
            st.info(f"🎵 **Tonalitat:** {tonalitat.replace('-', 'b')} Major")
            
            # 3. Preparem l'arxiu
            path_temporal = score_final.write('musicxml')
            with open(path_temporal, 'rb') as f:
                xml_data = f.read()
            
            # --- NOU: MOSTREM LA PARTITURA A LA WEB ---
            st.divider()  # Una línia separadora per fer-ho bonic
            st.subheader("Visualització de l'estudi")
            mostrar_partitura(xml_data)
            # ------------------------------------------

            # 4. Botó de descàrrega a sota del visor
            st.download_button(
                label="📥 Descarregar Partitura per a MuseScore (MusicXML)",
                data=xml_data,
                file_name="Estudi_Lectura_Vista.musicxml",
                mime="application/vnd.recordare.musicxml+xml"
            )
            
        except FileNotFoundError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"S'ha produït un error inesperat: {e}")
