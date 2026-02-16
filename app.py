import streamlit as st

# --- CONFIGURATION ---
st.set_page_config(page_title="OPTIVIA MARGIN PROTECTOR", page_icon="🛡️", layout="wide")

# --- CSS PERSONNALISÉ (MOBILE FRIENDLY) ---
st.markdown("""
    <style>
    .client-price { font-size: 32px !important; font-weight: bold; color: #1E3A8A; } 
    .buy-limit { font-size: 32px !important; font-weight: bold; color: #DC2626; } 
    .kpi-card { background-color: #F3F4F6; padding: 15px; border-radius: 10px; border-left: 5px solid #1E3A8A; margin-bottom: 10px;}
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR : PARAMÈTRES CACHÉS ---
with st.sidebar:
    st.header("⚙️ Réglages Tarifret")
    base_km_sell = st.number_input("Vente / Km (€)", value=1.55, step=0.05)
    fixed_sell = st.number_input("Fixe Vente (€)", value=250, step=10)
    st.divider()
    target_margin = st.slider("Marge Visée (%)", 15, 40, 25)

# --- TÊTE DE PAGE ---
st.title("🛡️ OPTIVIA CALCULATOR")
st.caption(f"Objectif Marge : {target_margin}%")

# --- BLOC 1 : LE TRAJET ---
col1, col2 = st.columns(2)
with col1:
    distance = st.number_input("📍 Distance (km)", min_value=1, value=450)
with col2:
    # Logique Tarifret simplifiée
    unit_type = st.radio("Unité", ["Palettes", "Mètres", "Complet"], horizontal=True)

# --- BLOC 2 : QUANTITÉ & OPTIONS ---
col3, col4 = st.columns(2)

with col3:
    qty = 0
    metres = 0
    ratio = 1.0
    cle_tarif = "Standard"
    
    if unit_type == "Palettes":
        qty = st.number_input("Nb Palettes", 1, 33, 3)
        ratio = qty / 33
        if qty <= 5: 
            power_factor = 0.55 # P60
            cle_tarif = "P60 (Fort)"
        elif qty <= 15:
            power_factor = 0.75 # P39
            cle_tarif = "P39 (Moyen)"
        else:
            power_factor = 0.90 # P26
    elif unit_type == "Mètres":
        metres = st.number_input("Mètres Plancher", 0.0, 13.6, 2.0)
        ratio = metres / 13.6
        if metres <= 2.0:
            power_factor = 0.55
            cle_tarif = "P60 (Fort)"
        else:
            power_factor = 0.85
    else: # Complet
        ratio = 1.0
        power_factor = 1.0

with col4:
    opt_hayon = st.checkbox("Hayon (+50€)")
    opt_stop = st.checkbox("Stop Sup (+50€)")
    opt_adr = st.checkbox("ADR (+20%)")
    opt_frais = st.checkbox("Frais Dossier (+15€)", value=True)

# --- CALCULS ---
full_price = (distance * base_km_sell) + fixed_sell
base_client = full_price * (ratio ** power_factor)

# Minimum taxation (Sécurité)
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

# --- RÉSULTATS ---
st.divider()
c_res1, c_res2 = st.columns(2)

with c_res1:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    st.markdown("### 💰 CLIENT")
    st.markdown(f'<p class="client-price">{FINAL_SELL:.0f} €</p>', unsafe_allow_html=True)
    st.caption(f"Clé: {cle_tarif}")
    st.markdown('</div>', unsafe_allow_html=True)

with c_res2:
    st.markdown('<div class="kpi-card" style="border-left: 5px solid #DC2626;">', unsafe_allow_html=True)
    st.markdown("### 🛑 ACHAT MAX")
    st.markdown(f'<p class="buy-limit">{MAX_BUY:.0f} €</p>', unsafe_allow_html=True)
    st.caption(f"Pour garder {target_margin}%")
    st.markdown('</div>', unsafe_allow_html=True)
