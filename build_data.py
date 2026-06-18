#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reconstrói os números EXATAMENTE como a aba 'P&L por Produto':
- Real (Jan-Mai): SUMIFS na Base de Pagamentos (case-insensitive, como o Excel)
  keyed pelo NOME REAL do produto (B6), + linhas rateadas (comissão, taxa de
  cartão, envio de remessas) = taxa(Rateio de Custos) x Receita Bruta.
- Orçado (Jan-Dez): direto da 'Receitas e Custos Orç' (colunas de grupo),
  keyed pelo NOME ORÇADO (De para Produtos col D).
"""
import json, openpyxl
from collections import defaultdict

F = "/mnt/user-data/uploads/_17_06_2026___FP_A__Resultado_StartSe_maio26_-_EBITDA_por_produto1.xlsx"
wb = openpyxl.load_workbook(F, data_only=True, read_only=True)

def norm(x):
    return str(x).strip().lower() if x is not None else ""

# ---------------------------------------------------------------- De para
dp = wb["De para Produtos"]
BU_SEG = {
    "events": ("Eventos", True),
    "online programs": ("Produtos Online", True),
    "offline programs": ("Produtos Offline", True),
    "intl. immersions": ("Imersões Internacionais", True),
}
produtos = []  # (real, orc, segmento)
for r in range(3, 25):
    bu = dp.cell(row=r, column=2).value
    real = dp.cell(row=r, column=3).value
    orc = dp.cell(row=r, column=4).value
    if not (bu and real and orc):
        continue
    seg = BU_SEG.get(norm(bu))
    if seg and seg[1]:
        produtos.append((str(real).strip(), str(orc).strip(), seg[0]))

# ---------------------------------------------------------------- Rateio
rt = wb["Rateio de Custos"]
def rate_table(lo, hi):
    d = {}
    for r in range(lo, hi + 1):
        k = norm(rt.cell(row=r, column=2).value)
        v = rt.cell(row=r, column=9).value
        if k:
            d[k] = float(v) if isinstance(v, (int, float)) else 0.0
    return d
R_COM = rate_table(230, 266)
R_TAX = rate_table(270, 304)
R_ENV = rate_table(308, 342)

# ---------------------------------------------------------------- Base de Pagamentos
# acumula (subproduto_lower, classificacao_lower, mes) -> soma valor (ano 2026)
pag = wb["Base de Pagamentos"]
PAG = defaultdict(float)
for row in pag.iter_rows(min_row=3, values_only=True):
    ano = row[31]  # AF
    if ano != 2026:
        continue
    val = row[15]  # P
    if not isinstance(val, (int, float)):
        continue
    sub = norm(row[27])   # AB
    cls = norm(row[22])   # W
    mes = row[30]         # AE
    if not isinstance(mes, (int, float)):
        continue
    PAG[(sub, cls, int(mes))] += val

# ---------------------------------------------------------------- Base de Receita
rec = wb["Base de Receita"]
REC = defaultdict(float)
for row in rec.iter_rows(min_row=3, values_only=True):
    ano = row[9]   # J
    if ano != 2026:
        continue
    val = row[17]  # R
    if not isinstance(val, (int, float)):
        continue
    sub = norm(row[30])  # AE
    mes = row[8]         # I
    if not isinstance(mes, (int, float)):
        continue
    REC[(sub, int(mes))] += val

# ---------------------------------------------------------------- Receitas e Custos Orç
orc = wb["Receitas e Custos Orç"]
ORC = {}  # (subproduto_orc_lower, mes) -> dict
for row in orc.iter_rows(min_row=3, values_only=True):
    l = norm(row[11])   # L
    mes = row[1]        # B
    if not l or not isinstance(mes, (int, float)):
        continue
    def g(i):
        v = row[i]
        return float(v) if isinstance(v, (int, float)) else 0.0
    ORC[(l, int(mes))] = {
        "ROB": g(21), "RecLiq": g(29), "Qtd": g(13),
        "Custos Variáveis": g(32), "Custos de Venda": g(37),
        "Marketing Direto": g(44), "Custos Fixos": g(46),
    }

# ---------------------------------------------------------------- monta registros
def pag_sum(sub_l, cls, m):
    return PAG.get((sub_l, norm(cls), m), 0.0)

GRUPOS = ["Custos Variáveis", "Custos de Venda", "Marketing Direto", "Custos Fixos"]

registros = []
for real, orc_name, seg in produtos:
    rl = norm(real)
    ol = norm(orc_name)
    com = R_COM.get(rl, 0.0)
    tax = R_TAX.get(rl, 0.0)
    env = R_ENV.get(rl, 0.0)
    for m in range(1, 13):
        tem_real = m <= 5
        # ---- REAL (positivo = custo), replicando P&L por Produto
        rb = REC.get((rl, m), 0.0) if tem_real else 0.0
        if tem_real:
            var = pag_sum(rl, "Alimentação", m) + pag_sum(rl, "Outros Custos Variáveis", m)
            venda = com * rb + tax * rb + pag_sum(rl, "Parcerias", m)
            mkt = pag_sum(rl, "Marketing Direto", m)
            fix = (pag_sum(rl, "Locação de espaço", m) + pag_sum(rl, "Faculty", m)
                   + pag_sum(rl, "Deslocamento e estadia interno", m)
                   + pag_sum(rl, "Infra de produção", m) + pag_sum(rl, "Logística", m)
                   + env * rb + pag_sum(rl, "Outros", m))
        else:
            var = venda = mkt = fix = 0.0
        # ---- ORÇADO (positivo = custo)
        ob = ORC.get((ol, m))
        if ob:
            o_rb = ob["ROB"]; o_rl = ob["RecLiq"]; o_qt = ob["Qtd"]
            o_var = -ob["Custos Variáveis"]; o_ven = -ob["Custos de Venda"]
            o_mkt = -ob["Marketing Direto"]; o_fix = -ob["Custos Fixos"]
        else:
            o_rb = o_rl = o_qt = o_var = o_ven = o_mkt = o_fix = 0.0

        rec_dict = {
            "produto": orc_name, "real_nome": real, "segmento": seg, "b2c": True,
            "mes": m, "tem_real": tem_real,
            "real_Custos Variáveis": var, "real_Custos de Venda": venda,
            "real_Marketing Direto": mkt, "real_Custos Fixos": fix,
            "real_Custos Totais": var + venda + mkt + fix,
            "real_Receita Bruta": rb,
            "orc_Custos Variáveis": o_var, "orc_Custos de Venda": o_ven,
            "orc_Marketing Direto": o_mkt, "orc_Custos Fixos": o_fix,
            "orc_Custos Totais": o_var + o_ven + o_mkt + o_fix,
            "orc_Receita Bruta": o_rb, "orc_Receita Líquida": o_rl,
            "orc_Qtd Turmas": o_qt,
        }
        registros.append(rec_dict)

with open("/home/claude/dados.json", "w", encoding="utf-8") as fh:
    json.dump(registros, fh, ensure_ascii=False)

print("registros:", len(registros), "| produtos B2C:", len(produtos))
