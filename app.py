import json
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(page_title="StartSe | Custos B2C", layout="wide",
                   initial_sidebar_state="collapsed")

# Paleta StartSe — preto, branco e azul marinho
LARANJA   = "#13315C"   # azul marinho — REALIZADO (cor principal)
LARANJA_2 = "#2F6FB3"   # azul vivo (destaque)
INK       = "#0B0B0C"   # preto
AZUL      = "#9AA3AD"   # cinza — ORÇADO (referência/sombra)
AZUL_2    = "#5B6B7B"
VERDE     = "#13315C"   # favorável (abaixo do orçado) → azul marinho
VERMELHO  = "#0B0B0C"   # desfavorável (acima do orçado) → preto
NEUTRO    = "#9AA3AD"
BG        = "#F6F7F9"
CARD      = "#FFFFFF"
BORDA     = "#E6E8EC"
MUTED     = "#5B636E"

LINHAS = ["Custos Variáveis", "Custos de Venda", "Marketing Direto", "Custos Fixos"]
# rampa monocromática azul marinho (claro → escuro)
COR_LINHA = {"Custos Variáveis": "#2F6FB3", "Custos de Venda": "#1E5288",
             "Marketing Direto": "#13315C", "Custos Fixos": "#0A2540"}
SEG_ORDER = ["Eventos", "Produtos Offline", "Produtos Online", "Imersões Internacionais"]
MESES = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
         7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}

# ----------------------------------------------------------------------------
# CSS — remove o visual padrão do Streamlit e aplica a identidade StartSe
# ----------------------------------------------------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

#MainMenu, footer, header {{visibility: hidden;}}
.stDeployButton {{display:none;}}
.block-container {{padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1280px;}}
html, body, [class*="css"] {{font-family: 'Inter', sans-serif; color: {INK};}}
.stApp {{background: {BG};}}

/* faixa de topo */
.topbar {{display:flex; align-items:center; gap:14px; padding: 6px 0 18px 0;
          border-bottom: 1px solid {BORDA}; margin-bottom: 22px;}}
.logo-dot {{width:13px; height:13px; border-radius:3px; background:{LARANJA};
            box-shadow: 16px 0 0 {INK};}}
.brand {{font-family:'Space Grotesk'; font-weight:700; letter-spacing:.5px;
         font-size:15px; color:{INK};}}
.brand b {{color:{LARANJA};}}
.subbrand {{font-size:12.5px; color:{MUTED}; margin-left:auto; font-weight:500;}}

/* cards / kpis */
.kpi {{background:{CARD}; border:1px solid {BORDA}; border-radius:14px;
       padding:16px 18px; height:100%;}}
.kpi .lab {{font-size:11.5px; text-transform:uppercase; letter-spacing:.8px;
            color:{MUTED}; font-weight:600;}}
.kpi .val {{font-family:'Space Grotesk'; font-size:27px; font-weight:700;
            color:{INK}; margin-top:6px; line-height:1;}}
.kpi .sub {{font-size:12.5px; margin-top:8px; font-weight:600;}}
.up {{color:{VERMELHO};}} .down {{color:{VERDE};}}
.accent {{border-top:3px solid {LARANJA};}}

.section {{font-family:'Space Grotesk'; font-weight:700; font-size:16px;
           color:{INK}; margin:8px 0 2px 0;}}
.hint {{font-size:12.5px; color:{MUTED}; margin-bottom:10px;}}

/* tabs sem chrome padrão */
.stTabs [data-baseweb="tab-list"] {{gap:4px; border-bottom:1px solid {BORDA};}}
.stTabs [data-baseweb="tab"] {{height:42px; padding:0 18px; background:transparent;
       border:none; font-weight:600; font-size:13.5px; color:{MUTED};}}
.stTabs [aria-selected="true"] {{color:{INK}; border-bottom:2.5px solid {LARANJA};}}

/* chips de classificação */
.chip {{display:inline-block; padding:3px 10px; border-radius:20px; font-size:11.5px;
        font-weight:600;}}
