import streamlit as st

# --- CONFIGURATION ---
st.set_page_config(page_title="OPTIVIA DEAL MAKER", page_icon="🎯", layout="wide")

# --- STYLE VISUEL ---
st.markdown("""
    <style>
    .client-price { font-size: 32px !important; font-weight: bold; color: #1E3A8A; } 
    .buy-limit { font-size: 32px !important; font-weight: bold; color: #DC2626; } 
    .kpi-card { background-color: #F3F4F6; padding: 15px; border-radius: 10px; border-left: 5px solid #1E3A8A; margin-bottom: 10px;}
    .zone-info { color: #854d0e; background-color: #fef9c3; padding: 10px; border-radius: 5px; font-weight: bold;}
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DONNÉES GÉOGRAPHIQUE (EXTRAIT TARIFRET) ---
# C'est ici qu'on définit les points précis dans chaque département
GEO_DATA = {
    "31 - Haute Garonne": {
        "Toulouse / Eurocentre (Standard)": {"km_delta": 0, "montagne": False},
        "Fronton (Nord - Accès A62)": {"km_delta": -15, "montagne": False},
        "St Gaudens (Sud - A64)": {"km_delta": 90, "montagne": False},
        "Bagnères de Luchon (Montagne)": {"km_delta": 140, "montagne": True, "acces_diff": True},
        "Revel / Villefranche (Est)": {"km_delta": 30, "montagne": False}
    },
    "09 - Ariège": {
        "Pamiers / Foix (Vallée)": {"km_delta": 0, "montagne": False},
        "Ax-les-Thermes / Andorre (Montagne)": {"km_delta": 40, "montagne": True},
        "St Girons (Couserans)": {"km_delta": 30, "montagne": True}
    },
    "65 - Hautes Pyrénées": {
        "Tarbes / Lourdes (Plaine)": {"km_delta": 0, "montagne": False},
        "Argelès / Cauterets (Montagne)": {"km_delta": 30, "montagne": True},
        "Lannemezan (Plateau)": {"km_delta": 35, "montagne": False}
    },
    "59 - Nord": {
        "Lille / Lesquin (Standard)": {"km_delta": 0, "montagne": False},
        "Dunkerque (Port)": {"km_delta": 80, "montagne": False},
        "Valenciennes": {"km_delta": 50, "montagne": False}
    },
    "75 - Paris (IdF)": {
        "Paris / Petite Couronne (Standard)": {"km_delta": 0, "montagne": False},
        "Grande Couronne (77/78/91/95)": {"km_delta": 40, "montagne": False}
    },
    "Autre Département": {
        "Chef-lieu / Préfecture": {"km_delta": 0, "montagne": False},
        "Zone Montagne / Difficile": {"km_delta": 40, "montagne": True}
    }
}

# Fonction pour calculer le coefficient de marché (Flux Nord/Sud)
ZONES_FORTES = ["59 - Nord", "62 - Pas de Calais", "75 - Paris (IdF)", "69 - Rhône", "67 - Bas Rhin"]
def get_flux_coef(dep_name_start, dep_name_end):
    coef = 1.0
    # Départ Zone Forte vers Province (Cher)
    if dep_name_start in ZONES_FORTES and dep_name_end not in ZONES_FORTES:
        coef = 1.05 
    # Retour vers Zone Forte (Moins cher)
    elif dep_name_start not in ZONES_FORTES and dep_name_end in ZONES_FORTES:
        coef = 0.92 
    return coef

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Moteur Tarifret")
    base_km_sell = st.number_input("Prix Vente / Km (€)", value=1.55, step=0.05)
    fixed_sell = st.number_input("Fixe Vente (€)", value=250, step=10)
    st.divider()
    target_margin = st.slider("Objectif Marge (%)", 15, 40, 25)

# --- TITRE ---
st.title("🎯 OPTIVIA DEAL MAKER")

# --- BLOC 1 : LE TRAJET DE PRÉCISION ---
st.subheader("📍 Origine & Destination")

# --- LIGNE DÉPART ---
c1, c2 = st.columns([1, 1])
with c1:
    dept_start = st.selectbox("Département Départ", list(GEO_DATA.keys()), index=0)
with c2:
    # Le menu déroulant des villes s'adapte au département choisi
    city_start = st.selectbox("Ville / Zone de Départ", list(GEO_DATA[dept_start].keys()))

# Récupération des données précises du point de départ
data_start = GEO_DATA[dept_start][city_start]

# --- LIGNE ARRIVÉE ---
c3, c4 = st.columns([1, 1])
with c3:
    dept_end = st.selectbox("Département Arrivée", list(GEO_DATA.keys()), index=4) # Par défaut Paris
with c4:
    city_end = st.selectbox("Ville / Zone d'Arrivée", list(GEO_DATA[dept_end].keys()))

data_end = GEO_DATA[dept_end][city_end]

# --- DISTANCE & FLUX ---
st.markdown("---")
c_dist, c_info = st.columns([1, 2])
with c_dist:
    dist_ref = st.number_input("Distance de Réf (Préfecture à Préfecture)", min_value=1, value=700)

# CALCUL DES CORRECTIONS GÉOGRAPHIQUES
# 1. Ajustement Distance (Si on part de Luchon, c'est + loin que Toulouse)
dist_reelle = dist_ref + data_start['km_delta'] + data_end['km_delta']

# 2. Surcharge Montagne / Accès
montagne_surcharge = 1.0
msg_zone = []

if data_start['montagne']:
    montagne_surcharge += 0.15 # +15% si départ montagne
    msg_zone.append(f"🏔️ Départ Montagne (+15%)")
if data_end['montagne']:
    montagne_surcharge += 0.15 # +15% si arrivée montagne
    msg_zone.append(f"🏔️ Arrivée Montagne (+15%)")

# 3. Coefficient de Flux (Nord/Sud)
flux_coef = get_flux_coef(dept_start, dept_end)
if flux_coef > 1: msg_zone.append("📈 Départ Zone Forte")
if flux_coef < 1: msg_zone.append("📉 Flux Retour")

with c_info:
    st.markdown(f"**Distance Corrigée :** {dist_ref} km ➔ **{dist_reelle} km**")
    if msg_zone:
        st.markdown(f"<div class='zone-info'>{'  |  '.join(msg_zone)}</div>", unsafe_allow_html=True)
    else:
        st.success("✅ Trajet Standard")

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
c_opt1, c_opt2, c_opt3, c_opt4 = st.columns(4)
with c_opt1: opt_hayon = st.checkbox("Hayon (+50€)")
with c_opt2: opt_stop = st.checkbox("Stop Sup (+50€)")
with c_opt3: opt_adr = st.checkbox("ADR (+20%)")
with c_opt4: opt_frais = st.checkbox("Frais (+15€)", value=True)

# --- MOTEUR DE CALCUL FINAL ---
# 1. Base km sur distance corrigée
base_price = (dist_reelle * base_km_sell) + fixed_sell

# 2. Application Coef Flux (Nord/Sud) ET Coef Montagne (Luchon)
base_price_geo = base_price * flux_coef * montagne_surcharge

# 3. Application Partiel
final_base = base_price_geo * (ratio ** power_factor)

if final_base < 120: final_base = 120

# 4. Options
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

# --- RÉSULTATS ---
st.divider()
r1, r2 = st.columns(2)

with r1:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    st.markdown("### 💰 PRIX CLIENT")
    st.markdown(f'<p class="client-price">{FINAL_SELL:.0f} € HT</p>', unsafe_allow_html=True)
    st.caption(f"Détail : {cle_tarif} | {dist_reelle}km (Réel)")
    st.markdown('</div>', unsafe_allow_html=True)

with r2:
    st.markdown('<div class="kpi-card" style="border-left: 5px solid #DC2626;">', unsafe_allow_html=True)
    st.markdown("### 🛑 ACHAT MAX")
    st.markdown(f'<p class="buy-limit">{MAX_BUY:.0f} € HT</p>', unsafe_allow_html=True)
    st.caption(f"Plafond pour {target_margin}% de marge")
    st.markdown('</div>', unsafe_allow_html=True)
