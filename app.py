import streamlit as st
import pandas as pd
import io
import os

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

# --- DONNÉES GÉOGRAPHIQUES ---
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

# --- FONCTION FLUX ---
ZONES_FORTES = ["59", "62", "75", "92", "93", "94", "69", "67", "68", "44", "35", "31"]
def get_flux_coef(dep_full_name_start, dep_full_name_end):
    code_start = dep_full_name_start.split(" - ")[0]
    code_end = dep_full_name_end.split(" - ")[0]
    coef = 1.0
    if code_start in ZONES_FORTES and code_end not in ZONES_FORTES:
        coef = 1.05 
    elif code_start not in ZONES_FORTES and code_end in ZONES_FORTES:
        coef = 0.92 
    return coef

# --- GÉNÉRATEUR EXCEL ---
def generate_excel_grid(dept_depart, base_km, base_fixe):
    output = io.BytesIO()
    
    # Création du writer Excel
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Styles
        fmt_title = workbook.add_format({'bold': True, 'font_size': 14, 'font_color': '#1E3A8A'})
        fmt_info = workbook.add_format({'font_size': 10, 'italic': True})
        fmt_header = workbook.add_format({'bold': True, 'bg_color': '#1E3A8A', 'font_color': 'white', 'border': 1, 'align': 'center'})
        fmt_currency = workbook.add_format({'num_format': '#,##0 €', 'border': 1})
        fmt_km = workbook.add_format({'num_format': '0', 'bg_color': '#FEF3C7', 'border': 1})
        fmt_bold_price = workbook.add_format({'num_format': '#,##0 €', 'border': 1, 'bold': True, 'bg_color': '#D1FAE5'})

        # Informations Société (si logo absent)
        company_info = [
            "OPTIVIA TRANSPORTS",
            "21 Allée Jean Jaurès 31000 Toulouse",
            "Tel: 05 32 78 00 08 | contact@optivia-transports.com",
            "SIRET: 880 457 437 00023"
        ]

        # --- FONCTION INTERNE POUR CRÉER UNE FEUILLE ---
        def create_sheet(sheet_name, max_pal, pal_type_label):
            ws = workbook.add_worksheet(sheet_name)
            
            # GESTION DU LOGO
            # On vérifie si logo.png existe dans le dossier
            logo_path = "logo.png"
            logo_inserted = False
            
            if os.path.exists(logo_path):
                try:
                    # Insertion logo en haut à gauche (redimensionné)
                    ws.insert_image('A1', logo_path, {'x_scale': 0.15, 'y_scale': 0.15, 'x_offset': 10, 'y_offset': 10})
                    logo_inserted = True
                    # On décale le texte vers le bas si logo
                    start_row = 6
                except:
                    start_row = 0
            else:
                start_row = 0

            # En-tête Texte (Adresse, Siret...)
            # On décale le texte vers la droite (colonne C) si logo présent, ou en dessous
            text_row = 0 if not logo_inserted else 0
            text_col = 2 if logo_inserted else 0
            
            for i, line in enumerate(company_info):
                ws.write(text_row + i, text_col, line, fmt_title if i==0 else fmt_info)
            
            # Titre de la grille
            ws.write(start_row + 5, 0, f"GRILLE TARIFAIRE AU DÉPART DE : {dept_depart}", fmt_title)
            ws.write(start_row + 6, 0, f"Type de palette : {pal_type_label}", fmt_info)
            
            # En-têtes Colonnes
            headers = ["Département", "Distance (km)"] + [f"{i} Pal" for i in range(1, max_pal + 1)]
            row_header = start_row + 8
            ws.write_row(row_header, 0, headers, fmt_header)
            
            # Données
            row = row_header + 1
            for dept_dest in FULL_GEO_DATA.keys():
                flux = get_flux_coef(dept_depart, dept_dest)
                ws.write(row, 0, dept_dest)
                ws.write(row, 1, 0, fmt_km) # Distance à saisir
                
                for i in range(1, max_pal + 1):
                    col_idx = i + 1
                    
                    # Logique Coeff
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
                        if i == 1: factor = 0.45
                        elif i <= 4: factor = 0.50
                        elif i <= 12: factor = 0.80
                        else: factor = 0.95
                    
                    # Formule Excel
                    price_base = f"($B{row+1}*{base_km}+{base_fixe})*{flux}"
                    curve = f"POWER({ratio},{factor})"
                    formula = f"=IF($B{row+1}>0, MAX(120, {price_base} * {curve}), 0)"
                    
                    style = fmt_bold_price if i == max_pal else fmt_currency
                    ws.write_formula(row, col_idx, formula, style)
                row += 1
                
            # Ajustement largeurs
            ws.set_column(0, 0, 25) # Dept
            ws.set_column(1, 1, 12) # Km
            ws.set_column(2, max_pal + 1, 8) # Prix

        # --- CRÉATION DES 3 FEUILLES ---
        create_sheet("EURO 80x120", 33, "Europe 80x120 (Base 33)")
        create_sheet("ISO 100x120", 26, "Industrie 100x120 (Base 26)")
        create_sheet("CHEP 120x120", 24, "Grand Format 120x120 (Base 24)")
            
    return output.getvalue()


# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Moteur & Export")
    mode = st.radio("Mode", ["Calculateur Rapide", "Générateur Excel"], index=0)
    
    st.divider()
    base_km_sell = st.number_input("Prix Vente / Km (€)", value=1.30, step=0.05)
    fixed_sell = st.number_input("Fixe Vente (€)", value=80, step=10)
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
        st.markdown("👇 **SAISIR LES KM ICI**")
        dist_reelle = st.number_input("Distance Réelle (km)", min_value=0, value=0)

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
    
    st.info("💡 **Instructions :** Cliquez sur télécharger. Ouvrez le fichier Excel. Remplissez simplement la colonne jaune 'Distance' pour voir tous les prix s'afficher.")
    
    # Bouton de génération
    excel_data = generate_excel_grid(dept_export, base_km_sell, fixed_sell)
    
    with col_btn:
        st.write("") # Spacer
        st.write("") 
        st.download_button(
            label=f"📥 TÉLÉCHARGER LA GRILLE ({dept_export})",
            data=excel_data,
            file_name=f"Grille_Optivia_Depart_{dept_export.split(' - ')[0]}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
