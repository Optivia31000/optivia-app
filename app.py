import streamlit as st

# --- CONFIGURATION (Titre de l'onglet) ---
st.set_page_config(page_title="CALCULATEUR OPTIVIA", page_icon="🚛", layout="wide")

# --- STYLE VISUEL ---
st.markdown("""
    <style>
    .client-price { font-size: 32px !important; font-weight: bold; color: #1E3A8A; } 
    .buy-limit { font-size: 32px !important; font-weight: bold; color: #DC2626; } 
    .kpi-card { background-color: #F3F4F6; padding: 15px; border-radius: 10px; border-left: 5px solid #1E3A8A; margin-bottom: 10px;}
    </style>
    """, unsafe_allow_html=True)

# --- MENU LATÉRAL (Réglages cachés) ---
with st.sidebar:
    st.header("⚙️ Réglages Tarifret")
    base_km_sell = st.number_input("Prix Vente / Km (€)", value=1.55, step=0.05)
    fixed_sell = st.number_input("Forfait Fixe Vente (€)", value=250, step=10)
    st.divider()
    target_margin = st.slider("Objectif de Marge (%)", 15, 40, 25)

# --- TITRE DE LA PAGE ---
st.title("🚛 CALCULATEUR OPTIVIA")
st.caption(f"Objectif de Marge verrouillé à : {target_margin}%")

# --- BLOC 1 : LE TRAJET ---
col1, col2 = st.columns(2)
with col1:
    distance = st.number_input("📍 Distance (km)", min_value=1, value=450)
with col2:
    # Choix de l'unité avec ajout de la 100x120
    unit_type = st.radio("Unité de chargement", 
                         ["Palettes (80x120)", "Palettes (100x120)", "Mètres de plancher", "Camion Complet"], 
                         horizontal=True)

# --- BLOC 2 : QUANTITÉ & OPTIONS ---
col3, col4 = st.columns(2)

with col3:
    qty = 0
    metres = 0
    ratio = 1.0
    cle_tarif = "Standard"
    
    # --- LOGIQUE CERVEAU TARIFRET ---
    
    # CAS 1 : Palette EURO (80x120) - Base 33/camion
    if unit_type == "Palettes (80x120)":
        qty = st.number_input("Nombre de Palettes (80x120)", 1, 33, 3)
        ratio = qty / 33
        if qty <= 5: 
            power_factor = 0.55 # P60 (Petit lot cher)
            cle_tarif = "P60 (Petit Lot)"
        elif qty <= 15:
            power_factor = 0.75 # P39
            cle_tarif = "P39 (Lot Moyen)"
        else:
            power_factor = 0.90 # P26
            cle_tarif = "P26 (Gros Lot)"

    # CAS 2 : Palette ISO/INDUSTRIE (100x120) - Base 26/camion
    elif unit_type == "Palettes (100x120)":
        qty = st.number_input("Nombre de Palettes (100x120)", 1, 26, 3)
        ratio = qty / 26 # Un complet c'est 26 palettes de ce type
        
        # Les seuils sont ajustés car la palette est plus grosse
        if qty <= 4: # Équivalent ~5 pal Euro
            power_factor = 0.55 
            cle_tarif = "P60 (Petit Lot)"
        elif qty <= 12:
            power_factor = 0.75 
            cle_tarif = "P39 (Lot Moyen)"
        else:
            power_factor = 0.90 
            cle_tarif = "P26 (Gros Lot)"
            
    # CAS 3 : Mètre de plancher
    elif unit_type == "Mètres de plancher":
        metres = st.number_input("Mètres de Plancher", 0.0, 13.6, 2.0)
        ratio = metres / 13.6
        if metres <= 2.0:
            power_factor = 0.55
            cle_tarif = "P60 (Petit Lot)"
        else:
            power_factor = 0.85
            cle_tarif = "Standard"
            
    # CAS 4 : Complet
    else: 
        ratio = 1.0
        power_factor = 1.0
        cle_tarif = "Complet"

with col4:
    st.write("Options & Forfaits")
    opt_hayon = st.checkbox("Hayon (+50€)")
    opt_stop = st.checkbox("Stop Supplémentaire (+50€)")
    opt_adr = st.checkbox("ADR / Dangereux (+20%)")
    opt_frais = st.checkbox("Frais de Dossier (+15€)", value=True)

# --- MOTEUR DE CALCUL ---
full_price = (distance * base_km_sell) + fixed_sell
base_client = full_price * (ratio ** power_factor)

# Sécurité : Pas de prix inférieur à 120€
if base_client < 120: base_client = 120

options = 0
if opt_hayon: options += 50
if opt_stop: options += 50
if opt_frais: options += 15
if opt_adr: 
    adr_val = base_client * 0.20
    if adr_val < 30: adr_val = 30
    options += adr_val

FINAL_SELL = base_client + options
MAX_BUY = FINAL_SELL * (1 - (target_margin/100))

# --- AFFICHAGE DES RÉSULTATS ---
st.divider()
c_res1, c_res2 = st.columns(2)

with c_res1:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    st.markdown("### 💰 PRIX CLIENT")
    st.markdown(f'<p class="client-price">{FINAL_SELL:.0f} € HT</p>', unsafe_allow_html=True)
    st.caption(f"Tarif calculé sur base : {cle_tarif}")
    st.markdown('</div>', unsafe_allow_html=True)

with c_res2:
    st.markdown('<div class="kpi-card" style="border-left: 5px solid #DC2626;">', unsafe_allow_html=True)
    st.markdown("### 🛑 ACHAT MAX")
    st.markdown(f'<p class="buy-limit">{MAX_BUY:.0f} € HT</p>', unsafe_allow_html=True)
    st.caption(f"Budget transporteur pour {target_margin}% de marge")
    st.markdown('</div>', unsafe_allow_html=True)
