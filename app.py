import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Jérôme Swing Golf Academy",
    page_icon="⛳",
    layout="wide"
)

# =========================
# UI HEADER
# =========================
st.markdown(
    """
    <div style="padding:14px 18px; background:#111; border-radius:10px; margin-bottom:16px;">
      <h1 style="color:#F5F5F5; margin:0;">Jérôme Swing Golf Academy – Training Performance Pro</h1>
      <p style="color:#BDBDBD; margin:6px 0 0;">Dashboard pro – Putting | Wedging | Long Game | Chipping</p>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# HELPERS
# =========================
def indicator_gauge(value, title):
    value = 0 if pd.isna(value) else float(value)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix":" %"},
        title={"text": title},
        gauge={
            "axis":{"range":[0,100]},
            "bar":{"color":"#2E7D32"},
            "steps":[
                {"range":[0,60], "color":"#311B92"},
                {"range":[60,80], "color":"#1B5E20"},
                {"range":[80,100], "color":"#004D40"}
            ],
            "threshold":{"line":{"color":"#FFC107","width":4}, "thickness":0.6, "value":value}
        }
    ))
    fig.update_layout(height=280, margin=dict(l=10,r=10,t=50,b=10))
    return fig

def radar(values, labels, title=""):
    vals = [0 if pd.isna(v) else float(v) for v in values]
    if len(vals) and vals[0] != vals[-1]:
        labels = list(labels) + [labels[0]]
        vals = list(vals) + [vals[0]]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=vals, theta=labels, fill='toself', line_color="#26A69A"))
    fig.update_polars(radialaxis=dict(range=[0,100], gridcolor="#BDBDBD"))
    fig.update_layout(title=title, height=340, margin=dict(l=10,r=10,t=50,b=10))
    return fig

def percent(n, d):
    try:
        n = float(n); d = float(d)
        return round(100*n/d, 1) if d>0 else 0.0
    except:
        return 0.0

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.header("⚙️ Paramètres")
    joueur = st.text_input("Nom du joueur", "Jérôme Bouvachon")
    st.caption("Astuce : change ce nom pour dupliquer l’app par joueur/élève.")

# =========================
# DATA INPUT
# =========================
st.subheader("📥 Données")
st.caption("Charge un fichier Excel (.xlsx) au format de ton modèle (onglets : Putting 1-3-5-7-9m, Wedging 30-50-70m, Long Game 20 clubs, Chipping, Journal). Si aucun fichier n'est chargé, des données démo sont utilisées.")
up = st.file_uploader("Importer vos données Excel", type=["xlsx"])

dfs = {}
if up:
    xls = pd.ExcelFile(up)
    for name in xls.sheet_names:
        try:
            dfs[name] = pd.read_excel(up, sheet_name=name)
        except:
            pass
else:
    # ======= DEMO FALLBACK =======
    dfs["Putting 1-3-5-7-9m"] = pd.DataFrame({
        "Distance (m)":[1,3,5,7,9],
        "Putts tentés":[20,20,20,20,20],
        "Putts réussis":[20,17,12,8,5],
        "Moy. distance raté (cm)":[10,25,40,65,80],
        "Note confiance (1-10)":[10,9,7,6,5]
    })
    dfs["Wedging 30-50-70m"] = pd.DataFrame({
        "Distance cible (m)":[30,50,70],
        "% <3m":[65,55,40],
        "% <5m":[90,85,70],
        "Distance moyenne (m)":[2.5,3.2,4.8]
    })
    dfs["Long Game 20 clubs"] = pd.DataFrame({
        "Club":["Driver","Bois 3","Fer 7","Fer 9","PW","52°","58°"],
        "Distance moyenne (m)":[250,230,145,130,115,100,85],
        "Dispersion (m)":[12,11,9,8,7,6,6],
        "Smash Factor":[1.45,1.43,1.33,1.31,1.30,1.28,1.26],
        "Centrage (%)":[80,78,85,86,87,88,89]
    })
    dfs["Chipping"] = pd.DataFrame({
        "Type de lie":["Fairway","Rough","Bunker","Pente"],
        "% <2m":[75,65,60,50],
        "% <3m":[95,85,80,70],
        "% tops":[0,2,3,3],
        "% grattes":[1,3,4,4]
    })
    dfs["Journal"] = pd.DataFrame({
        "Date":["2025-10-24","2025-10-25","2025-10-26"],
        "Type de séance":["Putting/Wedge","Long Game","Mixte"],
        "Volume total (balles)":[120,160,140],
        "Durée (min)":[90,95,80],
        "Objectif principal":["Contrôle distance","Trajectoires","Routine full"],
        "Performance (1-10)":[8,8.5,8.2]
    })

# =========================
# METRICS COMPUTATION
# =========================
# Putting
putt = dfs.get("Putting 1-3-5-7-9m")
if putt is not None:
    if "Distance (m)" not in putt.columns and "Distance" in putt.columns:
        putt.rename(columns={"Distance":"Distance (m)"}, inplace=True)
    putt["% réussite"] = putt.apply(lambda r: percent(r.get("Putts réussis",0), r.get("Putts tentés",0)), axis=1)
    putting_global = percent(putt["Putts réussis"].sum() if "Putts réussis" in putt else 0,
                             putt["Putts tentés"].sum() if "Putts tentés" in putt else 0)
else:
    putting_global = 0

# Wedging
wed = dfs.get("Wedging 30-50-70m")
if wed is not None:
    wed["% <3m"] = wed.get("% <3m", pd.Series([0]*len(wed)))
    wed["% <5m"] = wed.get("% <5m", pd.Series([0]*len(wed)))
    wedging_global = float(wed["% <3m"].mean()) if len(wed) else 0
else:
    wedging_global = 0

# Long Game
lg = dfs.get("Long Game 20 clubs")
if lg is not None:
    longgame_global = np.interp(np.nanmean(lg.get("Centrage (%)", pd.Series([0]))), [0,100],[0,100])
else:
    longgame_global = 0

# Chipping
chip = dfs.get("Chipping")
if chip is not None:
    chipping_global = float(chip.get("% <2m", pd.Series([0])).mean())
else:
    chipping_global = 0

global_score = round(np.mean([putting_global, wedging_global, longgame_global, chipping_global]),1)

# =========================
# DASHBOARD
# =========================
st.subheader(f"🏷️ Nom du joueur : {joueur}")

c1,c2,c3,c4,c5 = st.columns([1,1,1,1,1])
with c1: st.plotly_chart(indicator_gauge(putting_global, "Putting"), use_container_width=True)
with c2: st.plotly_chart(indicator_gauge(wedging_global, "Wedging"), use_container_width=True)
with c3: st.plotly_chart(indicator_gauge(longgame_global, "Long Game"), use_container_width=True)
with c4: st.plotly_chart(indicator_gauge(chipping_global, "Chipping"), use_container_width=True)
with c5: st.plotly_chart(indicator_gauge(global_score, "Global"), use_container_width=True)

# Radar global
st.markdown("### ⭐ Radar global")
st.plotly_chart(
    radar(
        [putting_global, wedging_global, longgame_global, chipping_global],
        ["Putting","Wedging","Long Game","Chipping"],
        title=f"Profil global – {joueur}"
    ),
    use_container_width=True
)

# =========================
# DETAIL TABS
# =========================
st.markdown("---")
t1,t2,t3,t4,t5 = st.tabs(["🎯 Putting","🟡 Wedging","🔵 Long Game","🟤 Chipping","📒 Journal"])

with t1:
    if putt is not None:
        st.write("Putting – tableau")
        st.dataframe(putt)
        st.write("Putting – % réussite par distance")
        fig = px.bar(putt, x="Distance (m)", y="% réussite", text="% réussite", range_y=[0,100], title="Make rate par distance")
        st.plotly_chart(fig, use_container_width=True)

with t2:
    if wed is not None:
        st.write("Wedging – tableau")
        st.dataframe(wed)
        st.write("Wedging – précision")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=wed["Distance cible (m)"], y=wed["% <3m"], name="% <3m"))
        fig.add_trace(go.Bar(x=wed["Distance cible (m)"], y=wed["% <5m"], name="% <5m"))
        fig.update_layout(barmode='group', yaxis=dict(range=[0,100]), title="Précision par distance")
        st.plotly_chart(fig, use_container_width=True)

with t3:
    if lg is not None:
        st.write("Long Game – tableau")
        st.dataframe(lg)
        st.write("Long Game – distance moyenne par club")
        if "Club" in lg.columns and "Distance moyenne (m)" in lg.columns:
            fig = px.bar(lg, x="Distance moyenne (m)", y="Club", orientation="h", title="Distance moyenne par club")
            st.plotly_chart(fig, use_container_width=True)

with t4:
    if chip is not None:
        st.write("Chipping – tableau")
        st.dataframe(chip)
        st.write("Chipping – réussite par type de lie")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=chip["Type de lie"], y=chip["% <2m"], name="% <2m"))
        fig.add_trace(go.Bar(x=chip["Type de lie"], y=chip["% <3m"], name="% <3m"))
        fig.update_layout(barmode='group', yaxis=dict(range=[0,100]), title="Précision par type de lie")
        st.plotly_chart(fig, use_container_width=True)

with t5:
    if "Journal" in dfs:
        st.write("Journal – historique")
        st.dataframe(dfs["Journal"])
        if "Date" in dfs["Journal"].columns and "Volume total (balles)" in dfs["Journal"].columns:
            j = dfs["Journal"].copy()
            try:
                j["Date"] = pd.to_datetime(j["Date"])
            except:
                pass
            fig = px.bar(j, x="Date", y="Volume total (balles)", title="Volume par séance")
            st.plotly_chart(fig, use_container_width=True)

st.caption("💡 Astuce : duplique cette app par joueur/élève (ou utilise le champ ‘Nom du joueur’) et uploade son Excel pour une vue personnalisée.")
