import streamlit as st

# --- CONFIGURATION ---
st.set_page_config(page_title="CALCULATEUR OPTIVIA", page_icon="🚛", layout="wide")

# --- STYLE VISUEL ---
st.markdown("""
    <style>
    .client-price { font-size: 32px !important; font-weight: bold; color: #1E3A8A; } 
    .buy-limit { font-size: 32px !important; font-weight: bold; color: #DC2626; } 
    .kpi-card { background-color: #F3F4F6; padding: 15px; border-radius: 10px; border-left: 5px solid #1E3A8A; margin-bottom: 10px;}
    .zone-info { color: #854d0e; background-color: #fef9c3; padding: 10px; border-radius: 5px; font-weight: bold; margin-bottom: 10px;}
    .big-input .stNumberInput > div > div > input { font-size: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DONNÉES GÉOGRAPHIQUE ---
FULL_GEO_DATA = {
    "01 - Ain": ["Belley", "Bourg-en-Bresse", "Gex", "Nantua"],
    "02 - Aisne": ["Château-Thierry", "Laon", "Saint-Quentin", "Soissons", "Vervins"],
    "03 - Allier": ["Montluçon", "Vichy", "Yseure"],
    "04 - Alpes-Htes-Prov.": ["Barcelonnette", "Castellane", "Digne-les-Bains", "Forcalquier"],
    "05 - Hautes-Alpes": ["Briançon", "Gap"],
    "06 - Alpes-Maritimes": ["Grasse", "Nice"],
    "07 - Ardèche": ["Largentière", "Privas", "Tournon-sur-Rhône"],
    "08 - Ardennes": ["Charleville-Mézières", "Rethel", "Sedan", "Vouziers"],
    "09 - Ariège": ["Foix", "Pamiers", "Saint-Girons"],
    "10 - Aube": ["Bar-sur-Aube", "Nogent-sur-Seine", "Troyes"],
    "11 - Aude": ["Carcassonne", "Limoux", "Narbonne"],
    "12 - Aveyron": ["Millau", "Rodez", "Villefranche-de-Rouergue"],
    "13 - Bouches-du-Rhône": ["Aix-en-Provence", "Arles", "Istres", "Marseille"],
    "14 - Calvados": ["Bayeux", "Caen", "Lisieux", "Vire"],
    "15 - Cantal": ["Aurillac", "Mauriac", "Saint-Flour"],
    "16 - Charente": ["Angoulême", "Cognac", "Confolens"],
    "17 - Charente-Maritime": ["Jonzac", "La Rochelle", "Rochefort", "Saintes", "Saint-Jean-d'Angély"],
    "18 - Cher": ["Bourges", "Saint-Amand-Montrond", "Vierzon"],
    "19 - Corrèze": ["Brive-la-Gaillarde", "Tulle", "Ussel"],
    "20 - Corse": ["Ajaccio", "Bastia", "Calvi", "Corte", "Sartène"],
    "21 - Côte-d'Or": ["Beaune", "Dijon", "Montbard"],
    "22 - Côtes-d'Armor": ["Dinan", "Guingamp", "Lannion", "Saint-Brieuc"],
    "23 - Creuse": ["Aubusson", "Guéret"],
    "24 - Dordogne": ["Bergerac", "Nontron", "Périgueux", "Sarlat-la-Canéda"],
    "25 - Doubs": ["Besançon", "Montbéliard", "Pontarlier"],
    "26 - Drôme": ["Die", "Nyons", "Valence"],
    "27 - Eure": ["Bernay", "Évreux", "Les Andelys"],
    "28 - Eure-et-Loir": ["Chartres", "Châteaudun", "Dreux", "Nogent-le-Rotrou"],
    "29 - Finistère": ["Brest", "Châteaulin", "Morlaix", "Quimper"],
    "30 - Gard": ["Alès", "Le Vigan", "Nîmes"],
    "31 - Haute-Garonne": ["Muret", "Saint-Gaudens", "Toulouse", "Eurocentre", "Fronton"],
    "32 - Gers": ["Auch", "Condom", "Mirande"],
    "33 - Gironde": ["Arcachon", "Blaye", "Bordeaux", "Langon", "Lesparre-Médoc", "Libourne"],
    "34 - Hérault": ["Béziers", "Lodève", "Montpellier"],
    "35 - Ille-et-Vilaine": ["Fougères", "Redon", "Rennes", "Saint-Malo"],
    "36 - Indre": ["Châteauroux", "Issoudun", "La Châtre", "Le Blanc"],
    "37 - Indre-et-Loire": ["Chinon", "Loches", "Tours"],
    "38 - Isère": ["Grenoble", "La Tour-du-Pin", "Vienne"],
    "39 - Jura": ["Dole", "Lons-le-Saunier", "Saint-Claude"],
    "40 - Landes": ["Dax", "Mont-de-Marsan"],
    "41 - Loir-et-Cher": ["Blois", "Romorantin-Lanthenay", "Vendôme"],
    "42 - Loire": ["Montbrison", "Roanne", "Saint-Étienne"],
    "43 - Haute-Loire": ["Brioude", "Le Puy-en-Velay", "Yssingeaux"],
    "44 - Loire-Atlantique": ["Ancenis", "Châteaubriant", "Nantes", "Saint-Nazaire"],
    "45 - Loiret": ["Montargis", "Orléans", "Pithiviers"],
    "46 - Lot": ["Cahors", "Figeac", "Gourdon"],
    "47 - Lot-et-Garonne": ["Agen", "Marmande", "Nérac", "Villeneuve-sur-Lot"],
    "48 - Lozère": ["Florac", "Mende"],
    "49 - Maine-et-Loire": ["Angers", "Cholet", "Saumur", "Segré"],
    "50 - Manche": ["Avranches", "Cherbourg-Octeville", "Coutances", "Saint-Lô"],
    "51 - Marne": ["Châlons-en-Champagne", "Épernay", "Reims", "Sainte-Menehould", "Vitry-le-François"],
    "52 - Haute-Marne": ["Chaumont", "Langres", "Saint-Dizier"],
    "53 - Mayenne": ["Château-Gontier", "Laval", "Mayenne"],
    "54 - Meurthe-et-Moselle": ["Briey", "Lunéville", "Nancy", "Toul"],
    "55 - Meuse": ["Bar-le-Duc", "Commercy", "Verdun"],
    "56 - Morbihan": ["Lorient", "Pontivy", "Vannes"],
    "57 - Moselle": ["Boulay-Moselle", "Château-Salins", "Forbach", "Metz", "Sarrebourg", "Sarreguemines", "Thionville"],
    "58 - Nièvre": ["Château-Chinon", "Clamecy", "Cosne-Cours-sur-Loire", "Nevers"],
    "59 - Nord": ["Avesnes-sur-Helpe", "Cambrai", "Douai", "Dunkerque", "Lille", "Valenciennes"],
    "60 - Oise": ["Beauvais", "Clermont", "Compiègne", "Senlis"],
    "61 - Orne": ["Alençon", "Argentan", "Mortagne-au-Perche"],
    "62 - Pas-de-Calais": ["Arras", "Béthune", "Boulogne-sur-Mer", "Calais", "Lens", "Montreuil", "Saint-Omer"],
    "63 - Puy-de-Dôme": ["Ambert", "Clermont-Ferrand", "Issoire", "Riom", "Thiers"],
    "64 - Pyr.-Atlantiques": ["Bayonne", "Oloron-Sainte-Marie", "Pau"],
    "65 - Hautes-Pyrénées": ["Argelès-Gazost", "Bagnères-de-Bigorre", "Tarbes"],
    "66 - Pyr.-Orientales": ["Céret", "Perpignan", "Prades"],
    "67 - Bas-Rhin": ["Haguenau", "Molsheim", "Saverne", "Sélestat", "Strasbourg", "Wissembourg"],
    "68 - Haut-Rhin": ["Altkirch", "Colmar", "Guebwiller", "Mulhouse", "Ribeauvillé", "Thann"],
    "69 - Rhône": ["Lyon", "Villefranche-sur-Saône"],
    "70 - Haute-Saône": ["Lure", "Vesoul"],
    "71 - Saône-et-Loire": ["Autun", "Chalon-sur-Saône", "Charolles", "Louhans", "Mâcon"],
    "72 - Sarthe": ["La Flèche", "Le Mans", "Mamers"],
    "73 - Savoie": ["Albertville", "Chambéry", "Saint-Jean-de-Maurienne"],
    "74 - Haute-Savoie": ["Annecy", "Bonneville", "Saint-Julien-en-Genevois", "Thonon-les-Bains"],
    "75 - Paris": ["Paris Intramuros"],
    "76 - Seine-Maritime": ["Dieppe", "Le Havre", "Rouen"],
    "77 - Seine-et-Marne": ["Fontainebleau", "Meaux", "Melun", "Provins", "Torcy"],
    "78 - Yvelines": ["Mantes-la-Jolie", "Rambouillet", "Saint-Germain-en-Laye", "Versailles"],
    "79 - Deux-Sèvres": ["Bressuire", "Niort", "Parthenay"],
    "80 - Somme": ["Abbeville", "Amiens", "Montdidier", "Péronne"],
    "81 - Tarn": ["Albi", "Castres"],
    "82 - Tarn-et-Garonne": ["Castelsarrasin", "Montauban"],
    "83 - Var": ["Brignoles", "Draguignan", "Toulon"],
    "84 - Vaucluse": ["Apt", "Avignon", "Carpentras"],
    "85 - Vendée": ["Fontenay-le-Comte", "La Roche-sur-Yon", "Les Sables-d'Olonne"],
    "86 - Vienne": ["Châtellerault", "Montmorillon", "Poitiers"],
    "87 - Haute-Vienne": ["Bellac", "Limoges", "Rochechouart"],
    "88 - Vosges": ["Épinal", "Neufchâteau", "Saint-Dié-des-Vosges"],
    "89 - Yonne": ["Auxerre", "Avallon", "Sens"],
    "90 - Terr. de Belfort": ["Belfort"],
    "91 - Essonne": ["Étampes", "Évry", "Palaiseau"],
    "92 - Hauts-de-Seine": ["Antony", "Boulogne-Billancourt", "Nanterre"],
    "93 - Seine-Saint-Denis": ["Bobigny", "Le Raincy", "Saint-Denis"],
    "94 - Val-de-Marne": ["Créteil", "L'Haÿ-les-Roses", "Nogent-sur-Marne"],
    "95 - Val-d'Oise": ["Argenteuil", "Pontoise", "Sarcelles"],
    "98 - Monaco": ["Monaco"]
}

# --- FONCTION FLUX ---
ZONES_FORTES = ["59", "62", "75", "92", "93", "94", "69", "67", "68", "44", "35", "31"]

def get_flux_coef(dep_full_name_start, dep_full_name_end):
    code_start = dep_full_name_start.split(" - ")[0]
    code_end = dep_full_name_end.split(" - ")[0]
    
    coef = 1.0
    # 1. Départ Zone Forte vers Province (Cher)
    if code_start in ZONES_FORTES and code_end not in ZONES_FORTES:
        coef = 1.05 
    # 2. Retour Province vers Zone Forte (Moins cher)
    elif code_start not in ZONES_FORTES and code_end in ZONES_FORTES:
        coef = 0.92 
    return coef

# --- SIDEBAR (NOUVEAUX RÉGLAGES MARCHÉ) ---
with st.sidebar:
    st.header("⚙️ Moteur Tarifret")
    # J'ai baissé ces valeurs pour coller à ton marché (655€ pour 441km)
    base_km_sell = st.number_input("Prix Vente / Km (€)", value=1.30, step=0.05)
    fixed_sell = st.number_input("Fixe Vente (€)", value=80, step=10)
    st.divider()
    target_margin = st.slider("Objectif Marge (%)", 15, 40, 25)

# --- TITRE ---
st.title("🚛 CALCULATEUR OPTIVIA")

# --- BLOC 1 : LE TRAJET ---
st.subheader("📍 Origine & Destination")

c1, c2 = st.columns([1, 1])
with c1:
    dept_start = st.selectbox("DÉPART", list(FULL_GEO_DATA.keys()), index=10) # 11 Aude
    city_start = st.selectbox("Ville Départ", FULL_GEO_DATA[dept_start])

with c2:
    dept_end = st.selectbox("ARRIVÉE", list(FULL_GEO_DATA.keys()), index=16) # 17 Charente
    city_end = st.selectbox("Ville Arrivée", FULL_GEO_DATA[dept_end])

# --- DISTANCE & FLUX ---
st.markdown("---")
c_dist, c_info = st.columns([1, 2])

with c_dist:
    st.markdown("👇 **SAISIR LES KM ICI**")
    # MISE A ZERO PAR DEFAUT
    dist_reelle = st.number_input("Distance Réelle (km)", min_value=0, value=0)
    st.caption("Distance Google Maps")

# Calcul Flux
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
    
    # Alerte si distance est à 0
    if dist_reelle == 0:
        st.warning("⚠️ Merci de saisir la distance réelle pour calculer le prix.")
    else:
        st.success(f"Calcul sur base {dist_reelle} km")

# --- BLOC 2 : MARCHANDISE ---
st.subheader("📦 La Marchandise")
c_type, c_qty = st.columns(2)

with c_type:
    unit_type = st.radio("Type", ["Palettes (80x120)", "Palettes (100x120)", "Mètres", "Complet"], horizontal=True)

with c_qty:
    qty = 0; ratio = 1.0; power_factor = 1.0; cle_tarif = "Standard"
    
    if "80x120" in unit_type:
        qty = st.number_input("Nb Pal (80x120)", 1, 33, 3)
        ratio = qty / 33
        if qty <= 5: power_factor = 0.55; cle_tarif = "P60 (Petit Lot)"
        elif qty <= 15: power_factor = 0.75; cle_tarif = "P39 (Moyen)"
        else: power_factor = 0.90; cle_tarif = "P26 (Gros)"
    elif "100x120" in unit_type:
        qty = st.number_input("Nb Pal (100x120)", 1, 26, 3)
        ratio = qty / 26
        if qty <= 4: power_factor = 0.55; cle_tarif = "P60"
        elif qty <= 12: power_factor = 0.75; cle_tarif = "P39"
        else: power_factor = 0.90; cle_tarif = "P26"
    elif "Mètres" in unit_type:
        metres = st.number_input("Mètres", 0.0, 13.6, 2.0)
        ratio = metres / 13.6
        if metres <= 2.4: power_factor = 0.55; cle_tarif = "P60"
        else: power_factor = 0.85; cle_tarif = "Standard"
    else:
        cle_tarif = "Complet"

# --- OPTIONS ---
st.subheader("🔧 Options & Forfaits")
c_opt1, c_opt2, c_opt3 = st.columns(3)

with c_opt1: 
    opt_hayon = st.checkbox("Hayon (+50€)")
    opt_stop = st.checkbox("Stop Sup (+50€)")
with c_opt2: 
    opt_adr = st.checkbox("ADR (+20%)")
    opt_frais = st.checkbox("Frais Dossier (+15€)", value=True)
with c_opt3:
    st.markdown("**Accès Difficile / Montagne**")
    opt_montagne = st.checkbox("Activer Majoration (+25%)")

# --- MOTEUR DE CALCUL FINAL ---
if dist_reelle > 0:
    # 1. Base km (AVEC NOUVEAUX PARAMETRES)
    base_price = (dist_reelle * base_km_sell) + fixed_sell

    # 2. Application Coef Flux
    base_price_geo = base_price * flux_coef 

    # 3. Application Partiel
    final_base = base_price_geo * (ratio ** power_factor)

    if final_base < 120: final_base = 120

    # 4. Majoration Montagne
    if opt_montagne:
        final_base = final_base * 1.25

    # 5. Options
    options_val = 0
    if opt_hayon: options_val += 50
    if opt_stop: options_val += 50
    if opt_frais: options_val += 15
    if opt_adr: 
        adr = final_base * 0.20
        if adr < 30: adr = 30
        options_val += adr

    FINAL_SELL = final_base + options_val
    MAX_BUY = FINAL_SELL * (1 - (target_margin/100))
else:
    FINAL_SELL = 0
    MAX_BUY = 0

# --- RÉSULTATS ---
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
        st.caption(f"Plafond pour {target_margin}% de marge")
    else:
        st.write("-")
    st.markdown('</div>', unsafe_allow_html=True)
