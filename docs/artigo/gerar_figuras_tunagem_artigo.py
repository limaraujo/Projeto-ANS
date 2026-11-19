"""Gera figuras e tabelas editoriais a partir dos registros, sem novos ajustes."""

import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-artigo")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/artigo"
FIG = OUT / "figuras/ieee"
T = pd.read_csv(ROOT / "resultados/tunagem/particionais.csv")
D = pd.read_csv(ROOT / "resultados/tunagem/dbscan.csv")
M = pd.read_csv(ROOT / "resultados/metricas_por_k.csv")
Q = json.loads((ROOT / "resultados/execucoes_questao_1.json").read_text())
NOMES = {
    "k-means": "K-Means", "fuzzy-k-means": "FCM",
    "kernel-fuzzy-k-means": "Kernel FCM", "k-medoids": "K-Medoids",
    "gaussian-mixture": "GMM/EM", "upgma": "UPGMA",
}
plt.rcParams.update({"font.size": 10, "axes.titlesize": 10,
                     "legend.fontsize": 8, "pdf.fonttype": 42})
CORES = ["#2878a1", "#d17950", "#4b8b65"]


def fmt(v, casas=4):
    return f"{v:.{casas}f}".replace(".", ",")


def save(fig, name):
    for ax in fig.axes:
        ax.grid(axis="y", alpha=.2)
        if ax.get_ylabel() not in {"m"}:
            ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:g}".replace(".", ",")))
    fig.savefig(FIG / f"tunagem_{name}.pdf", bbox_inches="tight")
    plt.close(fig)


def panels():
    return plt.subplots(1, 2, figsize=(7.2, 2.7), layout="constrained")


for method, param in [("k-means", "init"), ("fuzzy-k-means", "m"), ("k-medoids", "init")]:
    sub = T[T.algoritmo.eq(method)]
    profiles = sub.drop_duplicates("configuracao").sort_values(param)
    fig, axes = panels()
    labels = [str(v).replace(".", ",") for v in profiles[param]]
    axes[0].bar(labels, profiles.silhueta_media, color=CORES[:len(labels)])
    axes[0].set(title="Média em k de 2 a 5", ylabel="Silhueta média", xlabel=param)
    k3 = sub[sub.k.eq(3)].set_index("configuracao").loc[profiles.configuracao]
    axes[1].bar(labels, k3.ari, color=CORES[:len(labels)])
    axes[1].set(title="Concordância em k = 3", ylabel="ARI", xlabel=param)
    save(fig, method.replace("-", "_"))

sub = T[T.algoritmo.eq("kernel-fuzzy-k-means")]
fig, axes = panels()
matrix = sub.drop_duplicates("configuracao").pivot(index="m", columns="gamma", values="silhueta_media")
axes[0].imshow(matrix.to_numpy(), cmap="YlGnBu", aspect="auto")
axes[0].set(xticks=range(len(matrix.columns)), xticklabels=[fmt(x, 2) for x in matrix.columns],
            yticks=range(len(matrix.index)), yticklabels=[fmt(x, 1) for x in matrix.index],
            xlabel="γ", ylabel="m", title="Média em k de 2 a 5")
for (i, j), v in np.ndenumerate(matrix.to_numpy()):
    axes[0].text(j, i, fmt(v), ha="center", va="center", fontsize=9,
                 color="white" if v > matrix.to_numpy().mean() else "black")
for k, group in sub[sub.m.eq(2)].groupby("k"):
    group = group.sort_values("gamma")
    axes[1].plot(range(len(group)), group.silhueta, "o-", label=f"k = {k}")
axes[1].set(xticks=range(3), xticklabels=["0,05", "0,25", "1"],
            xlabel="γ (m = 2)", ylabel="Silhueta", title="Efeito da escala RBF")
axes[1].legend(ncol=2)
save(fig, "kernel_fuzzy_k_means")

sub = T[T.algoritmo.eq("gaussian-mixture")]
fig, axes = panels()
types = ["full", "tied", "diag", "spherical"]
for j, reg in enumerate(sorted(sub.reg_covar.unique())):
    profiles = sub[sub.reg_covar.eq(reg)].drop_duplicates("configuracao").set_index("covariance_type").loc[types]
    k3 = sub[sub.reg_covar.eq(reg) & sub.k.eq(3)].set_index("covariance_type").loc[types]
    x = np.arange(4) + (j-1)*.24
    label = f"reg. {reg:g}".replace(".", ",")
    axes[0].bar(x, profiles.silhueta_media, .24, label=label, color=CORES[j])
    axes[1].bar(x, k3.ari, .24, label=label, color=CORES[j])
for ax, title, ylabel in zip(axes, ["Média em k de 2 a 5", "Concordância em k = 3"], ["Silhueta média", "ARI"]):
    ax.set(xticks=range(4), xticklabels=types, title=title, ylabel=ylabel)
axes[0].legend()
save(fig, "gaussian_mixture")

fig, axes = plt.subplots(1, 3, figsize=(8, 2.7), layout="constrained")
for minimum, group in D.groupby("min_samples"):
    group = group.sort_values("eps")
    for ax, column in zip(axes, ["silhueta", "ari", "cobertura_pct"]):
        ax.plot(group.eps, group[column], "o-", markersize=3, label=str(minimum))
for ax, ylabel in zip(axes, ["Silhueta sem ruído", "ARI sem ruído", "Cobertura (%)"]):
    ax.set(xlabel="ε", ylabel=ylabel)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:g}".replace(".", ",")))
axes[0].legend(title="min_samples")
axes[2].axhline(95, color="#555555", ls="--", lw=1)
selected = D[D.selecionado].iloc[0]
for ax, col in zip(axes, ["silhueta", "ari", "cobertura_pct"]):
    ax.scatter([selected.eps], [selected[col]], s=90, facecolors="none", edgecolors="red", zorder=5)
save(fig, "dbscan")

rows_k3 = [[NOMES[r.algoritmo], fmt(r.silhueta), fmt(r.ari)]
           for r in M[M.k.eq(3)].sort_values("ari", ascending=False).itertuples()]
ranges = []
for method in list(NOMES)[:5]:
    runs = Q[method]["3"]
    values = [run["objetivo"] for run in runs]
    best = M[M.algoritmo.eq(method) & M.k.eq(3)].iloc[0]
    ranges.append([NOMES[method], fmt(min(values)), fmt(max(values)), str(int(best.seed))])
(OUT / "resumo_etapas.json").write_text(json.dumps({"k3": rows_k3, "objetivos_k3": ranges}, ensure_ascii=False, indent=2)+"\n")
