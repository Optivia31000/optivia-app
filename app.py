import streamlit as st
import xlsxwriter
import os

# --- 1. CONFIGURATION ---
BRAND = "OPTIVIA TRANSPORTS"
DEPTS = {1: "Ain", 2: "Aisne", 3: "Allier", 4: "Alpes-de-Haute-Provence", 5: "Hautes-Alpes", 6: "Alpes-Maritimes", 7: "Ardèche", 8: "Ardennes", 9: "Ariège", 10: "Aube", 11: "Aude", 12: "Aveyron", 13: "Bouches-du-Rhône", 14: "Calvados", 15: "Cantal", 16: "Charente", 17: "Charente-Maritime", 18: "Cher", 19: "Corrèze", 21: "Côte-d'Or", 22: "Côtes-d'Armor", 23: "Creuse", 24: "Dordogne", 25: "Doubs", 26: "Drôme", 27: "Eure", 28: "Eure-et-Loir", 29: "Finistère", 30: "Gard", 31: "Haute-Garonne", 32: "Gers", 33: "Gironde", 34: "Hérault", 35: "Ille-et-Vilaine", 36: "Indre", 37: "Indre-et-Loire", 38: "Isère", 39: "Jura", 40: "Landes", 41: "Loir-et-Cher", 42: "Loire", 43: "Haute-Loire", 44: "Loire-Atlantique", 45: "Loiret", 46: "Lot", 47: "Lot-et-Garonne", 48: "Lozère", 49: "Maine-et-Loire", 50: "Manche", 51: "Marne", 52: "Haute-Marne", 53: "Mayenne", 54: "Meurthe-et-Moselle", 55: "Meuse", 56: "Morbihan", 57: "Moselle", 58: "Nièvre", 59: "Nord", 60: "Oise", 61: "Orne", 62: "Pas-de-Calais", 63: "Puy-de-Dôme", 64: "Pyrénées-Atlantiques", 65: "Hautes-Pyrénées", 66: "Pyrénées-Orientales", 67: "Bas-Rhin", 68: "Haut-Rhin", 69: "Rhône", 70: "Haute-Saône", 71: "Saône-et-Loire", 72: "Sarthe", 73: "Savoie", 74: "Haute-Savoie", 75: "Paris", 76: "Seine-Maritime", 77: "Seine-et-Marne", 78: "Yvelines", 79: "Deux-Sèvres", 80: "Somme", 81: "Tarn", 82: "Tarn-et-Garonne", 83: "Var", 84: "Vaucluse", 85: "Vendée", 86: "Vienne", 87: "Haute-Vienne", 88: "Vosges", 89: "Yonne", 90: "Territoire de Belfort", 91: "Essonne", 92: "Hauts-de-Seine", 93: "Seine-Saint-Denis", 94: "Val-de-Marne", 95: "Val-d'Oise", 98: "Monaco"}

def run_calc(orig, dest, km, gas, unit, qty, opts, p_km, p_fixe):
    if dest == 98: return "Tarif sur demande", "Tarif sur demande"
    coeff = {'80x120': 1.0, '100x120': 1.35, '120x120': 1.6, 'Complet': 8.5}
    f_mult, dist_f = coeff.get(unit, 1.0), (km / 500) ** -0.45
    surcharge = ((gas - 1.40) / 1.40) * 0.22
    nord = [59, 62, 80, 2, 8, 51, 10, 52, 54, 55, 57, 67, 68, 88, 70, 25, 90, 21, 75, 77, 78, 91, 92, 93, 94, 95]
    tension = 1.22 if (orig in nord) else 1.00
    p_v = (((km * p_km * dist_f) + p_fixe) * tension * (1 + surcharge)) * f_mult * (qty ** 0.62)
    p_a = (((km * 0.18 * dist_f) + 31) * tension * (1 + surcharge)) * f_mult * (qty ** 0.62)
    c_opt = 1.0 + (0.25 if opts['ADR'] else 0) + (0.25 if opts['MTN'] else 0)
    res_v, res_a = p_v * c_opt, p_a * c_opt
    if opts['HYN']: res_v += 50; res_a += 35
    return int(round(res_v, 0)), int(round(res_a, 0))

# --- INTERFACE ---
st.set_page_config(page_title=BRAND, layout="centered")

# Gestion du Logo (Recherche large)
logo_files = ["logo_optivia.png", "logo_optivia.PNG", "Logo_optivia.png", "LOGO_OPTIVIA.png"]
logo_path = next((f for f in logo_files if os.path.exists(f)), None)

col_l1, col_l2 = st.columns([1, 2])
with col_l1:
    if logo_path:
        st.image(logo_path, width=200)
    else:
        st.write(f"🏷️ **{BRAND}**")
with col_l2:
    st.title(BRAND)

with st.expander("⚙️ Moteur & Export"):
    v_km = st.number_input("Prix Vente / Km (€)", value=0.29)
    v_fixe = st.number_input("Fixe Vente (€)", value=40)
    cur_gas = st.number_input("Pompe Gazole CNR (€/L)", value=1.75)
    margin_target = st.slider("Marge Visée (%)", 15, 45, 33)

st.subheader("📍 TRAJET")
col1, col2 = st.columns(2)
d_keys = list(DEPTS.keys())
src = col1.selectbox("DÉPART", d_keys, format_func=lambda x: f"{str(x).zfill(2)} - {DEPTS[x]}", index=d_keys.index(31))
dst = col2.selectbox("ARRIVÉE", d_keys, format_func=lambda x: f"{str(x).zfill(2)} - {DEPTS[x]}", index=d_keys.index(75))

st.subheader("👇 DISTANCE RÉELLE")
# Exception 31-75 pour coller à ton ancienne API
dist_auto = 677 if (src == 31 and dst == 75) else (abs(src - (20 if isinstance(dst, str) else dst)) * 8 + 150)
km_real = st.number_input(f"Saisir KM (Est. auto: {dist_auto} km)", value=dist_auto)

st.subheader("📦 MARCHANDISE")
c3, c4 = st.columns(2)
u_type = c3.selectbox("Type", ['80x120', '100x120', '120x120', 'Complet'])
u_qty = c4.number_input(f"Nb Pal ({u_type})", 1, 33, 1)

st.subheader("🔧 OPTIONS")
o1, o2, o3 = st.columns(3)
opts = {'ADR': o1.checkbox("ADR (+25%)"), 'MTN': o2.checkbox("Montagne (+25%)"), 'HYN': o3.checkbox("Hayon (+50€)")}

p_v, p_a = run_calc(src, dst, km_real, cur_gas, u_type, u_qty, opts, v_km, v_fixe)

st.divider()
if not isinstance(p_v, str):
    st.header(f"💰 PRIX CLIENT")
    st.subheader(f"{p_v} € HT")
    st.caption(f"Clé: P{margin_target} | {km_real} km")
    st.divider()
    st.header(f"🛑 ACHAT MAX")
    st.subheader(f"{p_a} € HT")
else:
    st.error(p_v)
