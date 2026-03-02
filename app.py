import streamlit as st
import streamlit.components.v1 as components
import json
import os
import random
import copy
import warnings
from music21 import *

warnings.filterwarnings("ignore")

# --- CONFIGURACIÓ DE STREAMLIT ---
st.set_page_config(page_title="Generador d'Estudis", layout="wide")
st.title("🎵 Generador de Lectura a Vista")
st.write("Clica el botó per generar un nou estudi a l'atzar i llegir-lo directament des d'aquí.")

if 'score_generat' not in st.session_state:
    st.session_state.score_generat = False
    st.session_state.xml_data = None

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

# --- FUNCIÓ DEL VISOR (OSMD) ---
def mostrar_partitura(xml_bytes):
    xml_str = xml_bytes.decode('utf-8')
    xml_escapat = json.dumps(xml_str)
    html_code = f"""
    <style>
      body {{ background-color: #FFFFFF; margin: 0; padding: 10px; border-radius: 8px; overflow-x: hidden; }}
    </style>
    <div id="osmdCanvas"></div>
    <script src="https://cdn.jsdelivr.net/npm/opensheetmusicdisplay@1.8.8/build/opensheetmusicdisplay.min.js"></script>
    <script>
      var osmd = new opensheetmusicdisplay.OpenSheetMusicDisplay("osmdCanvas", {{
        autoResize: true,
        backend: "svg",
        drawTitle: false,
        drawComposer: false, 
        drawPartNames: false,
        newSystemFromXML: true,
        stretchLastSystemLine: true
      }});
      osmd.load({xml_escapat}).then(function() {{
        osmd.render();
      }});
    </script>
    """
    components.html(html_code, height=600, scrolling=True)