.chip-v {{background:#E8EEF6; color:{VERDE};}}
.chip-r {{background:#ECEDEF; color:{VERMELHO};}}
.chip-n {{background:#F1F2F4; color:{MUTED};}}
.chip-o {{background:#E8EEF6; color:{LARANJA};}}

[data-testid="stMetricValue"] {{font-family:'Space Grotesk';}}
div[data-baseweb="select"] > div {{border-radius:10px; border-color:{BORDA};}}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# DADOS
# ----------------------------------------------------------------------------
@st.cache_data
def load():
    df = pd.DataFrame(json.load(open("dados.json", encoding="utf-8")))
    return df

df = load()
B2C_SEGS = ["Eventos", "Produtos Offline", "Produtos Online", "Imersões Internacionais"]
b = df[df["segmento"].isin(B2C_SEGS)].copy()

def brl(v, curto=True):
    s = "-" if v < 0 else ""
    v = abs(v)
    if curto:
        if v >= 1e6:  return f"{s}R$ {v/1e6:.1f} M"
        if v >= 1e3:  return f"{s}R$ {v/1e3:.0f} mil"
        return f"{s}R$ {v:.0f}"
    return f"{s}R$ {v:,.0f}".replace(",", ".")

def plot_layout(fig, h=360, legend_top=True):
    fig.update_layout(
        template="plotly_white", height=h,
        margin=dict(l=10, r=10, t=30, b=10),
        font=dict(family="Inter, sans-serif", size=12.5, color=INK),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=1.12 if legend_top else -0.18, x=0,
                    bgcolor="rgba(0,0,0,0)", font=dict(size=11.5)),
        hoverlabel=dict(bgcolor=INK, font_size=12, font_family="Inter"),
    )
    fig.update_xaxes(showgrid=False, linecolor=BORDA, ticks="outside",
                     tickcolor=BORDA)
    fig.update_yaxes(gridcolor="#EEF0F2", zeroline=True, zerolinecolor=BORDA)
    return fig

# YTD helpers (meses 1-5 = realizado disponível)
ytd = b[b["tem_real"]]
def ytd_sum(col, frame=ytd):
    return float(frame[col].sum())

# ----------------------------------------------------------------------------
# TOPBAR
# ----------------------------------------------------------------------------
st.markdown(f"""
<div class="topbar">
  <div class="logo-dot"></div>
  <div style="margin-left:22px;">
    <div class="brand">START<b>SE</b> · FP&A</div>
  </div>
  <div class="subbrand">Custos &amp; Despesas B2C · Realizado vs Orçado · Jan–Mai 2026</div>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["Panorama", "Segmentos", "Turmas", "Padrão e Desvio",
                "Vendas x Custos", "Forecast H2"])

# ============================================================================
# TAB 1 — PANORAMA
# ============================================================================
with tabs[0]:
    real_tot = ytd_sum("real_Custos Totais")
    orc_tot  = ytd_sum("orc_Custos Totais")
    desv     = real_tot - orc_tot
    desv_pct = desv / orc_tot * 100 if orc_tot else 0
    rec_real = ytd_sum("real_Receita Bruta")
    repr_real = real_tot / rec_real * 100 if rec_real else 0

    c = st.columns(4)
    kpis = [
        ("Custo realizado (YTD)", brl(real_tot), f"Orçado {brl(orc_tot)}", "", True),
        ("Desvio vs orçado", brl(desv), f"{desv_pct:+.1f}% vs orçado",
         "down" if desv <= 0 else "up", False),
        ("Custo / Receita", f"{repr_real:.1f}%", f"sobre {brl(rec_real)} de receita", "", False),
        ("Produtos B2C", f"{b['produto'].nunique()}",
         f"em {len(B2C_SEGS)} segmentos", "", False),
    ]
    for col, (lab, val, sub, cls, acc) in zip(c, kpis):
        col.markdown(f"""<div class="kpi {'accent' if acc else ''}">
            <div class="lab">{lab}</div><div class="val">{val}</div>
            <div class="sub {cls}">{sub}</div></div>""", unsafe_allow_html=True)

    st.write("")
    left, right = st.columns([1.35, 1])

    with left:
        st.markdown('<div class="section">Realizado vs orçado por segmento</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="hint">Custo total acumulado Jan–Mai por segmento B2C</div>',
                    unsafe_allow_html=True)
        g = ytd.groupby("segmento")[["real_Custos Totais", "orc_Custos Totais"]].sum()
        g = g.reindex([s for s in SEG_ORDER if s in g.index])
        fig = go.Figure()
        fig.add_bar(y=g.index, x=g["orc_Custos Totais"], name="Orçado",
                    orientation="h", marker_color=AZUL, opacity=.35,
                    hovertemplate="Orçado: %{x:,.0f}<extra></extra>")
        fig.add_bar(y=g.index, x=g["real_Custos Totais"], name="Realizado",
                    orientation="h", marker_color=LARANJA,
                    hovertemplate="Realizado: %{x:,.0f}<extra></extra>")
        fig.update_layout(barmode="overlay")
        fig.update_traces(width=.55, selector=dict(name="Realizado"))
        fig.update_traces(width=.78, selector=dict(name="Orçado"))
        plot_layout(fig, 320)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown('<div class="section">Composição do custo realizado</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="hint">Participação de cada linha no custo B2C (YTD)</div>',
                    unsafe_allow_html=True)
        comp = {l: ytd_sum(f"real_{l}") for l in LINHAS}
        fig = go.Figure(go.Pie(
            labels=list(comp.keys()), values=list(comp.values()), hole=.62,
            marker=dict(colors=[COR_LINHA[l] for l in comp], line=dict(color=CARD, width=2)),
            textinfo="percent", textfont=dict(size=12, color="white"),
            hovertemplate="%{label}: %{value:,.0f}<extra></extra>", sort=False))
        fig.add_annotation(text=f"<b>{brl(sum(comp.values()))}</b>", x=.5, y=.5,
                           font=dict(size=16, family="Space Grotesk"), showarrow=False)
        plot_layout(fig, 320)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section">Trajetória mensal — realizado vs orçado</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="hint">O custo B2C é sazonal: concentra-se nos meses de '
                'eventos e imersões, não é constante</div>', unsafe_allow_html=True)
    m = ytd.groupby("mes")[["real_Custos Totais", "orc_Custos Totais"]].sum().reindex(range(1, 6))
    fig = go.Figure()
    fig.add_bar(x=[MESES[i] for i in m.index], y=m["orc_Custos Totais"], name="Orçado",
                marker_color=AZUL, opacity=.30, hovertemplate="Orçado: %{y:,.0f}<extra></extra>")
    fig.add_scatter(x=[MESES[i] for i in m.index], y=m["real_Custos Totais"], name="Realizado",
                    mode="lines+markers", line=dict(color=LARANJA, width=3),
                    marker=dict(size=9), hovertemplate="Realizado: %{y:,.0f}<extra></extra>")
    plot_layout(fig, 330)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TAB 2 — SEGMENTOS
# ============================================================================
with tabs[1]:
    seg = st.selectbox("Segmento", B2C_SEGS, label_visibility="collapsed")
    sd = ytd[ytd["segmento"] == seg]
    rt, ot = sd["real_Custos Totais"].sum(), sd["orc_Custos Totais"].sum()
    rb = sd["real_Receita Bruta"].sum()
    dv = (rt - ot) / ot * 100 if ot else 0

    c = st.columns(4)
    info = [("Custo realizado", brl(rt), ""),
            ("Orçado", brl(ot), ""),
            ("Desvio", f"{dv:+.1f}%", "down" if dv <= 0 else "up"),
            ("Receita realizada", brl(rb), "")]
    for col, (l, v, cls) in zip(c, info):
        col.markdown(f"""<div class="kpi"><div class="lab">{l}</div>
            <div class="val {cls}">{v}</div><div class="sub">&nbsp;</div></div>""",
            unsafe_allow_html=True)
    st.write("")

    left, right = st.columns(2)
    with left:
        st.markdown('<div class="section">Custo mensal por linha — realizado</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="hint">Empilhado por natureza de custo</div>', unsafe_allow_html=True)
        mm = sd.groupby("mes")[[f"real_{l}" for l in LINHAS]].sum().reindex(range(1, 6)).fillna(0)
        fig = go.Figure()
        for l in LINHAS:
            fig.add_bar(x=[MESES[i] for i in mm.index], y=mm[f"real_{l}"], name=l,
                        marker_color=COR_LINHA[l],
                        hovertemplate=l + ": %{y:,.0f}<extra></extra>")
        fig.update_layout(barmode="stack")
        plot_layout(fig, 350)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown('<div class="section">Realizado vs orçado por linha</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="hint">Acumulado YTD</div>', unsafe_allow_html=True)
        rr = [sd[f"real_{l}"].sum() for l in LINHAS]
        oo = [sd[f"orc_{l}"].sum() for l in LINHAS]
        fig = go.Figure()
        fig.add_bar(x=LINHAS, y=oo, name="Orçado", marker_color=AZUL, opacity=.30)
        fig.add_bar(x=LINHAS, y=rr, name="Realizado", marker_color=LARANJA)
        fig.update_layout(barmode="group")
        plot_layout(fig, 350)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section">Produtos do segmento</div>', unsafe_allow_html=True)
    pv = sd.groupby("produto").agg(
        real=("real_Custos Totais", "sum"), orc=("orc_Custos Totais", "sum"),
        rec=("real_Receita Bruta", "sum")).reset_index()
    pv["desvio_%"] = (pv["real"] - pv["orc"]) / pv["orc"].replace(0, pd.NA) * 100
    pv = pv.sort_values("real", ascending=False)
    show = pv.copy()
    show["Realizado"] = show["real"].map(lambda x: brl(x))
    show["Orçado"] = show["orc"].map(lambda x: brl(x))
    show["Receita"] = show["rec"].map(lambda x: brl(x))
    show["Desvio"] = show["desvio_%"].map(lambda x: "—" if pd.isna(x) else f"{x:+.0f}%")
    st.dataframe(show[["produto", "Realizado", "Orçado", "Desvio", "Receita"]]
                 .rename(columns={"produto": "Produto / Turma"}),
                 hide_index=True, use_container_width=True)

# ============================================================================
# TAB 3 — TURMAS (granular por produto)
# ============================================================================
with tabs[2]:
    prods = sorted(b["produto"].unique())
    prod = st.selectbox("Produto / Turma", prods, label_visibility="collapsed")
    pd_ = b[b["produto"] == prod]
    pr5 = pd_[pd_["tem_real"]]
    rt, ot = pr5["real_Custos Totais"].sum(), pr5["orc_Custos Totais"].sum()
    rec = pr5["real_Receita Bruta"].sum()
    turmas = pd_[pd_["tem_real"]]["orc_Qtd Turmas"].sum()
    seg = pd_["segmento"].iloc[0]
    dv = (rt - ot) / ot * 100 if ot else None
    cpt = rt / turmas if turmas else 0

    c = st.columns(5)
    cards = [("Segmento", seg, ""),
             ("Custo realizado", brl(rt), ""),
             ("Desvio vs orçado", ("—" if dv is None else f"{dv:+.0f}%"),
              "" if dv is None else ("down" if dv <= 0 else "up")),
             ("Turmas (orç.)", f"{turmas:.0f}", ""),
             ("Custo / turma", brl(cpt) if turmas else "—", "")]
    for col, (l, v, cls) in zip(c, cards):
        col.markdown(f"""<div class="kpi"><div class="lab">{l}</div>
            <div class="val {cls}" style="font-size:21px;">{v}</div>
            <div class="sub">&nbsp;</div></div>""", unsafe_allow_html=True)
    st.write("")

    left, right = st.columns([1.3, 1])
    with left:
        st.markdown('<div class="section">Custo por mês — realizado vs orçado</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="hint">Barras = orçado · linha = realizado (Jan–Mai)</div>',
                    unsafe_allow_html=True)
        mm = pr5.groupby("mes")[["real_Custos Totais", "orc_Custos Totais"]].sum().reindex(range(1, 6)).fillna(0)
        fig = go.Figure()
        fig.add_bar(x=[MESES[i] for i in mm.index], y=mm["orc_Custos Totais"], name="Orçado",
                    marker_color=AZUL, opacity=.30)
        fig.add_scatter(x=[MESES[i] for i in mm.index], y=mm["real_Custos Totais"], name="Realizado",
                        mode="lines+markers", line=dict(color=LARANJA, width=3), marker=dict(size=9))
        plot_layout(fig, 340)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown('<div class="section">Linhas de custo (YTD)</div>', unsafe_allow_html=True)
        st.markdown('<div class="hint">Realizado vs orçado por natureza</div>', unsafe_allow_html=True)
        rr = [pr5[f"real_{l}"].sum() for l in LINHAS]
        oo = [pr5[f"orc_{l}"].sum() for l in LINHAS]
        fig = go.Figure()
        fig.add_bar(y=LINHAS, x=oo, name="Orçado", orientation="h", marker_color=AZUL, opacity=.30)
        fig.add_bar(y=LINHAS, x=rr, name="Realizado", orientation="h", marker_color=LARANJA)
        fig.update_layout(barmode="group")
        plot_layout(fig, 340)
        st.plotly_chart(fig, use_container_width=True)

    # tabela mensal detalhada
    st.markdown('<div class="section">Detalhe mensal por linha de custo</div>', unsafe_allow_html=True)
    rows = []
    for _, r in pr5.sort_values("mes").iterrows():
        rows.append({"Mês": MESES[r["mes"]],
                     **{l: brl(r[f"real_{l}"]) for l in LINHAS},
                     "Total real": brl(r["real_Custos Totais"]),
                     "Total orç.": brl(r["orc_Custos Totais"])})
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

# ============================================================================
# TAB 4 — PADRÃO E DESVIO
# ============================================================================
with tabs[3]:
    st.markdown('<div class="section">Mapa de desvio · produto × mês</div>', unsafe_allow_html=True)
    st.markdown('<div class="hint">Azul marinho = realizado abaixo do orçado · Preto = acima · '
                'Cinza = sem orçamento no mês</div>', unsafe_allow_html=True)

    piv_r = ytd.pivot_table(index="produto", columns="mes", values="real_Custos Totais", aggfunc="sum")
    piv_o = ytd.pivot_table(index="produto", columns="mes", values="orc_Custos Totais", aggfunc="sum")
    piv_r = piv_r.reindex(columns=range(1, 6)); piv_o = piv_o.reindex(columns=range(1, 6))
    dev = (piv_r - piv_o) / piv_o.replace(0, pd.NA) * 100
    order = (piv_r.sum(axis=1)).sort_values(ascending=False).index
    dev = dev.reindex(order)
    z = dev.clip(-100, 100).values
    txt = [[("—" if pd.isna(v) else f"{v:+.0f}%") for v in row] for row in dev.values]
    fig = go.Figure(go.Heatmap(
        z=z, x=[MESES[i] for i in range(1, 6)], y=list(dev.index),
        text=txt, texttemplate="%{text}", textfont=dict(size=10.5),
        colorscale=[[0, "#13315C"], [.5, "#EEF1F4"], [1, "#0B0B0C"]], zmid=0,
        zmin=-100, zmax=100, showscale=False,
        hovertemplate="%{y} · %{x}: %{text}<extra></extra>", xgap=3, ygap=3))
    plot_layout(fig, max(330, 26 * len(dev)))
    st.plotly_chart(fig, use_container_width=True)

    st.write("")
    # ranking de desvio (largura total)
    st.markdown('<div class="section">Ranking de desvio (YTD)</div>', unsafe_allow_html=True)
    st.markdown('<div class="hint">Diferença % do custo realizado vs orçado · '
                'negativo = economia · só produtos orçados</div>', unsafe_allow_html=True)
    rk = ytd.groupby("produto").agg(r=("real_Custos Totais", "sum"),
                                    o=("orc_Custos Totais", "sum")).reset_index()
    rk = rk[rk["o"] > 0]
    rk["d"] = (rk["r"] - rk["o"]) / rk["o"] * 100
    rk = rk.sort_values("d")
    fig = go.Figure(go.Bar(
        x=rk["d"], y=rk["produto"], orientation="h",
        marker_color=[VERDE if v <= 0 else VERMELHO for v in rk["d"]],
        text=[f"{v:+.0f}%" for v in rk["d"]], textposition="outside",
        textfont=dict(size=10), hovertemplate="%{y}: %{x:+.0f}%<extra></extra>"))
    fig.add_vline(x=0, line_color=INK, line_width=1)
    plot_layout(fig, max(360, 26 * len(rk)))
    fig.update_xaxes(title="desvio % (negativo = economia)")
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TAB 5 — VENDAS x CUSTOS  (custo caiu por vender menos ou por eficiência?)
# ============================================================================
with tabs[4]:
    # agregados YTD (Jan-Mai)
    R_real = ytd_sum("real_Receita Bruta")
    C_real = ytd_sum("real_Custos Totais")
    R_orc  = ytd_sum("orc_Receita Bruta")
    C_orc  = ytd_sum("orc_Custos Totais")
    r_real = C_real / R_real if R_real else 0     # custo / receita realizado
    r_orc  = C_orc / R_orc if R_orc else 0        # custo / receita orçado

    # decomposição do desvio de custo: volume (vendas) vs eficiência (intensidade)
    ef_volume     = (R_real - R_orc) * r_orc          # custo explicado por vender +/- que o plano
    ef_eficiencia = R_real * (r_real - r_orc)         # custo explicado por gastar +/- por R$ vendido
    delta_custo   = C_real - C_orc                    # = ef_volume + ef_eficiencia

    # veredito dinâmico
    if abs(ef_eficiencia) >= abs(ef_volume):
        domina = "eficiência operacional" if ef_eficiencia < 0 else "pressão de custo"
        verdito = f"Predomina {domina}"
    else:
        domina = "menor volume de vendas" if (R_real - R_orc) < 0 else "maior volume de vendas"
        verdito = f"Predomina {domina}"

    st.markdown('<div class="hint">A receita e o custo caíram juntos (menos vendas) ou o '
                'custo por real vendido melhorou (eficiência)? A decomposição abaixo separa os '
                'dois efeitos.</div>', unsafe_allow_html=True)

    c = st.columns(4)
    kpis = [
        ("Receita realizada (YTD)", brl(R_real),
         f"Orçado {brl(R_orc)} · {(R_real-R_orc)/R_orc*100:+.0f}%" if R_orc else "", "", True),
        ("Custo realizado (YTD)", brl(C_real),
         f"Orçado {brl(C_orc)} · {(C_real-C_orc)/C_orc*100:+.0f}%" if C_orc else "", "", False),
        ("Custo / Receita", f"{r_real*100:.1f}%",
         f"Orçado {r_orc*100:.1f}% · {(r_real-r_orc)*100:+.1f} p.p.",
         "down" if r_real <= r_orc else "up", False),
        ("Leitura", verdito,
         f"Eficiência {brl(ef_eficiencia)} · Volume {brl(ef_volume)}",
         "down" if ef_eficiencia <= 0 else "up", False),
    ]
    for col, (lab, val, sub, cls, acc) in zip(c, kpis):
        col.markdown(f"""<div class="kpi {'accent' if acc else ''}">
            <div class="lab">{lab}</div><div class="val" style="font-size:21px;">{val}</div>
            <div class="sub {cls}">{sub}</div></div>""", unsafe_allow_html=True)

    st.write("")
    left, right = st.columns([1.25, 1])

    # ---- trajetória mensal: receita x custo x intensidade
    with left:
        st.markdown('<div class="section">Receita e custo mês a mês</div>', unsafe_allow_html=True)
        st.markdown('<div class="hint">Barras = realizado · linha = custo por R$ de receita (%). '
                    'Se a linha sobe, o custo cresce mais que a venda</div>', unsafe_allow_html=True)
        m = ytd.groupby("mes")[["real_Receita Bruta", "real_Custos Totais"]].sum().reindex(range(1, 6))
        ratio = [(ct / rb * 100 if rb else None)
                 for rb, ct in zip(m["real_Receita Bruta"], m["real_Custos Totais"])]
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_bar(x=[MESES[i] for i in m.index], y=m["real_Receita Bruta"], name="Receita",
                    marker_color=AZUL, opacity=.45,
                    hovertemplate="Receita: %{y:,.0f}<extra></extra>", secondary_y=False)
        fig.add_bar(x=[MESES[i] for i in m.index], y=m["real_Custos Totais"], name="Custo",
                    marker_color=LARANJA, hovertemplate="Custo: %{y:,.0f}<extra></extra>",
                    secondary_y=False)
        fig.add_scatter(x=[MESES[i] for i in m.index], y=ratio, name="Custo / Receita",
                        mode="lines+markers", line=dict(color=INK, width=2.5, dash="dot"),
                        marker=dict(size=7), connectgaps=True,
                        hovertemplate="Custo/Receita: %{y:.0f}%<extra></extra>", secondary_y=True)
        fig.update_layout(barmode="group")
        plot_layout(fig, 360)
        fig.update_yaxes(title_text="R$", secondary_y=False)
        fig.update_yaxes(title_text="custo / receita %", secondary_y=True,
                         showgrid=False, rangemode="tozero")
        st.plotly_chart(fig, use_container_width=True)

    # ---- waterfall: do orçado ao realizado
    with right:
        st.markdown('<div class="section">Por que o custo mudou</div>', unsafe_allow_html=True)
        st.markdown('<div class="hint">Do custo orçado ao realizado, separando o efeito de '
                    'vendas (volume) do efeito de eficiência</div>', unsafe_allow_html=True)
        fig = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute", "relative", "relative", "total"],
            x=["Custo<br>orçado", "Efeito<br>vendas", "Efeito<br>eficiência", "Custo<br>realizado"],
            y=[C_orc, ef_volume, ef_eficiencia, C_real],
            text=[brl(C_orc), brl(ef_volume), brl(ef_eficiencia), brl(C_real)],
            textposition="outside", textfont=dict(size=10.5),
            connector=dict(line=dict(color=BORDA)),
            increasing=dict(marker=dict(color=VERMELHO)),
            decreasing=dict(marker=dict(color=VERDE)),
            totals=dict(marker=dict(color=LARANJA))))
        plot_layout(fig, 360, legend_top=False)
        fig.update_yaxes(rangemode="tozero")
        st.plotly_chart(fig, use_container_width=True)

    # ---- por produto: custo/receita realizado vs orçado
    st.markdown('<div class="section">Custo por real de receita · por produto</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="hint">Barra azul (realizado) à esquerda da cinza (orçado) = ganho de '
                'eficiência · à direita = custo mais pesado que o planejado · '
                'só produtos com receita realizada e orçada</div>', unsafe_allow_html=True)
    g = ytd.groupby("produto").agg(
        rr=("real_Receita Bruta", "sum"), cr=("real_Custos Totais", "sum"),
        ro=("orc_Receita Bruta", "sum"), co=("orc_Custos Totais", "sum")).reset_index()
    g = g[(g["rr"] > 0) & (g["ro"] > 0)].copy()
    g["int_real"] = g["cr"] / g["rr"] * 100
    g["int_orc"]  = g["co"] / g["ro"] * 100
    g = g.sort_values("int_real", ascending=True)
    fig = go.Figure()
    fig.add_bar(y=g["produto"], x=g["int_orc"], name="Orçado", orientation="h",
                marker_color=AZUL, opacity=.40,
                hovertemplate="%{y} · orçado: %{x:.0f}%<extra></extra>")
    fig.add_bar(y=g["produto"], x=g["int_real"], name="Realizado", orientation="h",
                marker_color=LARANJA,
                hovertemplate="%{y} · realizado: %{x:.0f}%<extra></extra>")
    fig.update_layout(barmode="overlay")
    fig.update_traces(width=.55, selector=dict(name="Realizado"))
    fig.update_traces(width=.80, selector=dict(name="Orçado"))
    plot_layout(fig, max(380, 26 * len(g)))
    fig.update_xaxes(title="custo / receita (%)")
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TAB 6 — FORECAST H2
# ============================================================================
with tabs[5]:
    st.markdown('<div class="section">Leitura para o forecast do 2º semestre</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="hint">Compara o run-rate realizado (Jan–Mai) com o orçado e projeta '
                'o orçamento de Jun–Dez mantido vs ajustado pelo desempenho observado</div>',
                unsafe_allow_html=True)

    rows = []
    for p in sorted(b["produto"].unique()):
        seg = b[b["produto"] == p]["segmento"].iloc[0]
        h1 = b[(b["produto"] == p) & (b["tem_real"])]
        h2 = b[(b["produto"] == p) & (~b["tem_real"])]
        r = h1["real_Custos Totais"].sum()
        o1 = h1["orc_Custos Totais"].sum()
        o2 = h2["orc_Custos Totais"].sum()
        if o1 <= 0 and o2 <= 0 and r <= 0:
            continue
        ratio = r / o1 if o1 > 0 else None      # fator de realização H1
        h2_aj = o2 * ratio if (ratio is not None and o2 > 0) else o2
        rows.append({"produto": p, "seg": seg, "r": r, "o1": o1, "o2": o2,
                     "ratio": ratio, "h2_aj": h2_aj})
    fc = pd.DataFrame(rows)

    o2_tot = fc["o2"].sum()
    aj_tot = fc["h2_aj"].sum()
    delta = aj_tot - o2_tot

    c = st.columns(3)
    c[0].markdown(f"""<div class="kpi accent"><div class="lab">Orçado H2 (Jun–Dez)</div>
        <div class="val">{brl(o2_tot)}</div><div class="sub">custo B2C orçado</div></div>""",
        unsafe_allow_html=True)
    c[1].markdown(f"""<div class="kpi"><div class="lab">Forecast H2 ajustado</div>
        <div class="val">{brl(aj_tot)}</div>
        <div class="sub">pelo run-rate de Jan–Mai</div></div>""", unsafe_allow_html=True)
    cls = "down" if delta <= 0 else "up"
    c[2].markdown(f"""<div class="kpi"><div class="lab">Revisão sugerida</div>
        <div class="val {cls}">{brl(delta)}</div>
        <div class="sub {cls}">{delta/o2_tot*100:+.1f}% vs orçado H2</div></div>""",
        unsafe_allow_html=True)
    st.write("")

    st.markdown('<div class="section">Orçado H2 vs forecast ajustado · por produto</div>',
                unsafe_allow_html=True)
    fco = fc[fc["o2"] > 0].sort_values("o2", ascending=True)
    fig = go.Figure()
    fig.add_bar(y=fco["produto"], x=fco["o2"], name="Orçado H2", orientation="h",
                marker_color=AZUL, opacity=.32)
    fig.add_bar(y=fco["produto"], x=fco["h2_aj"], name="Forecast ajustado", orientation="h",
                marker_color=LARANJA)
    fig.update_layout(barmode="overlay")
    fig.update_traces(width=.5, selector=dict(name="Forecast ajustado"))
    fig.update_traces(width=.78, selector=dict(name="Orçado H2"))
    plot_layout(fig, max(360, 26 * len(fco)))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section">Recomendação por produto</div>', unsafe_allow_html=True)
    def tag(ratio):
        if ratio is None: return '<span class="chip chip-n">sem base orçada</span>'
        if ratio < 0.85:  return '<span class="chip chip-v">reduzir forecast</span>'
        if ratio > 1.15:  return '<span class="chip chip-r">elevar forecast</span>'
        return '<span class="chip chip-o">manter orçado</span>'
    tb = []
    for _, r in fc.sort_values("o2", ascending=False).iterrows():
        tb.append({
            "Produto / Turma": r["produto"], "Segmento": r["seg"],
            "Real H1": brl(r["r"]), "Orç. H1": brl(r["o1"]),
            "Realização": ("—" if r["ratio"] is None else f"{r['ratio']*100:.0f}%"),
            "Orç. H2": brl(r["o2"]), "Forecast aj.": brl(r["h2_aj"]),
            "_tag": tag(r["ratio"])})
    tdf = pd.DataFrame(tb)
    # render como HTML para mostrar os chips
    html = "<table style='width:100%; border-collapse:collapse; font-size:12.5px;'>"
    html += "<tr style='text-align:left; color:%s; border-bottom:1px solid %s;'>" % (MUTED, BORDA)
    for h in ["Produto / Turma", "Segmento", "Real H1", "Orç. H1", "Realização",
              "Orç. H2", "Forecast aj.", "Sinal"]:
        html += f"<th style='padding:7px 8px; font-weight:600;'>{h}</th>"
    html += "</tr>"
    for row in tb:
        html += "<tr style='border-bottom:1px solid #EEF0F2;'>"
        for k in ["Produto / Turma", "Segmento", "Real H1", "Orç. H1", "Realização",
                  "Orç. H2", "Forecast aj."]:
            html += f"<td style='padding:7px 8px;'>{row[k]}</td>"
        html += f"<td style='padding:7px 8px;'>{row['_tag']}</td></tr>"
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)

# rodapé discreto
st.markdown(f"""<div style="margin-top:34px; padding-top:14px; border-top:1px solid {BORDA};
    font-size:11.5px; color:{MUTED};">Números reproduzidos célula a célula da aba
    <b>P&amp;L por Produto</b> (mesmas fórmulas: SUMIFS na Base de Pagamentos + linhas rateadas
    de Comissão, Taxa de Cartão e Envio de Remessas sobre a Receita Bruta; orçado da
    Receitas e Custos Orç). Cada valor mensal é idêntico ao da planilha. O YTD aqui é a
    soma dos meses Jan–Mai — inclui Maio na linha Taxa de Cartão de Crédito, que a célula
    de YTD da planilha (SOMA C:F) deixa de fora.</div>""",
    unsafe_allow_html=True)
