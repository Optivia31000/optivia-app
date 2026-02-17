import streamlit as st
import pandas as pd
import io
import os
import math
import requests
import xlsxwriter # Important pour la conversion d'adresse de cellule

# --- CONFIGURATION ---
st.set_page_config(page_title="CALCULATEUR OPTIVIA", page_icon="🚛", layout="wide")

# --- STYLE ---
st.markdown("""
    <style>
    .client-price { font-size: 32px !important; font-weight: bold; color: #1E3A8A; } 
    .buy-limit { font-size: 32px !important; font-weight: bold; color: #DC2626; } 
    .kpi-card { background-color: #F3F4F6; padding: 15px; border-radius: 10px; border-left: 5px solid #1E3A8A; margin-bottom: 10px;}
    .zone-info { color: #854d0e; background-color: #fef9c3; padding: 10px; border-radius: 5px; font-weight: bold; margin-bottom: 10px;}
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DONNÉES GPS ---
DEPT_GPS = {
    "01": (46.2052, 5.2255), "02": (49.5641, 3.6199), "03": (46.5681, 3.3344), "04": (44.0922, 6.2369),
    "05": (44.5632, 6.0796), "06": (43.7102, 7.2620), "07": (44.7333, 4.5955), "08": (49.7738, 4.7198),
    "09": (42.9644, 1.6054), "10": (48.2973, 4.0744), "11": (43.2122, 2.3537), "12": (44.3504, 2.5726),
    "13": (43.2965, 5.3698), "14": (49.1829, -0.3707), "15": (44.9278, 2.4423), "16": (45.6484, 0.1562),
    "17": (46.1603, -1.1511), "18": (47.0810, 2.3988), "19": (45.2673, 1.7709), "20": (41.9192, 8.7386),
    "21": (47.3220, 5.0415), "22": (48.5141, -2.7658), "23": (46.1712, 1.8679), "24": (45.1839, 0.7214),
    "25": (47.2378, 6.0241), "26": (44.9333, 4.8917), "27": (49.0274, 1.1511), "28": (48.4439, 1.4890),
    "29": (48.0000, -4.1000), "30": (43.8367, 4.3601), "31": (43.6047, 1.4442), "32": (43.6465, 0.5862),
    "33": (44.8378, -0.5792), "34": (43.6108, 3.8767), "35": (48.1173, -1.6778), "36": (46.8115, 1.6915),
    "37": (47.3941, 0.6848), "38": (45.1885, 5.7245), "39": (46.6753, 5.5539), "40": (43.8920, -0.5004),
    "41": (47.5861, 1.3359), "42": (45.4397, 4.3872), "43": (45.0435, 3.8837), "44": (47.2184, -1.5536),
    "45": (47.9030, 1.9093), "46": (44.4491, 1.4366), "47": (44.2031, 0.6156), "48": (44.5167, 3.5000),
    "49": (47.4784, -0.5632), "50": (49.1171, -1.0945), "51": (48.9566, 4.3676), "52": (48.1119, 5.1438),
    "53": (48.0706, -0.7719), "54": (48.6921, 6.1844), "55": (48.7734, 5.1612), "56": (47.6582, -2.7608),
    "57": (49.1193, 6.1757), "58": (46.9909, 3.1628), "59": (50.6292, 3.0573), "60": (49.4317, 2.0898),
    "61": (48.4307, 0.0924), "62": (50.2910, 2.7775), "63": (45.7772, 3.0870), "64": (43.2951, -0.3708),
    "65": (43.2333, 0.0833), "66": (42.6987, 2.8959), "67": (48.5734, 7.7521), "68": (47.7495, 7.3398),
    "69": (45.7640, 4.8357), "70": (47.6198, 6.1544), "71": (46.3069, 4.8288), "72": (48.0061, 0.1996),
    "73": (45.5646, 5.9178), "74": (45.8992, 6.1294), "75": (48.8566, 2.3522), "76": (49.4432, 1.0999),
    "77": (48.5397, 2.6601), "78": (48.8049, 2.1204), "79": (46.3237, -0.4648), "80": (49.8941, 2.2957),
    "81": (43.9287, 2.1464), "82": (44.0176, 1.3558), "83": (43.1242, 5.9280), "84": (43.9493, 4.8055),
    "85": (46.6705, -1.4264), "86": (46.5802, 0.3404), "87": (45.8336, 1.2611), "88": (48.1744, 6.4512),
    "89": (47.7985, 3.5670), "90": (47.6397, 6.8638), "91": (48.6298, 2.4418), "92": (48.8924, 2.2154),
    "93": (48.9105, 2.4392), "94": (48.7904, 2.4556), "95": (49.0389, 2.0776)
}

# --- DONNÉES GÉOGRAPHIQUES (Villes) ---
FULL_GEO_DATA = {
    "01 - Ain": ["Belley", "Bourg-en-Bresse", "Gex", "Nantua"],
    "02 - Aisne": ["Château-Thierry", "Laon", "Saint-Quentin", "Soissons", "Vervins"],
    "03 - Allier": ["Montluçon", "Vichy", "Yseure"],
    "04 - Alpes-Htes-Prov.": ["Digne-les-Bains", "Forcalquier"],
    "05 - Hautes-Alpes": ["Briançon", "Gap"],
    "06 - Alpes-Maritimes": ["Grasse", "Nice"],
    "07 - Ardèche": ["Privas", "Tournon-sur-Rhône"],
    "08 - Ardennes": ["Charleville-Mézières", "Sedan"],
    "09 - Ariège": ["Foix", "Pamiers"],
    "10 - Aube": ["Troyes"],
    "11 - Aude": ["Carcassonne", "Narbonne", "Castelnaudary"],
    "12 - Aveyron": ["Millau", "Rodez"],
    "13 - Bouches-du-Rhône": ["Aix", "Marseille"],
    "14 - Calvados": ["Caen"],
    "15 - Cantal": ["Aurillac"],
    "16 - Charente": ["Angoulême"],
    "17 - Charente-Maritime": ["La Rochelle"],
    "18 - Cher": ["Bourges"],
    "19 - Corrèze": ["Brive", "Tulle"],
    "20 - Corse": ["Ajaccio", "Bastia"],
    "21 - Côte-d'Or": ["Dijon"],
    "22 - Côtes-d'Armor": ["Saint-Brieuc"],
    "23 - Creuse": ["Guéret"],
    "24 - Dordogne": ["Périgueux"],
    "25 - Doubs": ["Besançon"],
    "26 - Drôme": ["Valence"],
    "27 - Eure": ["Évreux"],
    "28 - Eure-et-Loir": ["Chartres"],
    "29 - Finistère": ["Brest", "Quimper"],
    "30 - Gard": ["Nîmes"],
    "31 - Haute-Garonne": ["Toulouse", "Luchon", "Muret"],
    "32 - Gers": ["Auch"],
    "33 - Gironde": ["Bordeaux"],
    "34 - Hérault": ["Montpellier"],
    "35 - Ille-et-Vilaine": ["Rennes"],
    "36 - Indre": ["Châteauroux"],
    "37 - Indre-et-Loire": ["Tours"],
    "38 - Isère": ["Grenoble"],
    "39 - Jura": ["Lons-le-Saunier"],
    "40 - Landes": ["Mont-de-Marsan"],
    "41 - Loir-et-Cher": ["Blois"],
    "42 - Loire": ["Saint-Étienne"],
    "43 - Haute-Loire": ["Le Puy-en-Velay"],
    "44 - Loire-Atlantique": ["Nantes"],
    "45 - Loiret": ["Orléans"],
    "46 - Lot": ["Cahors"],
    "47 - Lot-et-Garonne": ["Agen"],
    "48 - Lozère": ["Mende"],
    "49 - Maine-et-Loire": ["Angers"],
    "50 - Manche": ["Saint-Lô"],
    "51 - Marne": ["Reims"],
    "52 - Haute-Marne": ["Chaumont"],
    "53 - Mayenne": ["Laval"],
    "54 - Meurthe-et-Moselle": ["Nancy"],
    "55 - Meuse": ["Bar-le-Duc"],
    "56 - Morbihan": ["Vannes"],
    "57 - Moselle": ["Metz"],
    "58 - Nièvre": ["Nevers"],
    "59 - Nord": ["Lille"],
    "60 - Oise": ["Beauvais"],
    "61 - Orne": ["Alençon"],
    "62 - Pas-de-Calais": ["Calais"],
    "63 - Puy-de-Dôme": ["Clermont-Ferrand"],
    "64 - Pyr.-Atlantiques": ["Pau", "Bayonne"],
    "65 - Hautes-Pyrénées": ["Tarbes"],
    "66 - Pyr.-Orientales": ["Perpignan"],
    "67 - Bas-Rhin": ["Strasbourg"],
    "68 - Haut-Rhin": ["Mulhouse"],
    "69 - Rhône": ["Lyon"],
    "70 - Haute-Saône": ["Vesoul"],
    "71 - Saône-et-Loire": ["Mâcon"],
    "72 - Sarthe": ["Le Mans"],
    "73 - Savoie": ["Chambéry"],
    "74 - Haute-Savoie": ["Annecy"],
    "75 - Paris": ["Paris"],
    "76 - Seine-Maritime": ["Rouen"],
    "77 - Seine-et-Marne": ["Melun"],
    "78 - Yvelines": ["Versailles"],
    "79 - Deux-Sèvres": ["Niort"],
    "80 - Somme": ["Amiens"],
    "81 - Tarn": ["Albi"],
    "82 - Tarn-et-Garonne": ["Montauban"],
    "83 - Var": ["Toulon"],
    "84 - Vaucluse": ["Avignon"],
    "85 - Vendée": ["La Roche-sur-Yon"],
    "86 - Vienne": ["Poitiers"],
    "87 - Haute-Vienne": ["Limoges"],
    "88 - Vosges": ["Épinal"],
    "89 - Yonne": ["Auxerre"],
    "90 - Terr. de Belfort": ["Belfort"],
    "91 - Essonne": ["Évry"],
    "92 - Hauts-de-Seine": ["Nanterre"],
    "93 - Seine-Saint-Denis": ["Bobigny"],
    "94 - Val-de-Marne": ["Créteil"],
    "95 - Val-d'Oise": ["Pontoise"],
}

# --- MOTEUR DE DISTANCE ---
def get_route_distance(dept_start, dept_end):
    if dept_start == dept_end: return 50
    if dept_start not in DEPT_GPS or dept_end not in DEPT_GPS: return 0
    
    lat1, lon1 = DEPT_GPS[dept_start]
    lat2, lon2 = DEPT_GPS[dept_end]

    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
        r = requests.get(url, timeout=2)
        if r.status_code == 200:
            data = r.json()
            return int(data["routes"][0]["distance"] / 1000)
    except:
        pass
    
    R = 6371 
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return int(R * c * 1.30)

# --- FONCTION FLUX ---
ZONES_FORTES = ["59", "62", "75", "92", "93", "94", "69", "67", "68", "44", "35", "31"]
def get_flux_coef(dep_full_name_start, dep_full_name_end):
    code_start = dep_full_name_start.split(" - ")[0]
    code_end = dep_full_name_end.split(" - ")[0]
    coef = 1.0
    if code_start in ZONES_FORTES and code_end not in ZONES_FORTES: coef = 1.05 
    elif code_start not in ZONES_FORTES and code_end in ZONES_FORTES: coef = 0.92 
    return coef

# --- GÉNÉRATEUR EXCEL (AVEC ANTI-CHUTE) ---
def generate_excel_grid(dept_depart, base_km, base_fixe, min_regional):
    output = io.BytesIO()
    code_dep_start = dept_depart.split(" - ")[0]
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    total_steps = len(FULL_GEO_DATA)
    current_step = 0
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Styles
        fmt_title = workbook.add_format({'bold': True, 'font_size': 14, 'font_color': '#1E3A8A'})
        fmt_info = workbook.add_format({'font_size': 10, 'italic': True})
        fmt_header = workbook.add_format({'bold': True, 'bg_color': '#1E3A8A', 'font_color': 'white', 'border': 1, 'align': 'center'})
        fmt_currency = workbook.add_format({'num_format': '#,##0 €', 'border': 1})
        fmt_km = workbook.add_format({'num_format': '0', 'border': 1, 'align': 'center', 'bg_color': '#E0F2F1'}) 
        fmt_bold_price = workbook.add_format({'num_format': '#,##0 €', 'border': 1, 'bold': True, 'bg_color': '#D1FAE5'})

        company_info = [
            "OPTIVIA TRANSPORTS",
            "21 Allée Jean Jaurès 31000 Toulouse",
            "Tel: 05 32 78 00 08 | contact@optivia-transports.com",
            "SIRET: 880 457 437 00023"
        ]

        # Cache distances
        DISTANCES_CACHE = {}
        status_text.text("🚀 Calcul des itinéraires en cours...")
        for dept_dest in FULL_GEO_DATA.keys():
            code_dep_dest = dept_dest.split(" - ")[0]
            dist = get_route_distance(code_dep_start, code_dep_dest)
            DISTANCES_CACHE[dept_dest] = dist
            current_step += 1
            progress_bar.progress(current_step / total_steps)
        status_text.text("✅ Génération du fichier Excel...")

        def create_sheet(sheet_name, max_pal, pal_type_label):
            ws = workbook.add_worksheet(sheet_name)
            
            logo_path = "logo.png"
            logo_inserted = False
            if os.path.exists(logo_path):
                try:
                    ws.insert_image('A1', logo_path, {'x_scale': 0.15, 'y_scale': 0.15, 'x_offset': 10, 'y_offset': 10})
                    logo_inserted = True
                    start_row = 6
                except:
                    start_row = 0
            else:
                start_row = 0

            text_row = 0 if not logo_inserted else 0
            text_col = 2 if logo_inserted else 0
            for i, line in enumerate(company_info):
                ws.write(text_row + i, text_col, line, fmt_title if i==0 else fmt_info)
            
            ws.write(start_row + 5, 0, f"GRILLE TARIFAIRE AU DÉPART DE : {dept_depart}", fmt_title)
            ws.write(start_row + 6, 0, f"Type de palette : {pal_type_label}", fmt_info)
            ws.write(start_row + 7, 0, f"Plancher Complet Régional appliqué : {min_regional} € HT", fmt_info)
            
            headers = ["Département", "Distance (km)"] + [f"{i} Pal" for i in range(1, max_pal + 1)]
            row_header = start_row + 8
            ws.write_row(row_header, 0, headers, fmt_header)
            
            row = row_header + 1
            for dept_dest in FULL_GEO_DATA.keys():
                dist_val = DISTANCES_CACHE.get(dept_dest, 0)
                flux = get_flux_coef(dept_depart, dept_dest)
                
                ws.write(row, 0, dept_dest)
                ws.write(row, 1, dist_val, fmt_km)
                
                for i in range(1, max_pal + 1):
                    col_idx = i + 1
                    
                    if max_pal == 33: # 80x120
                        ratio = i / 33
                        if i == 1: factor = 0.40
                        elif i <= 5: factor = 0.45
                        elif i <= 15: factor = 0.75
                        else: factor = 0.90
                    elif max_pal == 26: # 100x120
                        ratio = i / 26
                        if i == 1: factor = 0.40
                        elif i <= 4: factor = 0.45
                        elif i <= 12: factor = 0.75
                        else: factor = 0.90
                    elif max_pal == 24: # 120x120
                        ratio = i / 24
                        if i == 1: factor = 0.37
                        elif i <= 4: factor = 0.42
                        elif i <= 12: factor = 0.80
                        else: factor = 0.95
                    
                    # Logique de prix
                    price_full_theo = f"(($B{row+1}*{base_km}+{base_fixe})*{flux})"
                    price_full_floored = f"MAX({price_full_theo}, {min_regional})"
                    curve = f"POWER({ratio},{factor})"
                    
                    # --- LE CLIQUET ANTI-RETOUR ---
                    # Le prix de la palette (i) ne doit jamais être inférieur à la palette (i-1)
                    # Sauf pour la palette 1 qui n'a pas de précédent
                    
                    calc_current = f"{price_full_floored} * {curve}"
                    
                    if i == 1:
                        # Pas de précédent
                        formula = f"=IF($B{row+1}>0, MAX(120, {calc_current}), 0)"
                    else:
                        # On compare avec la cellule de gauche (i-1)
                        # xlsxwriter permet de référencer des cellules
                        prev_cell = xlsxwriter.utility.xl_rowcol_to_cell(row, col_idx - 1)
                        formula = f"=IF($B{row+1}>0, MAX(120, {calc_current}, {prev_cell}), 0)"
                    
                    style = fmt_bold_price if i == max_pal else fmt_currency
                    ws.write_formula(row, col_idx, formula, style)
                row += 1
                
            ws.set_column(0, 0, 25)
            ws.set_column(1, 1, 12)
            ws.set_column(2, max_pal + 1, 8)

        create_sheet("EURO 80x120", 33, "Europe 80x120 (Base 33)")
        create_sheet("ISO 100x120", 26, "Industrie 100x120 (Base 26)")
        create_sheet("CHEP 120x120", 24, "Grand Format 120x120 (Base 24)")
        
    status_text.empty()
    progress_bar.empty()
    return output.getvalue()


# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Moteur & Export")
    mode = st.radio("Mode", ["Calculateur Rapide", "Générateur Excel"], index=0)
    
    st.divider()
    base_km_sell = st.number_input("Prix Vente / Km (€)", value=1.30, step=0.05)
    fixed_sell = st.number_input("Fixe Vente (€)", value=80, step=10)
    min_regional = st.number_input("Plancher Régional Complet (€)", value=320, step=10, help="Prix minimum d'un camion complet, même pour 10km")
    target_margin = st.slider("Marge Visée (%)", 15, 40, 25)

# --- MODE 1 : CALCULATEUR ---
if mode == "Calculateur Rapide":
    st.title("🚛 CALCULATEUR OPTIVIA")
    
    c1, c2 = st.columns([1, 1])
    with c1:
        dept_start = st.selectbox("DÉPART", list(FULL_GEO_DATA.keys()), index=10) # 11
        city_start = st.selectbox("Ville Départ", FULL_GEO_DATA[dept_start])

    with c2:
        dept_end = st.selectbox("ARRIVÉE", list(FULL_GEO_DATA.keys()), index=16) # 17
        city_end = st.selectbox("Ville Arrivée", FULL_GEO_DATA[dept_end])

    st.markdown("---")
    c_dist, c_info = st.columns([1, 2])

    with c_dist:
        code_s = dept_start.split(" - ")[0]
        code_e = dept_end.split(" - ")[0]
        auto_dist = get_route_distance(code_s, code_e)
        
        st.markdown("👇 **SAISIR LES KM ICI**")
        dist_reelle = st.number_input("Distance Réelle (km)", min_value=0, value=auto_dist)
        if auto_dist > 0:
            st.caption(f"Estimation auto : {auto_dist} km")

    flux_coef = get_flux_coef(dept_start, dept_end)
    flux_label = "➡️ Flux Standard"
    flux_color = "blue"
    if flux_coef > 1: 
        flux_label = "📈 Départ Zone Forte (+5%)"
        flux_color = "red"
    elif flux_coef < 1: 
        flux_label = "📉 Flux Retour (-8%)"
        flux_color = "green"

    with c_info:
        if flux_coef != 1.0:
            st.markdown(f"<div class='zone-info' style='color:{flux_color}'>{flux_label}</div>", unsafe_allow_html=True)
        if dist_reelle == 0:
            st.warning("⚠️ Merci de saisir la distance réelle.")

    st.subheader("📦 La Marchandise")
    c_type, c_qty = st.columns(2)
    with c_type:
        unit_type = st.radio("Type", ["Palettes (80x120)", "Palettes (100x120)", "Mètres", "Complet"], horizontal=True)
    with c_qty:
        qty = 0; ratio = 1.0; power_factor = 1.0; cle_tarif = "Standard"
        if "80x120" in unit_type:
            qty = st.number_input("Nb Pal (80x120)", 1, 33, 3)
            ratio = qty / 33
            if qty == 1: power_factor = 0.40; cle_tarif = "P40"
            elif qty <= 5: power_factor = 0.45; cle_tarif = "P45"
            elif qty <= 15: power_factor = 0.75; cle_tarif = "P39"
            else: power_factor = 0.90; cle_tarif = "P26"
        elif "100x120" in unit_type:
            qty = st.number_input("Nb Pal (100x120)", 1, 26, 3)
            ratio = qty / 26
            if qty == 1: power_factor = 0.40; cle_tarif = "P40"
            elif qty <= 4: power_factor = 0.45; cle_tarif = "P45"
            elif qty <= 12: power_factor = 0.75; cle_tarif = "P39"
            else: power_factor = 0.90; cle_tarif = "P26"
        elif "Mètres" in unit_type:
            metres = st.number_input("Mètres", 0.0, 13.6, 2.0)
            ratio = metres / 13.6
            if metres <= 1.0: power_factor = 0.40; cle_tarif = "Mini"
            elif metres <= 2.4: power_factor = 0.55; cle_tarif = "P60"
            else: power_factor = 0.85; cle_tarif = "Std"
        else:
            cle_tarif = "Complet"

    st.subheader("🔧 Options")
    c_opt1, c_opt2, c_opt3 = st.columns(3)
    with c_opt1: opt_hayon = st.checkbox("Hayon (+50€)")
    with c_opt2: opt_adr = st.checkbox("ADR (+20%)")
    with c_opt3: opt_montagne = st.checkbox("Montagne (+25%)")

    if dist_reelle > 0:
        base_price = (dist_reelle * base_km_sell) + fixed_sell
        base_price_geo = base_price * flux_coef 
        
        if base_price_geo < min_regional:
            st.toast(f"ℹ️ Distance courte : Application du plancher complet à {min_regional}€")
            base_price_geo = min_regional

        final_base = base_price_geo * (ratio ** power_factor)
        if final_base < 120: final_base = 120
        if opt_montagne: final_base = final_base * 1.25
        
        options_val = 0
        if opt_hayon: options_val += 50
        if opt_adr: 
            adr = final_base * 0.20
            if adr < 30: adr = 30
            options_val += adr
        FINAL_SELL = final_base + options_val
        MAX_BUY = FINAL_SELL * (1 - (target_margin/100))
    else:
        FINAL_SELL = 0
        MAX_BUY = 0

    st.divider()
    r1, r2 = st.columns(2)
    with r1:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.markdown("### 💰 PRIX CLIENT")
        if dist_reelle > 0:
            st.markdown(f'<p class="client-price">{FINAL_SELL:.0f} € HT</p>', unsafe_allow_html=True)
            st.caption(f"Clé: {cle_tarif} | {dist_reelle} km")
        else:
            st.warning("Saisir distance")
        st.markdown('</div>', unsafe_allow_html=True)
    with r2:
        st.markdown('<div class="kpi-card" style="border-left: 5px solid #DC2626;">', unsafe_allow_html=True)
        st.markdown("### 🛑 ACHAT MAX")
        if dist_reelle > 0:
            st.markdown(f'<p class="buy-limit">{MAX_BUY:.0f} € HT</p>', unsafe_allow_html=True)
        else:
            st.write("-")
        st.markdown('</div>', unsafe_allow_html=True)

# --- MODE 2 : GÉNÉRATEUR EXCEL ---
else:
    st.title("📊 GÉNÉRATEUR DE GRILLE TARIFAIRE")
    st.markdown("### Créez votre grille tarifaire nationale en 1 clic")
    
    col_sel, col_btn = st.columns([1, 1])
    with col_sel:
        dept_export = st.selectbox("CHOISIR LE DÉPARTEMENT DE DÉPART", list(FULL_GEO_DATA.keys()), index=10) # 11 par défaut
    
    st.info("⚠️ **Patience :** Le calcul des distances réelles pour 95 départements prend environ 15 secondes.")
    
    if st.button("LANCER LE CALCUL ET PRÉPARER LE FICHIER"):
        excel_data = generate_excel_grid(dept_export, base_km_sell, fixed_sell, min_regional)
        
        st.success("✅ Fichier prêt !")
        st.download_button(
            label=f"📥 TÉLÉCHARGER LA GRILLE ({dept_export})",
            data=excel_data,
            file_name=f"Grille_Optivia_Depart_{dept_export.split(' - ')[0]}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