# --- LÒGICA PRINCIPAL ---
def generar_estudi_web():
    ruta_entrada = 'Variacions_DoMajor_60c.musicxml'
    ruta_compas7 = 'compas7.musicxml'
    
    if not os.path.exists(ruta_entrada) or not os.path.exists(ruta_compas7):
        raise FileNotFoundError("❌ No s'han trobat els arxius .musicxml base a GitHub.")

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
    
    score_out = stream.Score()
    score_out.metadata = metadata.Metadata()
    score_out.metadata.title = ""
    score_out.metadata.composer = ""
    
    part_d = stream.Part()
    part_e = stream.Part()
    part_d.partName = ""
    part_e.partName = ""
    
    centre_previ = None 
    
    acords_finals_dreta = [
        ['C4', 'E4', 'G4'],         
        ['E4', 'G4', 'C5'],         
        ['G3', 'C4', 'E4'],         
        ['C4', 'E4', 'G4', 'B4'],   
        ['E4', 'G4', 'B4', 'C5'],   
        ['G3', 'B3', 'C4', 'E4']    
    ]
    acords_finals_esquerra = [
        ['C2', 'C3'],               
        ['C3', 'G3'],               
        ['C2', 'G2', 'C3']          
    ]
    
    # Memòria per enllaçar el compàs 8 amb l'última nota del compàs 7
    ultim_ps_dreta = 60
    ultim_ps_esquerra = 48
    
    for i, acord in enumerate(progressio):
        if i == 7:
            c_d, c_e = stream.Measure(number=8), stream.Measure(number=8)
            
            # --- CÀLCUL INTEL·LIGENT DE L'ACORD FINAL (MÀ DRETA) ---
            opcions_final_d = []
            for base_notes in acords_finals_dreta:
                ch = chord.Chord(base_notes, quarterLength=4.0)
                centre_base = sum(p.ps for p in ch.pitches) / len(ch.pitches)
                # Calculem quantes octaves l'hem de moure per acostar-lo al final del c7
                octave_shift = round((ultim_ps_dreta - centre_base) / 12.0)
                for p in ch.pitches: p.octave += int(octave_shift)
                opcions_final_d.append(ch)
                
            # Ordenem les opcions segons la distància real amb l'última nota
            opcions_final_d = sorted(opcions_final_d, key=lambda ch: abs((sum(p.ps for p in ch.pitches) / len(ch.pitches)) - ultim_ps_dreta))
            # Agafem un dels 2 acords / inversions que lliguen millor
            ch_d = random.choice(opcions_final_d[:2])
            c_d.append(ch_d)
            
            # --- CÀLCUL INTEL·LIGENT DE L'ACORD FINAL (MÀ ESQUERRA) ---
            opcions_final_e = []
            for base_notes in acords_finals_esquerra:
                ch = chord.Chord(base_notes, quarterLength=4.0)
                centre_base = sum(p.ps for p in ch.pitches) / len(ch.pitches)
                octave_shift = round((ultim_ps_esquerra - centre_base) / 12.0)
                for p in ch.pitches: p.octave += int(octave_shift)
                opcions_final_e.append(ch)
                
            opcions_final_e = sorted(opcions_final_e, key=lambda ch: abs((sum(p.ps for p in ch.pitches) / len(ch.pitches)) - ultim_ps_esquerra))
            ch_e = random.choice(opcions_final_e[:2])
            c_e.append(ch_e)
            
            c_d.rightBarline = bar.Barline('final')
            c_e.rightBarline = bar.Barline('final')
            
        else:
            if i == 6:
                idx7 = random.randint(0, len(m7_dreta) - 1)
                c_d = copy.deepcopy(m7_dreta[idx7])
                c_e = copy.deepcopy(m7_esquerra[idx7])
                c_d.number = c_e.number = 7
            else:
                idx = random.randint(0, len(compassos_dreta) - 1)
                c_d = copy.deepcopy(compassos_dreta[idx])
                c_e = copy.deepcopy(compassos_esquerra[idx])
                c_d.number = c_e.number = i + 1
                
            for c in [c_d, c_e]:
                for cl in ['KeySignature', 'TimeSignature', 'Clef', 'SystemLayout', 'PageLayout', 'Barline']:
                    c.removeByClass(cl)
                
        if i < 6:
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

        if i < 7:
            notes_d = [p for n in c_d.flatten().notes for p in (n.pitches if n.isChord else [n.pitch])]
            if notes_d:
                c_act = sum(p.ps for p in notes_d) / len(notes_d)
                # Bloc shift: connecta la melodia suament, SÍ afecta el compàs 7
                if centre_previ is not None:
                    diff = centre_previ - c_act
                    if diff >= 7: 
                        for p in notes_d: p.octave += 1
                    elif diff <= -7: 
                        for p in notes_d: p.octave -= 1
                
                # NOMÉS apliquem els límits extrems als c. 1 al 6 (el 7 es queda lliure)
                if i < 6:
                    for p in notes_d:
                        while p.ps < rh_min: p.octave += 1
                        while p.ps > rh_max: p.octave -= 1
                centre_previ = sum(p.ps for p in notes_d) / len(notes_d)

            notes_e = [p for n in c_e.flatten().notes for p in (n.pitches if n.isChord else [n.pitch])]
            if notes_e:
                if i < 6:
                    while max(p.ps for p in notes_e) > lh_max: 
                        for p in notes_e: p.octave -= 1
                    while min(p.ps for p in notes_e) < lh_min: 
                        for p in notes_e: p.octave += 1

            # Límits de distància (desena major) només aplicats als c. 1 al 6
            if i < 6:
                if notes_d and notes_e:
                    intents = 0
                    while intents < 3: 
                        min_ps_d = min(p.ps for p in notes_d)
                        max_ps_e = max(p.ps for p in notes_e)
                        
                        if (min_ps_d - max_ps_e) <= 16:
                            break 
                            
                        if max_ps_e + 12 <= lh_max:
                            for p in notes_e: p.octave += 1
                        elif min_ps_d - 12 >= rh_min:
                            for p in notes_d: p.octave -= 1
                        else:
                            for p in notes_d: p.octave -= 1
                        intents += 1

            # Quan arribem al final del compàs 7, capturem l'última nota per al c.8
            if i == 6:
                if notes_d: ultim_ps_dreta = notes_d[-1].ps
                if notes_e: ultim_ps_esquerra = notes_e[-1].ps

        if i == 0:
            c_d.insert(0, clef.TrebleClef()); c_d.insert(0, meter.TimeSignature('4/4')); c_d.insert(0, key.Key('C'))
            c_e.insert(0, clef.BassClef()); c_e.insert(0, meter.TimeSignature('4/4')); c_e.insert(0, key.Key('C'))
        if i == 4: c_d.insert(0, layout.SystemLayout(isNew=True))
            
        part_d.append(c_d)
        part_e.append(c_e)
        
    grup_piano = layout.StaffGroup([part_d, part_e], name='', symbol='brace', barTogether=True)
    score_out.insert(0, part_d); score_out.insert(0, part_e); score_out.insert(0, grup_piano)
    
    if tonalitat_desti != 'C':
        score_out.transpose(itvl_transp, inPlace=True)
        
    for element in score_out.flatten().notesAndRests:
        if hasattr(element, 'stemDirection'):
            element.stemDirection = 'unspecified'
        if hasattr(element, 'style') and element.style is not None:
            if hasattr(element.style, 'stemDirection'):
                element.style.stemDirection = 'unspecified'
                
        if element.isChord:
            for n in element.notes:
                if hasattr(n, 'stemDirection'):
                    n.stemDirection = 'unspecified'
                if hasattr(n, 'style') and n.style is not None:
                    if hasattr(n.style, 'stemDirection'):
                        n.style.stemDirection = 'unspecified'
                        
    return score_out, tonalitat_desti

# --- INTERFÍCIE D'USUARI ---
col1, col2 = st.columns([1, 1])

with col1:
    if st.button('Generar nova lectura a vista', use_container_width=True):
        with st.spinner('Creant la partitura...'):
            try:
                score_final, tonalitat = generar_estudi_web()
                path_temporal = score_final.write('musicxml')
                with open(path_temporal, 'rb') as f:
                    st.session_state.xml_data = f.read()
                st.session_state.score_generat = True
            except FileNotFoundError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"S'ha produït un error inesperat: {e}")

if st.session_state.score_generat:
    with col2:
        st.download_button(
            label="📥 Descarregar Partitura per a MuseScore",
            data=st.session_state.xml_data,
            file_name="Estudi_Lectura_Vista.musicxml",
            mime="application/vnd.recordare.musicxml+xml",
            use_container_width=True
        )
    
    st.divider()
    mostrar_partitura(st.session_state.xml_data)
