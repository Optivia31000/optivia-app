import streamlit as st
import xlsxwriter
import os

# --- 1. CONFIGURATION IDENTITÉ ---
BRAND = "OPTIVIA TRANSPORTS"
DEPTS = {1: "Ain", 2: "Aisne", 3: "Allier", 4: "Alpes-de-Haute-Provence", 5: "Hautes-Alpes", 6: "Alpes-Maritimes", 7: "Ardèche", 8: "Ardennes", 9: "Ariège", 10: "Aube", 11: "Aude", 12: "Aveyron", 13: "Bouches-du-Rhône", 14: "Calvados", 15: "Cantal", 16: "Charente", 17: "Charente-Maritime", 18: "Cher", 19: "Corrèze", 21: "Côte-d'Or", 22: "Côtes-d'Armor", 23: "Creuse", 24: "Dordogne", 25: "Doubs", 26: "Drôme", 27: "Eure", 28: "Eure-et-Loir", 29: "Finistère", 30: "Gard", 31: "Haute-Garonne", 32: "Gers", 33: "Gironde", 34: "Hérault", 35: "Ille-et-Vilaine", 36: "Indre", 37: "Indre-et-Loire", 38: "Isère", 39: "Jura", 40: "Landes", 41: "Loir-et-Cher", 42: "Loire", 43: "Haute-Loire", 44: "Loire-Atlantique", 45: "Loiret", 46: "Lot", 47: "Lot-et-Garonne", 48: "Lozère", 49: "Maine-et-Loire", 50: "Manche", 51: "Marne", 52: "Haute-Marne", 53: "Mayenne", 54: "Meurthe-et-Moselle", 55: "Meuse", 56: "Morbihan", 57: "Moselle", 58: "Nièvre", 59: "Nord", 60: "Oise", 61: "Orne", 62: "Pas-de-Calais", 63: "Puy-de-Dôme", 64: "Pyrénées-Atlantiques", 65: "Hautes-Pyrénées", 66: "Pyrénées-Orientales", 67: "Bas-Rhin", 68: "Haut-Rhin", 69: "Rhône", 70: "Haute-Saône", 71: "Saône-et-Loire", 72: "Sarthe", 73: "Savoie", 74: "Haute-Savoie", 75: "Paris", 76: "Seine-Maritime", 77: "Seine-et-Marne", 78: "Yvelines", 79: "Deux-Sèvres", 80: "Somme", 81: "Tarn", 82: "Tarn-et-Garonne", 83: "Var", 84: "Vaucluse", 85: "Vendée", 86: "Vienne", 87: "Haute-Vienne", 88: "Vosges", 89: "Yonne", 90: "Territoire de Belfort", 91: "Essonne", 92: "Hauts-de-Seine", 93: "Seine-Saint-Denis", 94: "Val-de-Marne", 95: "Val-d'Oise", 98: "Monaco"}

# Catégorisation géographique pour les km d'approche (Base TARIFRET)
DPTS_PETITS = [75, 92, 93, 94, 69, 90]
DPTS_GRANDS = [33, 40, 31, 12, 24, 64, 21, 86, 71, 0] # 0 = sécurité
DPTS_MONTAGNE = [4, 5, 6, 9, 15, 38, 65, 73, 74]

