"""Busca não supervisionada de hiperparâmetros e análise de sensibilidade dos 7 algoritmos."""

from itertools import product
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from threadpoolctl import threadpool_limits

from algoritmos import (
    calcular_ari,
    calcular_silhueta,
    carregar_iris,
    dbscan,
    executar_melhores_por_k,
    plt,
    salvar_json,
    selecionar_k_por_silhueta,
    sns,
    upgma,
)

RAIZ = Path(__file__).resolve().parent.parent
DIRETORIO_SAIDA = RAIZ / "resultados" / "tunagem"
DIRETORIO_FIGURAS = RAIZ / "resultados" / "figuras"


def _avaliar_particional_na_grade(
    nome: str,
    dados: np.ndarray,
    y_true: np.ndarray,
    grade: list[dict[str, Any]],
    sentido_objetivo: str = "minimizar",
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Avalia uma grade de hiperparâmetros para um algoritmo baseado em k."""
    linhas = []
    for params in grade:
        melhores = executar_melhores_por_k(nome, dados, valores_k=range(1, 6), **params)
        k_estrela, silhuetas = selecionar_k_por_silhueta(dados, melhores)
        linhas.append(
            {
                **params,
                "k_estrela": k_estrela,
                "silhueta": silhuetas[k_estrela],
                "ari": calcular_ari(y_true, melhores[k_estrela].rotulos),
                "objetivo": melhores[k_estrela].objetivo,
                "silhueta_k3": silhuetas[3],
                "ari_k3": calcular_ari(y_true, melhores[3].rotulos),
                "objetivo_k3": melhores[3].objetivo,
            }
        )

    df = pd.DataFrame(linhas)
    asc_obj = sentido_objetivo == "minimizar"
    melhor_linha = df.sort_values(
        by=["silhueta", "objetivo"],
        ascending=[False, asc_obj],
        kind="mergesort",
    ).iloc[0]

    chaves_param = list(grade[0].keys())
    melhores_params = {
        k: (
            melhor_linha[k].item()
            if hasattr(melhor_linha[k], "item")
            else melhor_linha[k]
        )
        for k in chaves_param
    }
    resumo_selecao = {
        "algoritmo": nome,
        "parametros": melhores_params,
        "k_estrela": int(melhor_linha["k_estrela"]),
        "silhueta": float(melhor_linha["silhueta"]),
        "ari": float(melhor_linha["ari"]),
        "silhueta_k3": float(melhor_linha["silhueta_k3"]),
        "ari_k3": float(melhor_linha["ari_k3"]),
    }
    return df, resumo_selecao


def tunar_kmeans(dados: np.ndarray, y_true: np.ndarray) -> tuple[pd.DataFrame, dict[str, Any]]:
    grade = [
        {"init": init, "tol": tol, "max_iter": max_iter}
        for init, tol, max_iter in product(
            ["k-means++", "random"], [1e-2, 1e-4, 1e-6], [50, 100, 300]
        )
    ]
    return _avaliar_particional_na_grade("k-means", dados, y_true, grade, "minimizar")


def tunar_fuzzy_kmeans(
    dados: np.ndarray, y_true: np.ndarray
) -> tuple[pd.DataFrame, dict[str, Any]]:
    grade = [
        {"m": m, "error": error}
        for m, error in product([1.2, 1.5, 1.8, 2.0, 2.5, 3.0], [1e-3, 1e-5, 1e-7])
    ]
    return _avaliar_particional_na_grade(
        "fuzzy-k-means", dados, y_true, grade, "minimizar"
    )


def tunar_kernel_fuzzy_kmeans(
    dados: np.ndarray, y_true: np.ndarray
) -> tuple[pd.DataFrame, dict[str, Any]]:
    grade = [
        {"gamma": gamma, "m": m}
        for gamma, m in product([0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0], [1.5, 2.0, 2.5])
    ]
    return _avaliar_particional_na_grade(
        "kernel-fuzzy-k-means", dados, y_true, grade, "minimizar"
    )


def tunar_kmedoids(
    dados: np.ndarray, y_true: np.ndarray
) -> tuple[pd.DataFrame, dict[str, Any]]:
    grade = [
        {"init": init, "max_iter": max_iter}
        for init, max_iter in product(["build", "random", "first"], [50, 100, 300])
    ]
    return _avaliar_particional_na_grade(
        "k-medoids", dados, y_true, grade, "minimizar"
    )


def tunar_gaussian_mixture(
    dados: np.ndarray, y_true: np.ndarray
) -> tuple[pd.DataFrame, dict[str, Any]]:
    grade = [
        {
            "covariance_type": cov,
            "reg_covar": reg,
            "init_params": init_p,
        }
        for cov, reg, init_p in product(
            ["full", "tied", "diag", "spherical"],
            [1e-6, 1e-4, 1e-2],
            ["random_from_data", "kmeans"],
        )
    ]
    return _avaliar_particional_na_grade(
        "gaussian-mixture", dados, y_true, grade, "maximizar"
    )


def tunar_upgma(
    dados: np.ndarray, y_true: np.ndarray
) -> tuple[pd.DataFrame, dict[str, Any]]:
    linhas = []
    for escalonamento, optimal_ordering in product(
        ["standard", "minmax", "robust", "l2"], [False, True]
    ):
        resultados = upgma(
            dados,
            valores_k=(1, 2, 3, 4, 5),
            escalonamento=escalonamento,
            optimal_ordering=optimal_ordering,
        )
        k_estrela, silhuetas = selecionar_k_por_silhueta(dados, resultados)
        linhas.append(
            {
                "escalonamento": escalonamento,
                "optimal_ordering": optimal_ordering,
                "k_estrela": k_estrela,
                "silhueta": silhuetas[k_estrela],
                "ari": calcular_ari(y_true, resultados[k_estrela].rotulos),
                "silhueta_k3": silhuetas[3],
                "ari_k3": calcular_ari(y_true, resultados[3].rotulos),
            }
        )

    df = pd.DataFrame(linhas)
    melhor_linha = df.sort_values(
        by=["silhueta", "ari_k3"],
        ascending=[False, False],
        kind="mergesort",
    ).iloc[0]
    resumo_selecao = {
        "algoritmo": "upgma",
        "parametros": {
            "escalonamento": str(melhor_linha["escalonamento"]),
            "optimal_ordering": bool(melhor_linha["optimal_ordering"]),
        },
        "k_estrela": int(melhor_linha["k_estrela"]),
        "silhueta": float(melhor_linha["silhueta"]),
        "ari": float(melhor_linha["ari"]),
        "silhueta_k3": float(melhor_linha["silhueta_k3"]),
        "ari_k3": float(melhor_linha["ari_k3"]),
    }
    return df, resumo_selecao


def tunar_dbscan(
    dados: np.ndarray, y_true: np.ndarray
) -> tuple[pd.DataFrame, dict[str, Any]]:
    referencia = float(
        np.median(
            NearestNeighbors(n_neighbors=5).fit(dados).kneighbors(dados)[0][:, -1]
        )
    )
    linhas = []
    for eps, min_samples in product(
        [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2], [3, 4, 5, 7, 10]
    ):
        res = dbscan(dados, eps=eps, min_samples=min_samples)
        rotulos = res.rotulos
        grupos = len(set(rotulos) - {-1})
        ruido = int(np.sum(rotulos == -1))
        ruido_pct = 100.0 * ruido / len(rotulos)
        linhas.append(
            {
                "eps": float(eps),
                "min_samples": int(min_samples),
                "referencia_5_vizinhos": referencia,
                "grupos": grupos,
                "ruido": ruido,
                "ruido_pct": ruido_pct,
                "silhueta": calcular_silhueta(dados, rotulos, ignorar_ruido=True),
                "ari": calcular_ari(y_true, rotulos, ignorar_ruido=True),
            }
        )

    df = pd.DataFrame(linhas)
    # Salvaguarda não supervisionada: exigir >= 2 grupos e <= 20% de ruído
    candidatos = df[(df["grupos"] >= 2) & (df["ruido_pct"] <= 20.0)].dropna(
        subset=["silhueta"]
    )
    if candidatos.empty:
        candidatos = df[df["grupos"] >= 2].dropna(subset=["silhueta"])

    melhor_linha = candidatos.sort_values(
        by=["silhueta", "ruido"],
        ascending=[False, True],
        kind="mergesort",
    ).iloc[0]

    resumo_selecao = {
        "algoritmo": "dbscan",
        "parametros": {
            "eps": float(melhor_linha["eps"]),
            "min_samples": int(melhor_linha["min_samples"]),
        },
        "grupos": int(melhor_linha["grupos"]),
        "ruido": int(melhor_linha["ruido"]),
        "ruido_pct": float(melhor_linha["ruido_pct"]),
        "silhueta": float(melhor_linha["silhueta"]),
        "ari": float(melhor_linha["ari"]),
    }
    return df, resumo_selecao


def _plotar_sensibilidade(
    df_kmeans: pd.DataFrame,
    df_fcm: pd.DataFrame,
    df_kfcm: pd.DataFrame,
    df_kmedoids: pd.DataFrame,
    df_gmm: pd.DataFrame,
    df_upgma: pd.DataFrame,
    df_dbscan: pd.DataFrame,
    diretorio_figuras: Path,
) -> None:
    """Gera um gráfico de comportamento por hiperparâmetro para cada um dos 7 algoritmos."""
    diretorio_figuras.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="notebook")

    # 1. K-Means
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
    sub_km = df_kmeans[df_kmeans["max_iter"] == 300].copy()
    sub_km["tol_str"] = sub_km["tol"].apply(lambda v: f"{v:.0e}")
    sns.barplot(
        data=sub_km, x="tol_str", y="silhueta", hue="init", ax=axes[0]
    )
    axes[0].set(title="K-Means: Silhueta (k*) por init e tol", xlabel="Tolerância (tol)", ylabel="Silhueta (k*)")
    axes[0].set_ylim(0, 0.8)
    sns.barplot(
        data=sub_km, x="tol_str", y="ari_k3", hue="init", ax=axes[1]
    )
    axes[1].set(title="K-Means: ARI (k=3) por init e tol", xlabel="Tolerância (tol)", ylabel="ARI (k=3)")
    axes[1].set_ylim(0, 0.8)
    fig.tight_layout()
    fig.savefig(diretorio_figuras / "tunagem_k_means.png", dpi=150)
    plt.close(fig)

    # 2. Fuzzy K-Means
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
    sub_fcm = df_fcm[np.isclose(df_fcm["error"], 1e-5)]
    sns.lineplot(
        data=sub_fcm, x="m", y="silhueta", marker="o", label="Silhueta (k*)", ax=axes[0]
    )
    sns.lineplot(
        data=sub_fcm, x="m", y="silhueta_k3", marker="s", label="Silhueta (k=3)", ax=axes[0]
    )
    axes[0].set(title="Fuzzy K-Means: Silhueta × m", xlabel="Fuzzifier (m)", ylabel="Silhueta")
    sns.lineplot(
        data=sub_fcm, x="m", y="ari", marker="o", label="ARI (k*)", ax=axes[1]
    )
    sns.lineplot(
        data=sub_fcm, x="m", y="ari_k3", marker="s", label="ARI (k=3)", ax=axes[1]
    )
    axes[1].set(title="Fuzzy K-Means: ARI × m", xlabel="Fuzzifier (m)", ylabel="ARI")
    fig.tight_layout()
    fig.savefig(diretorio_figuras / "tunagem_fuzzy_k_means.png", dpi=150)
    plt.close(fig)

    # 3. Kernel Fuzzy K-Means
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4))
    piv_sil = df_kfcm.pivot(index="m", columns="gamma", values="silhueta")
    sns.heatmap(piv_sil, annot=True, fmt=".3f", cmap="YlGnBu", ax=axes[0])
    axes[0].set(title="Kernel FCM: Silhueta (k*) por (m, gamma)", xlabel="gamma", ylabel="m")
    piv_ari = df_kfcm.pivot(index="m", columns="gamma", values="ari_k3")
    sns.heatmap(piv_ari, annot=True, fmt=".3f", cmap="OrRd", ax=axes[1])
    axes[1].set(title="Kernel FCM: ARI (k=3) por (m, gamma)", xlabel="gamma", ylabel="m")
    fig.tight_layout()
    fig.savefig(diretorio_figuras / "tunagem_kernel_fuzzy_k_means.png", dpi=150)
    plt.close(fig)

    # 4. K-Medoids
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
    sub_kmed = df_kmedoids[df_kmedoids["max_iter"] == 300]
    sns.barplot(data=sub_kmed, x="init", y="silhueta", color="#2676a1", ax=axes[0])
    axes[0].set(title="K-Medoids (Euclidiana): Silhueta (k*) por init", xlabel="Inicialização (init)", ylabel="Silhueta (k*)")
    axes[0].set_ylim(0, 0.8)
    sns.barplot(data=sub_kmed, x="init", y="ari_k3", color="#e07a5f", ax=axes[1])
    axes[1].set(title="K-Medoids (Euclidiana): ARI (k=3) por init", xlabel="Inicialização (init)", ylabel="ARI (k=3)")
    axes[1].set_ylim(0, 0.9)
    fig.tight_layout()
    fig.savefig(diretorio_figuras / "tunagem_k_medoids.png", dpi=150)
    plt.close(fig)

    # 5. GMM / EM
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4))
    sub_gmm = df_gmm[df_gmm["init_params"] == "random_from_data"].copy()
    sub_gmm["reg_str"] = sub_gmm["reg_covar"].apply(lambda v: f"{v:.0e}")
    sns.barplot(
        data=sub_gmm, x="covariance_type", y="silhueta", hue="reg_str", ax=axes[0]
    )
    axes[0].set(title="GMM/EM: Silhueta (k*) por covariância e reg_covar", xlabel="Tipo de covariância", ylabel="Silhueta (k*)")
    axes[0].set_ylim(0, 0.8)
    sns.barplot(
        data=sub_gmm, x="covariance_type", y="ari_k3", hue="reg_str", ax=axes[1]
    )
    axes[1].set(title="GMM/EM: ARI (k=3) por covariância e reg_covar", xlabel="Tipo de covariância", ylabel="ARI (k=3)")
    axes[1].set_ylim(0, 1.0)
    fig.tight_layout()
    fig.savefig(diretorio_figuras / "tunagem_gaussian_mixture.png", dpi=150)
    plt.close(fig)

    # 6. UPGMA
    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    sub_upgma = df_upgma[~df_upgma["optimal_ordering"]].melt(
        id_vars="escalonamento",
        value_vars=["silhueta", "ari", "silhueta_k3", "ari_k3"],
        var_name="Métrica",
        value_name="Valor",
    )
    sns.barplot(data=sub_upgma, x="escalonamento", y="Valor", hue="Métrica", ax=ax)
    ax.set(
        title="UPGMA (Manhattan): comportamento por escalonamento dos atributos",
        xlabel="Escalonamento",
        ylabel="Pontuação",
    )
    ax.set_ylim(0, 0.9)
    fig.tight_layout()
    fig.savefig(diretorio_figuras / "tunagem_upgma.png", dpi=150)
    plt.close(fig)

    # 7. DBSCAN
    fig, axes = plt.subplots(1, 3, figsize=(14.5, 4.3))
    sns.lineplot(
        data=df_dbscan, x="eps", y="silhueta", hue="min_samples", marker="o", palette="viridis", ax=axes[0]
    )
    axes[0].set(title="DBSCAN: Silhueta (sem ruído) × eps", xlabel="eps", ylabel="Silhueta")
    sns.lineplot(
        data=df_dbscan, x="eps", y="ari", hue="min_samples", marker="o", palette="viridis", ax=axes[1]
    )
    axes[1].set(title="DBSCAN: ARI (sem ruído) × eps", xlabel="eps", ylabel="ARI")
    sns.lineplot(
        data=df_dbscan, x="eps", y="ruido_pct", hue="min_samples", marker="o", palette="viridis", ax=axes[2]
    )
    axes[2].axhline(20.0, color="#c43c39", linestyle="--", label="Limite 20%")
    axes[2].set(title="DBSCAN: Ruído (%) × eps", xlabel="eps", ylabel="Ruído (%)")
    fig.tight_layout()
    fig.savefig(diretorio_figuras / "tunagem_dbscan.png", dpi=150)
    plt.close(fig)


def executar_tunagem_completa(
    dados: np.ndarray,
    y_true: np.ndarray,
    diretorio_saida: Path = DIRETORIO_SAIDA,
    diretorio_figuras: Path = DIRETORIO_FIGURAS,
) -> dict[str, dict[str, Any]]:
    """Executa a busca de hiperparâmetros dos 7 algoritmos, salva CSVs e figuras."""
    diretorio_saida.mkdir(parents=True, exist_ok=True)
    diretorio_figuras.mkdir(parents=True, exist_ok=True)

    print("Tunando hiperparâmetros dos 7 algoritmos...")
    df_km, sel_km = tunar_kmeans(dados, y_true)
    df_fcm, sel_fcm = tunar_fuzzy_kmeans(dados, y_true)
    df_kfcm, sel_kfcm = tunar_kernel_fuzzy_kmeans(dados, y_true)
    df_kmed, sel_kmed = tunar_kmedoids(dados, y_true)
    df_gmm, sel_gmm = tunar_gaussian_mixture(dados, y_true)
    df_upgma, sel_upgma = tunar_upgma(dados, y_true)
    df_db, sel_db = tunar_dbscan(dados, y_true)

    tabelas = {
        "k-means": df_km,
        "fuzzy-k-means": df_fcm,
        "kernel-fuzzy-k-means": df_kfcm,
        "k-medoids": df_kmed,
        "gaussian-mixture": df_gmm,
        "upgma": df_upgma,
        "dbscan": df_db,
    }
    for nome, df in tabelas.items():
        df.to_csv(
            diretorio_saida / f"tunagem_{nome.replace('-', '_')}.csv",
            index=False,
            encoding="utf-8",
        )

    selecoes = {
        "k-means": sel_km,
        "fuzzy-k-means": sel_fcm,
        "kernel-fuzzy-k-means": sel_kfcm,
        "k-medoids": sel_kmed,
        "gaussian-mixture": sel_gmm,
        "upgma": sel_upgma,
        "dbscan": sel_db,
    }
    salvar_json(diretorio_saida / "melhores_hiperparametros.json", selecoes)
    _plotar_sensibilidade(
        df_km, df_fcm, df_kfcm, df_kmed, df_gmm, df_upgma, df_db, diretorio_figuras
    )
    print(f"Tunagem concluída e salva em: {diretorio_saida}")
    return selecoes


def main() -> None:
    dados, y_true, _ = carregar_iris(padronizar=True)
    executar_tunagem_completa(dados, y_true)


if __name__ == "__main__":
    with threadpool_limits(limits=1):
        main()