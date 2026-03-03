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
    'Fm': {'C': None, 'D': None, 'E': None, 'F': None, 'G': None, 'A': 'flat', 'B': None},
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
        raise FileNotFoundError("❌ No s'han trobat els arxius .musicxml base.")

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
    
    # Límits dinàmics per compensar la transposició final
    rh_min, rh_max = 55 - shift, 76 - shift
    lh_min, lh_max = 33 - shift, 50 - shift
    
    c7_rh_min, c7_rh_max = 60 - shift, 81 - shift
    c7_lh_min, c7_lh_max = 40 - shift, 60 - shift

    progressions_possibles = [
        ['C', 'Am', 'F', 'C', 'G', 'D7', 'G7', 'C'],
        ['Cmaj7', 'A7', 'Dm7', 'F', 'C', 'Dm', 'G7', 'C'],
        ['C', 'E7', 'Am', 'C7', 'F', 'Dm7', 'G7', 'C'],
        ['C', 'F', 'Bdim', 'E7', 'Am', 'D7', 'G7', 'C'],
        ['C', 'G', 'Am', 'F', 'C', 'G', 'G7', 'C'],
        ['C', 'Am', 'F', 'G', 'C', 'Am', 'G7', 'C'],
        ['C', 'G', 'Am', 'Em', 'F', 'C', 'G7', 'C'],
        ['C', 'C7', 'F', 'D7', 'G', 'Am', 'G7', 'C'],
        ['C', 'F', 'Bdim', 'Em', 'Am', 'Dm7', 'G7', 'C'],
        ['C', 'Dm', 'Em', 'F', 'C', 'D7', 'G7', 'C'],
        ['C', 'G', 'Am', 'E7', 'F', 'C', 'G7', 'C'],
        ['Cmaj7', 'Am', 'Dm7', 'G7', 'Em', 'A7', 'G7', 'C'],
        ['C', 'C7', 'F', 'Fm', 'C', 'Am', 'G7', 'C'],
        ['C', 'Em', 'F', 'G', 'Am', 'D7', 'G7', 'C']
    ]
    progressio = random.choice(progressions_possibles)
    
    score_out = stream.Score()
    score_out.metadata = metadata.Metadata()
    
    part_d = stream.Part(); part_d.partName = ""
    part_e = stream.Part(); part_e.partName = ""
    
    centre_previ_d = None 
    centre_previ_e = None
    
    acords_finals_dreta = [
        ['C4', 'E4', 'G4'], ['E4', 'G4', 'C5'], ['G3', 'C4', 'E4'],         
        ['C4', 'E4', 'G4', 'B4'], ['E4', 'G4', 'B4', 'C5'], ['G3', 'B3', 'C4', 'E4']    
    ]
    acords_finals_esquerra = [['C2', 'C3'], ['C3', 'G3'], ['C2', 'G2', 'C3']]
    
    min_ps_dreta_c7 = 60
    max_ps_dreta_c7 = 72
    
    for i, acord in enumerate(progressio):
        
        # --- CAS 1: COMPASSOS 1 AL 6 ---
        if i < 6:
            idx = random.randint(0, len(compassos_dreta) - 1)
            c_d = copy.deepcopy(compassos_dreta[idx])
            c_e = copy.deepcopy(compassos_esquerra[idx])
            c_d.number = c_e.number = i + 1
            
            for c in [c_d, c_e]:
                for cl in ['KeySignature', 'TimeSignature', 'Clef', 'SystemLayout', 'PageLayout', 'Barline']:
                    c.removeByClass(cl)
                    
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
            
            # Ajust Bloc Dreta
            notes_d = [p for n in c_d.flatten().notes for p in (n.pitches if n.isChord else [n.pitch])]
            if notes_d:
                millors_shifts_d = []
                min_penalty_d = float('inf')
                for oct_shift in range(-4, 5):
                    penalty = sum(max(0, rh_min - (p.ps + oct_shift*12)) + max(0, (p.ps + oct_shift*12) - rh_max) for p in notes_d)
                    if penalty < min_penalty_d:
                        min_penalty_d = penalty
                        millors_shifts_d = [oct_shift]
                    elif penalty == min_penalty_d:
                        millors_shifts_d.append(oct_shift)
                        
                if centre_previ_d is not None:
                    shift_final_d = min(millors_shifts_d, key=lambda s: abs((sum(p.ps + s*12 for p in notes_d)/len(notes_d)) - centre_previ_d))
                else:
                    shift_final_d = millors_shifts_d[0]
                    
                for p in notes_d: p.octave += shift_final_d
                centre_previ_d = sum(p.ps for p in notes_d) / len(notes_d)

            # Ajust Bloc Esquerra
            notes_e = [p for n in c_e.flatten().notes for p in (n.pitches if n.isChord else [n.pitch])]
            if notes_e:
                millors_shifts_e = []
                min_penalty_e = float('inf')
                for oct_shift in range(-4, 5):
                    penalty = sum(max(0, lh_min - (p.ps + oct_shift*12)) + max(0, (p.ps + oct_shift*12) - lh_max) for p in notes_e)
                    if penalty < min_penalty_e:
                        min_penalty_e = penalty
                        millors_shifts_e = [oct_shift]
                    elif penalty == min_penalty_e:
                        millors_shifts_e.append(oct_shift)
                        
                if centre_previ_e is not None:
                    shift_final_e = min(millors_shifts_e, key=lambda s: abs((sum(p.ps + s*12 for p in notes_e)/len(notes_e)) - centre_previ_e))
                else:
                    shift_final_e = millors_shifts_e[0]
                    
                for p in notes_e: p.octave += shift_final_e
                centre_previ_e = sum(p.ps for p in notes_e) / len(notes_e)

        # --- CAS 2: COMPÀS 7 ---
        elif i == 6:
            idx7 = random.randint(0, len(m7_dreta) - 1)
            c_d = copy.deepcopy(m7_dreta[idx7])
            c_e = copy.deepcopy(m7_esquerra[idx7])
            c_d.number = c_e.number = 7
            
            for c in [c_d, c_e]:
                for cl in ['KeySignature', 'TimeSignature', 'Clef', 'SystemLayout', 'PageLayout', 'Barline']:
                    c.removeByClass(cl)
                    
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

            # Ajust Bloc Dreta (C7)
            notes_d = [p for n in c_d.flatten().notes for p in (n.pitches if n.isChord else [n.pitch])]
            if notes_d:
                millors_shifts_d = []
                min_penalty_d = float('inf')
                for oct_shift in range(-4, 5):
                    penalty = sum(max(0, c7_rh_min - (p.ps + oct_shift*12)) + max(0, (p.ps + oct_shift*12) - c7_rh_max) for p in notes_d)
                    if penalty < min_penalty_d:
                        min_penalty_d = penalty
                        millors_shifts_d = [oct_shift]
                    elif penalty == min_penalty_d:
                        millors_shifts_d.append(oct_shift)
                        
                if centre_previ_d is not None:
                    shift_final_d = min(millors_shifts_d, key=lambda s: abs((sum(p.ps + s*12 for p in notes_d)/len(notes_d)) - centre_previ_d))
                else:
                    shift_final_d = millors_shifts_d[0]
                    
                for p in notes_d: p.octave += shift_final_d
                
                # Guardem dades per al compàs 8 sense el shift aplicat encara
                min_ps_dreta_c7 = min(p.ps for p in notes_d)
                max_ps_dreta_c7 = max(p.ps for p in notes_d)

            # Ajust Bloc Esquerra (C7)
            notes_e = [p for n in c_e.flatten().notes for p in (n.pitches if n.isChord else [n.pitch])]
            if notes_e:
                millors_shifts_e = []
                min_penalty_e = float('inf')
                for oct_shift in range(-4, 5):
                    penalty = sum(max(0, c7_lh_min - (p.ps + oct_shift*12)) + max(0, (p.ps + oct_shift*12) - c7_lh_max) for p in notes_e)
                    if penalty < min_penalty_e:
                        min_penalty_e = penalty
                        millors_shifts_e = [oct_shift]
                    elif penalty == min_penalty_e:
                        millors_shifts_e.append(oct_shift)
                        
                if centre_previ_e is not None:
                    shift_final_e = min(millors_shifts_e, key=lambda s: abs((sum(p.ps + s*12 for p in notes_e)/len(notes_e)) - centre_previ_e))
                else:
                    shift_final_e = millors_shifts_e[0]
                    
                for p in notes_e: p.octave += shift_final_e

        # --- CAS 3: COMPÀS 8 (Cadència Final) ---
        elif i == 7:
            c_d, c_e = stream.Measure(number=8), stream.Measure(number=8)
            
            valid_chords = []
            fallback_chords = []
            center_c7 = (min_ps_dreta_c7 + max_ps_dreta_c7) / 2.0
            
            for base_notes in acords_finals_dreta:
                for octave_shift in range(-3, 4):
                    ch = chord.Chord(base_notes, quarterLength=4.0)
                    for p in ch.pitches: p.octave += octave_shift
                    
                    min_chord = min(p.ps for p in ch.pitches)
                    max_chord = max(p.ps for p in ch.pitches)
                    center_chord = sum(p.ps for p in ch.pitches) / len(ch.pitches)
                    
                    fallback_chords.append((ch, abs(center_chord - center_c7)))
                    if min_chord >= min_ps_dreta_c7 and max_chord <= max_ps_dreta_c7:
                        valid_chords.append(ch)
                        
            if valid_chords:
                ch_d = random.choice(valid_chords)
            else:
                fallback_chords = sorted(fallback_chords, key=lambda x: x[1])
                ch_d = random.choice([fallback_chords[0][0], fallback_chords[1][0]])
                
            c_d.append(ch_d)
            
            notes_e_final = random.choice(acords_finals_esquerra)
            c_e.append(chord.Chord(notes_e_final, quarterLength=4.0))
            
            c_d.rightBarline = bar.Barline('final')
            c_e.rightBarline = bar.Barline('final')

        # Formateig inicial
        if i == 0:
            c_d.insert(0, clef.TrebleClef()); c_d.insert(0, meter.TimeSignature('4/4')); c_d.insert(0, key.Key('C'))
            c_e.insert(0, clef.BassClef()); c_e.insert(0, meter.TimeSignature('4/4')); c_e.insert(0, key.Key('C'))
        if i == 4: c_d.insert(0, layout.SystemLayout(isNew=True))
            
        part_d.append(c_d)
        part_e.append(c_e)
        
    grup_piano = layout.StaffGroup([part_d, part_e], name='', symbol='brace', barTogether=True)
    score_out.insert(0, part_d); score_out.insert(0, part_e); score_out.insert(0, grup_piano)
    
    # Única transposició final
    if tonalitat_desti != 'C':
        score_out.transpose(itvl_transp, inPlace=True)
        
    for element in score_out.flatten().notesAndRests:
        if hasattr(element, 'stemDirection'): element.stemDirection = 'unspecified'
        if hasattr(element, 'style') and element.style is not None:
            if hasattr(element.style, 'stemDirection'): element.style.stemDirection = 'unspecified'
        if element.isChord:
            for n in element.notes:
                if hasattr(n, 'stemDirection'): n.stemDirection = 'unspecified'
                if hasattr(n, 'style') and n.style is not None:
                    if hasattr(n.style, 'stemDirection'): n.style.stemDirection = 'unspecified'
                        
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
            except Exception as e:
                st.error(f"S'ha produït un error: {e}")

if st.session_state.score_generat:
    with col2:
        st.download_button(
            label="📥 Descarregar per MuseScore",
            data=st.session_state.xml_data,
            file_name="Estudi.musicxml",
            mime="application/vnd.recordare.musicxml+xml",
            use_container_width=True
        )
    st.divider()
    mostrar_partitura(st.session_state.xml_data)