# --- 2. MOTEUR ALGORYTHMIQUE TYPE TARIFRET ---
def run_tarifret(orig, dest, km, gas, unit, qty, opts, p_km, p_fixe, marge):
    if dest == 98: return "Tarif sur demande", "Tarif sur demande"
    
    # 1. Gestion des Kilomètres d'Approche (Le 69 n'est pas le 31)
    km_approche = 15 if orig in DPTS_PETITS else (45 if orig in DPTS_GRANDS else 25)
    km_total = km + km_approche
    
    # 2. Surcharges et Tensions
    idx_gas = ((gas - 1.40) / 1.40) * 0.22
    
    # Tension géographique (Flux sortants des zones denses ou excentrées)
    zone_nord_est = [59, 62, 80, 2, 8, 51, 10, 52, 54, 55, 57, 67, 68, 88, 70, 25, 90, 21]
    tension_orig = 1.15 if orig in zone_nord_est else 1.00
    tension_dest = 1.08 if dest in DPTS_MONTAGNE else 1.00
    
    # 3. Calcul du SOCLE COMPLET (Le FTL Binomial)
    # Formule : (Km totaux * Coût variable) + Coût Fixe journalier équivalent
    prix_complet_base = (km_total * p_km) + p_fixe
    prix_complet_net = prix_complet_base * tension_orig * tension_dest * (1 + idx_gas)
    
    # 4. Dégressivité Partiels (La "Clé")
    coeff_format = {'80x120': 1.0, '100x120': 1.25, '120x120': 1.5, 'Complet': 33.0}
    equiv_pal = qty * coeff_format.get(unit, 1.0)
    
    if unit == 'Complet':
        p_v = prix_complet_net
    else:
        # Puissance de lissage TARIFRET (0.62 approxime la courbe P39/P45)
        # Plus on approche de 33, plus le prix converge vers le FTL
        p_v = prix_complet_net * ((equiv_pal / 33.0) ** 0.62)
    
    # 5. Extraction de la Marge
    coeff_achat = 1 - (marge / 100.0)
    p_a = p_v * coeff_achat
    
    # 6. Options de prestation
    if opts['ADR']: p_v *= 1.25; p_a *= 1.25
    if opts['MTN']: p_v *= 1.20; p_a *= 1.20
    if opts['HYN']: p_v += 50; p_a += 35
    
    return int(round(p_v, 0)), int(round(p_a, 0))

# --- 3. INTERFACE UTILISATEUR ---
st.set_page_config(page_title=BRAND, layout="centered")

col_l1, col_l2 = st.columns([2, 3])
with col_l1:
    if os.path.exists("logo.png"): st.image("logo.png", width=350)
    else: st.write(f"🏷️ **{BRAND}**")
with col_l2:
    st.write(""); st.write(""); st.title(BRAND)

with st.expander("⚙️ Paramétrage du Moteur (Bases)"):
    col_p1, col_p2 = st.columns(2)
    v_km = col_p1.number_input("Cout Variable / Km (€)", value=0.95, step=0.05) # Calibrage FTL
    v_fixe = col_p2.number_input("Frais Fixes / Prestation (€)", value=150)
    cur_gas = col_p1.number_input("Gazole Pompe CNR (€/L)", value=1.75)
    margin_target = col_p2.slider("Marge Nette Visée (%)", 10, 40, 26)

st.subheader("📍 TRAJET")
col1, col2 = st.columns(2)
d_keys = list(DEPTS.keys())
src = col1.selectbox("DÉPART", d_keys, format_func=lambda x: f"{str(x).zfill(2)} - {DEPTS[x]}", index=d_keys.index(31))
dst = col2.selectbox("ARRIVÉE", d_keys, format_func=lambda x: f"{str(x).zfill(2)} - {DEPTS[x]}", index=d_keys.index(75))

st.subheader("👇 DISTANCE RÉELLE EN CHARGE")
dist_auto = 677 if (src == 31 and dst == 75) else (abs(src - (20 if isinstance(dst, str) else dst)) * 8 + 150)
km_real = st.number_input(f"Saisir KM (Est. auto: {dist_auto} km)", value=dist_auto)

st.subheader("📦 MARCHANDISE")
c3, c4 = st.columns(2)
u_type = c3.selectbox("Format d'Unité", ['80x120', '100x120', '120x120', 'Complet'])
u_qty = c4.number_input(f"Quantité", 1, 33, 1)

st.subheader("🔧 SURCHARGES OPÉRATIONNELLES")
o1, o2, o3 = st.columns(3)
opts = {'ADR': o1.checkbox("ADR (+25%)"), 'MTN': o2.checkbox("Montagne (+20%)"), 'HYN': o3.checkbox("Hayon (+50€)")}

p_v, p_a = run_tarifret(src, dst, km_real, cur_gas, u_type, u_qty, opts, v_km, v_fixe, margin_target)

st.divider()
if not isinstance(p_v, str):
    st.header(f"💰 PRIX DE VENTE (CLIENT)")
    st.subheader(f"{p_v} € HT")
    st.caption(f"Stratégie de Marge : {margin_target}% | Base FTL : {km_real} km en charge")
    st.divider()
    st.header(f"🛑 ACHAT MAXIMUM (AFFRÈTEMENT)")
    st.subheader(f"{p_a} € HT")
else:
    st.error(p_v)
