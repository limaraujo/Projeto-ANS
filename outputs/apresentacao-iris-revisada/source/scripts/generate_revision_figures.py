#!/usr/bin/env python3
"""Gera apenas visualizações a partir dos registros existentes; não reajusta modelos."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from scipy.cluster.hierarchy import dendrogram


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parents[1] / "assets" / "input"
BG = "#141414"
BG2 = "#202020"
FG = "#F5F5F5"
MUTED = "#B8B8B8"
GRID = "#3A3A3A"
YELLOW = "#FFD400"


def comma(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def style_ax(ax):
    ax.set_facecolor(BG)
    ax.tick_params(colors=FG, labelsize=18)
    for spine in ax.spines.values():
        spine.set_color(MUTED)
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    ax.title.set_color(FG)


def save(fig, name: str):
    fig.patch.set_facecolor(BG)
    fig.savefig(OUT / name, dpi=220, facecolor=BG, bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)


def read_csv(name: str):
    with (ROOT / name).open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def panel_heatmap(ax, values, row_labels, col_labels, selected, title, x_label, y_label=None):
    # A intensidade permanece neutra; amarelo é reservado à configuração escolhida.
    style_ax(ax)
    display = np.zeros_like(values, dtype=float)
    ax.imshow(display, cmap=ListedColormap([BG2]), vmin=0, vmax=1, aspect="auto")
    for y in range(values.shape[0]):
        for x in range(values.shape[1]):
            chosen = (y, x) == selected
            ax.add_patch(
                plt.Rectangle(
                    (x - 0.5, y - 0.5), 1, 1,
                    facecolor=YELLOW if chosen else BG2,
                    edgecolor=YELLOW if chosen else "#666666",
                    linewidth=4 if chosen else 1.3,
                )
            )
            ax.text(
                x, y, comma(values[y, x]), ha="center", va="center",
                color="#0B0B0B" if chosen else FG, fontsize=18,
                fontweight="bold" if chosen else "normal",
            )
    ax.set_xticks(range(len(col_labels)), col_labels)
    ax.set_yticks(range(len(row_labels)), row_labels)
    ax.set_title(title, fontsize=26, fontweight="bold", pad=12, color=FG)
    ax.set_xlabel(x_label, fontsize=20, labelpad=8, color=FG)
    if y_label:
        ax.set_ylabel(y_label, fontsize=20, labelpad=8, color=FG)
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)


def make_slide_8():
    rows = read_csv("resultados/tunagem/particionais.csv")
    kernel = [r for r in rows if r["algoritmo"] == "kernel-fuzzy-k-means" and r["k"] == "2"]
    # silhueta_media é repetida por k; k=2 fornece uma linha por configuração.
    ms = [2.5, 2.0, 1.5]
    gammas = [0.05, 0.25, 1.0]
    kernel_values = np.array([
        [float(next(r["silhueta_media"] for r in kernel if float(r["m"]) == m and float(r["gamma"]) == g)) for g in gammas]
        for m in ms
    ])

    gmm = [r for r in rows if r["algoritmo"] == "gaussian-mixture" and r["k"] == "2"]
    covs = ["full", "tied", "diag", "spherical"]
    regs = [1e-6, 1e-4, 1e-2]
    gmm_values = np.array([
        [float(next(r["silhueta_media"] for r in gmm if r["covariance_type"] == cov and np.isclose(float(r["reg_covar"]), reg))) for reg in regs]
        for cov in covs
    ])

    db = read_csv("resultados/tunagem/dbscan.csv")
    fig, axes = plt.subplots(1, 3, figsize=(15.2, 4.5), gridspec_kw={"width_ratios": [1, 1.13, 1.18]})
    fig.subplots_adjust(left=0.045, right=0.99, top=0.88, bottom=0.20, wspace=0.34)
    panel_heatmap(
        axes[0], kernel_values,
        ["2,5", "2,0", "1,5"], ["0,05", "0,25", "1,0"], (1, 0),
        "Kernel FCM", "γ (RBF)", "m",
    )
    panel_heatmap(
        axes[1], gmm_values, covs,
        ["10⁻⁶", "10⁻⁴", "10⁻²"], (3, 2),
        "GMM/EM", "regularização",
    )

    ax = axes[2]
    style_ax(ax)
    markers = {"3": "o", "5": "s", "10": "^"}
    for min_samples, marker in markers.items():
        subset = [r for r in db if r["min_samples"] == min_samples and r["silhueta"]]
        ax.scatter(
            [float(r["cobertura_pct"]) for r in subset],
            [float(r["silhueta"]) for r in subset],
            marker=marker, s=90, facecolors="none", edgecolors=FG, linewidths=1.8,
            label=f"min_samples = {min_samples}", zorder=3,
        )
    selected = next(r for r in db if r["selecionado"] == "True")
    sx, sy = float(selected["cobertura_pct"]), float(selected["silhueta"])
    ax.axvline(95, color=YELLOW, linestyle="--", linewidth=2.6, zorder=1)
    ax.scatter([sx], [sy], s=310, facecolors="none", edgecolors=YELLOW, linewidths=4, zorder=5)
    ax.annotate(
        "selecionada",
        xy=(sx, sy), xytext=(65, 0.535), color=YELLOW, fontsize=13.5, fontweight="bold",
        arrowprops={"arrowstyle": "->", "color": YELLOW, "lw": 2},
        bbox={"boxstyle": "square,pad=0.25", "fc": BG, "ec": YELLOW, "lw": 1.5},
    )
    ax.text(95.5, 0.13, "piso 95%", color=YELLOW, fontsize=15, rotation=90, va="bottom")
    ax.set_xlim(10, 102)
    ax.set_ylim(0.12, 0.69)
    ax.set_xticks([20, 40, 60, 80, 100])
    ax.set_yticks([0.2, 0.4, 0.6], ["0,2", "0,4", "0,6"])
    ax.set_title("DBSCAN", fontsize=26, fontweight="bold", pad=12)
    ax.set_xlabel("Cobertura (%)", fontsize=20, labelpad=8)
    ax.set_ylabel("Silhueta", fontsize=20, labelpad=8)
    ax.grid(color=GRID, alpha=0.75, linewidth=0.8)
    ax.legend(loc="lower left", fontsize=12.5, frameon=False, labelcolor=FG, handletextpad=0.4)
    save(fig, "figure-8-revised.png")


def make_slide_10():
    payload = json.loads((ROOT / "resultados/execucoes_questao_1.json").read_text(encoding="utf-8"))
    hierarchy = np.asarray(payload["upgma"]["2"]["hierarquia"], dtype=float)
    n = hierarchy.shape[0] + 1
    fig, ax = plt.subplots(figsize=(15.4, 4.35))
    fig.subplots_adjust(left=0.065, right=0.94, top=0.95, bottom=0.30)
    dendrogram(
        hierarchy, truncate_mode="lastp", p=12, show_leaf_counts=True,
        leaf_label_func=lambda node: f"({int(hierarchy[node-n, 3])})" if node >= n else str(node),
        leaf_rotation=0, leaf_font_size=18, ax=ax, color_threshold=0,
        above_threshold_color=FG, link_color_func=lambda _: FG,
    )
    for line in ax.get_lines():
        line.set_linewidth(2.4)
    heights = {}
    for k, color in [(2, YELLOW), (3, FG)]:
        height = (hierarchy[-k, 2] + hierarchy[-k + 1, 2]) / 2
        heights[k] = height
        ax.axhline(height, color=color, linestyle="--", linewidth=3.2, zorder=4)
        ax.text(
            119.5, height + 0.08, f"corte: {k} grupos", color=color, fontsize=17,
            fontweight="bold", va="bottom", ha="left",
            bbox={"boxstyle": "square,pad=0.18", "fc": BG, "ec": color, "lw": 1.5},
        )
    style_ax(ax)
    ax.set_ylabel("Distância Manhattan", fontsize=20, labelpad=10)
    ax.set_xlabel(
        "As folhas representam subárvores agregadas; os números entre parênteses indicam a quantidade de observações.",
        fontsize=16, labelpad=14, color=FG,
    )
    ax.set_yticks([0, 2, 4, 6], ["0", "2", "4", "6"])
    ax.tick_params(axis="x", pad=10)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_xlim(-1, 135)
    save(fig, "figure-10-revised.png")


def make_slide_11():
    rows = [
        ("97%", "1,000", "10", "97,33%", "0,5984", "0,5706"),
        ("95%", "0,694", "3", "96,00%", "0,6035", "0,5760"),
        ("94%", "0,694", "5", "94,67%", "0,6104", "0,5733"),
        ("85%", "0,694", "10", "86,67%", "0,6276", "0,6001"),
        ("75%", "0,600", "10", "76,67%", "0,6482", "0,6358"),
    ]
    cols = ["Piso", "ε", "min_samples", "Cobertura", "Silhueta", "ARI"]
    fig, ax = plt.subplots(figsize=(15.4, 4.55))
    ax.set_axis_off()
    fig.subplots_adjust(left=0.02, right=0.98, top=0.96, bottom=0.03)
    table = ax.table(cellText=rows, colLabels=cols, cellLoc="center", colLoc="center", bbox=[0.01, 0.38, 0.98, 0.59])
    table.auto_set_font_size(False)
    table.set_fontsize(19)
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor(FG)
        cell.set_linewidth(1.2)
        cell.set_text_props(color=FG, fontweight="bold" if r == 0 else "normal")
        cell.set_facecolor("#2B2B2B" if r == 0 else BG2)
    # Cabeçalho = linha 0; o piso de 95% é a segunda linha de dados.
    for c in range(len(cols)):
        cell = table[(2, c)]
        cell.set_facecolor(YELLOW)
        cell.set_text_props(color="#0B0B0B", fontweight="bold")
        cell.set_linewidth(2.8)
        cell.set_edgecolor(YELLOW)
    ax.text(0.01, 0.285, "LEITURA", color=YELLOW, fontsize=18, fontweight="bold", transform=ax.transAxes)
    ax.text(
        0.15, 0.285,
        "A silhueta aumenta quando mais observações são descartadas; as linhas não usam a mesma amostra.",
        color=FG, fontsize=18, fontweight="bold", transform=ax.transAxes,
    )
    ax.text(
        0.01, 0.155,
        "MÉTODO  95% foi definido antes da seleção; pisos menores foram examinados depois, como sensibilidade.",
        color=FG, fontsize=16.5, transform=ax.transAxes,
    )
    ax.text(
        0.01, 0.055,
        "COMPARAÇÃO  Silhuetas exigem atenção ao conjunto retido.  |  Escolhida: 2 grupos; 6 ruídos.",
        color=MUTED, fontsize=16.5, transform=ax.transAxes,
    )
    save(fig, "figure-11-revised.png")


def make_slide_16():
    series = [
        ("K-Means", 0.4290, 0.6451, 1, YELLOW),
        ("GMM/EM", 0.4199, 0.6199, 6, FG),
    ]
    fig, ax = plt.subplots(figsize=(15.4, 4.45))
    fig.subplots_adjust(left=0.16, right=0.96, top=0.92, bottom=0.32)
    style_ax(ax)
    ax.set_xlim(0.39, 0.67)
    ax.set_ylim(-0.6, 1.6)
    ax.set_yticks([1, 0], ["K-Means", "GMM/EM"])
    ax.set_xticks([0.40, 0.45, 0.50, 0.55, 0.60, 0.65], ["0,40", "0,45", "0,50", "0,55", "0,60", "0,65"])
    ax.set_xlabel("ARI observado nas 10 inicializações (k = 3)", fontsize=18, labelpad=10)
    ax.grid(axis="x", color=GRID, linewidth=1)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for y, (name, lo, hi, count, color) in zip([1, 0], series):
        ax.hlines(y, lo, hi, color=color, linewidth=8, zorder=3)
        ax.scatter([lo, hi], [y, y], s=180, color=color, edgecolors=BG, linewidths=1.5, zorder=4)
        ax.text(lo, y + 0.23, comma(lo, 4), color=color, fontsize=18, fontweight="bold", ha="center")
        ax.text(hi, y + 0.23, comma(hi, 4), color=color, fontsize=18, fontweight="bold", ha="center")
        ax.text(
            (lo + hi) / 2, y - 0.31,
            f"amplitude = {comma(hi-lo, 4)}  |  melhor objetivo: {count}/10",
            color=FG, fontsize=16.5, ha="center",
        )
    fig.text(
        0.56, 0.105,
        "Dez inicializações não equivalem a dez amostras independentes do conjunto de dados.",
        color=YELLOW, fontsize=16.5, fontweight="bold", ha="center",
    )
    fig.text(
        0.56, 0.035, "Objetivo: até 10⁻³ do melhor (não igualdade exata) · faixas não são intervalos de confiança.",
        color=MUTED, fontsize=14.5, ha="center",
    )
    save(fig, "figure-16-revised.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    make_slide_8()
    make_slide_10()
    make_slide_11()
    make_slide_16()
