"""Busca piloto não supervisionada de hiperparâmetros e análise de sensibilidade."""

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
SEMENTES_PILOTO_INICIAL = 0  # Sementes piloto 0..9 (separadas das oficiais 42..51)


def _avaliar_particional_piloto(
    nome: str,
    dados: np.ndarray,
    y_true: np.ndarray,
    grade: list[tuple[dict[str, Any], bool]],
    sentido_objetivo: str = "minimizar",
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Avalia a grade piloto sobre k in {2, 3, 4, 5} e escolhe pela média da silhueta."""
    linhas_resumo = []
    linhas_detalhadas = []
    valores_k_piloto = range(2, 6)

    for idx_cfg, (params, eh_referencia) in enumerate(grade):
        melhores = executar_melhores_por_k(
            nome,
            dados,
            valores_k=valores_k_piloto,
            seed_inicial=SEMENTES_PILOTO_INICIAL,
            **params,
        )
        silhuetas_k = {}
        objetivos_k = {}
        aris_k = {}
        for k in valores_k_piloto:
            sil = calcular_silhueta(dados, melhores[k].rotulos)
            ari = calcular_ari(y_true, melhores[k].rotulos)
            obj = float(melhores[k].objetivo)
            silhuetas_k[k] = sil
            objetivos_k[k] = obj
            aris_k[k] = ari
            linhas_detalhadas.append(
                {
                    "algoritmo": nome,
                    "config_id": idx_cfg,
                    **params,
                    "eh_referencia": eh_referencia,
                    "k": k,
                    "silhueta": sil,
                    "objetivo": obj,
                    "ari": ari,
                }
            )

        silhueta_media = float(np.mean(list(silhuetas_k.values())))
        objetivo_medio = float(np.mean(list(objetivos_k.values())))
        linhas_resumo.append(
            {
                **params,
                "eh_referencia": eh_referencia,
                "silhueta_k2": silhuetas_k[2],
                "silhueta_k3": silhuetas_k[3],
                "silhueta_k4": silhuetas_k[4],
                "silhueta_k5": silhuetas_k[5],
                "silhueta_media_k2_k5": silhueta_media,
                "ari_k2": aris_k[2],
                "ari_k3": aris_k[3],
                "objetivo_medio": objetivo_medio,
            }
        )

    df_resumo = pd.DataFrame(linhas_resumo)
    df_detalhado = pd.DataFrame(linhas_detalhadas)

    # Arredonda silhueta média a 9 casas para garantir desempate exato pela referência
    df_resumo["_sil_ord"] = df_resumo["silhueta_media_k2_k5"].round(9)
    asc_obj = sentido_objetivo == "minimizar"
    melhor_linha = df_resumo.sort_values(
        by=["_sil_ord", "eh_referencia", "objetivo_medio"],
        ascending=[False, False, asc_obj],
        kind="mergesort",
    ).iloc[0]
    df_resumo = df_resumo.drop(columns=["_sil_ord"])

    chaves_param = list(grade[0][0].keys())
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
        "eh_referencia": bool(melhor_linha["eh_referencia"]),
        "silhueta_media_k2_k5": float(melhor_linha["silhueta_media_k2_k5"]),
        "silhueta_k2": float(melhor_linha["silhueta_k2"]),
        "silhueta_k3": float(melhor_linha["silhueta_k3"]),
        "ari_k2": float(melhor_linha["ari_k2"]),
        "ari_k3": float(melhor_linha["ari_k3"]),
    }
    return df_resumo, df_detalhado, resumo_selecao


def tunar_kmeans(dados: np.ndarray, y_true: np.ndarray):
    ref = {"init": "k-means++", "tol": 1e-4, "max_iter": 300}
    grade = [
        (cfg := {"init": init, "tol": tol, "max_iter": max_iter}, cfg == ref)
        for init, tol, max_iter in product(
            ["k-means++", "random"], [1e-2, 1e-4, 1e-6], [50, 100, 300]
        )
    ]
    return _avaliar_particional_piloto("k-means", dados, y_true, grade, "minimizar")


def tunar_fuzzy_kmeans(dados: np.ndarray, y_true: np.ndarray):
    ref = {"m": 2.0, "error": 1e-5}
    grade = [
        (cfg := {"m": m, "error": error}, cfg == ref)
        for m, error in product([1.5, 2.0, 2.5, 3.0], [1e-4, 1e-5, 1e-6])
    ]
    return _avaliar_particional_piloto(
        "fuzzy-k-means", dados, y_true, grade, "minimizar"
    )


def tunar_kernel_fuzzy_kmeans(dados: np.ndarray, y_true: np.ndarray):
    ref = {"gamma": 0.25, "m": 2.0}
    grade = [
        (cfg := {"gamma": gamma, "m": m}, cfg == ref)
        for m, gamma in product([1.5, 2.0, 2.5], [0.05, 0.25, 1.0])
    ]
    return _avaliar_particional_piloto(
        "kernel-fuzzy-k-means", dados, y_true, grade, "minimizar"
    )


def tunar_kmedoids(dados: np.ndarray, y_true: np.ndarray):
    ref = {"init": "random", "max_iter": 300}
    grade = [
        (cfg := {"init": init, "max_iter": max_iter}, cfg == ref)
        for init, max_iter in product(["random", "first"], [50, 100, 300])
    ]
    return _avaliar_particional_piloto(
        "k-medoids", dados, y_true, grade, "minimizar"
    )


def tunar_gaussian_mixture(dados: np.ndarray, y_true: np.ndarray):
    ref = {
        "covariance_type": "full",
        "reg_covar": 1e-6,
        "init_params": "random_from_data",
    }
    grade = [
        (
            cfg := {
                "covariance_type": cov,
                "reg_covar": reg,
                "init_params": init_p,
            },
            cfg == ref,
        )
        for cov, reg, init_p in product(
            ["full", "tied", "diag", "spherical"],
            [1e-6, 1e-4, 1e-2],
            ["random_from_data", "kmeans"],
        )
    ]
    return _avaliar_particional_piloto(
        "gaussian-mixture", dados, y_true, grade, "maximizar"
    )


def tunar_upgma(dados: np.ndarray, y_true: np.ndarray):
    """Avalia os cortes da árvore única UPGMA (Manhattan / average linkage)."""
    resultados = upgma(dados, valores_k=(1, 2, 3, 4, 5))
    k_estrela, silhuetas = selecionar_k_por_silhueta(dados, resultados)
    linhas = [
        {
            "metric": "manhattan",
            "linkage": "average",
            "k": k,
            "silhueta": silhuetas[k],
            "ari": calcular_ari(y_true, resultados[k].rotulos),
            "selecionado": k == k_estrela,
        }
        for k in range(1, 6)
    ]
    df = pd.DataFrame(linhas)
    sil_media = float(np.mean([silhuetas[k] for k in range(2, 6)]))
    resumo_selecao = {
        "algoritmo": "upgma",
        "parametros": {},
        "k_estrela": int(k_estrela),
        "silhueta_media_k2_k5": sil_media,
        "silhueta_k2": float(silhuetas[2]),
        "silhueta_k3": float(silhuetas[3]),
        "ari_k2": float(calcular_ari(y_true, resultados[2].rotulos)),
        "ari_k3": float(calcular_ari(y_true, resultados[3].rotulos)),
    }
    return df, resumo_selecao


def tunar_dbscan(dados: np.ndarray, y_true: np.ndarray):
    """Busca piloto do DBSCAN exigindo >= 95% de cobertura (<= 5% de ruído)."""
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
        cobertura_pct = 100.0 - ruido_pct
        linhas.append(
            {
                "eps": float(eps),
                "min_samples": int(min_samples),
                "eh_referencia": bool(np.isclose(eps, 0.8) and min_samples == 5),
                "referencia_5_vizinhos": referencia,
                "grupos": grupos,
                "ruido": ruido,
                "ruido_pct": ruido_pct,
                "cobertura_pct": cobertura_pct,
                "silhueta": calcular_silhueta(dados, rotulos, ignorar_ruido=True),
                "ari": calcular_ari(y_true, rotulos, ignorar_ruido=True),
            }
        )

    df = pd.DataFrame(linhas)
    candidatos = df[(df["grupos"] >= 2) & (df["cobertura_pct"] >= 95.0)].dropna(
        subset=["silhueta"]
    )
    if candidatos.empty:
        candidatos = df[df["grupos"] >= 2].dropna(subset=["silhueta"])

    candidatos = candidatos.copy()
    candidatos["_sil_ord"] = candidatos["silhueta"].round(9)
    melhor_linha = candidatos.sort_values(
        by=["_sil_ord", "cobertura_pct", "eh_referencia"],
        ascending=[False, False, False],
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
        "cobertura_pct": float(melhor_linha["cobertura_pct"]),
        "silhueta": float(melhor_linha["silhueta"]),
        "ari": float(melhor_linha["ari"]),
    }
    return df, resumo_selecao


def _plotar_sensibilidade(
    df_kmeans: pd.DataFrame,
    df_fcm: pd.DataFrame,
    df_kfcm: pd.DataFrame,
    df_kfcm_detalhe: pd.DataFrame,
    df_kmedoids: pd.DataFrame,
    df_gmm: pd.DataFrame,
    df_upgma: pd.DataFrame,
    df_dbscan: pd.DataFrame,
    diretorio_figuras: Path,
) -> None:
    """Gera gráficos de comportamento paramétrico para cada um dos 7 algoritmos."""
    diretorio_figuras.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="notebook")

    # 1. K-Means
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
    sub_km = df_kmeans[df_kmeans["max_iter"] == 300].copy()
    sub_km["tol_str"] = sub_km["tol"].apply(lambda v: f"{v:.0e}")
    sns.barplot(
        data=sub_km, x="tol_str", y="silhueta_media_k2_k5", hue="init", ax=axes[0]
    )
    axes[0].set(
        title="K-Means: Silhueta média (k=2..5) por init e tol",
        xlabel="Tolerância (tol)",
        ylabel="Silhueta média (k=2..5)",
    )
    axes[0].set_ylim(0, 0.65)
    sns.barplot(data=sub_km, x="tol_str", y="ari_k3", hue="init", ax=axes[1])
    axes[1].set(
        title="K-Means: ARI (k=3) por init e tol",
        xlabel="Tolerância (tol)",
        ylabel="ARI (k=3)",
    )
    axes[1].set_ylim(0, 0.8)
    fig.tight_layout()
    fig.savefig(diretorio_figuras / "tunagem_k_means.png", dpi=150)
    plt.close(fig)

    # 2. Fuzzy K-Means
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
    sub_fcm = df_fcm[np.isclose(df_fcm["error"], 1e-5)]
    sns.lineplot(
        data=sub_fcm,
        x="m",
        y="silhueta_media_k2_k5",
        marker="o",
        label="Média (k=2..5)",
        ax=axes[0],
    )
    sns.lineplot(
        data=sub_fcm,
        x="m",
        y="silhueta_k3",
        marker="s",
        label="k = 3",
        ax=axes[0],
    )
    axes[0].set(
        title="Fuzzy K-Means: Silhueta × m", xlabel="Fuzzifier (m)", ylabel="Silhueta"
    )
    sns.lineplot(
        data=sub_fcm, x="m", y="ari_k2", marker="o", label="ARI (k=2)", ax=axes[1]
    )
    sns.lineplot(
        data=sub_fcm, x="m", y="ari_k3", marker="s", label="ARI (k=3)", ax=axes[1]
    )
    axes[1].set(
        title="Fuzzy K-Means: ARI × m", xlabel="Fuzzifier (m)", ylabel="ARI"
    )
    fig.tight_layout()
    fig.savefig(diretorio_figuras / "tunagem_fuzzy_k_means.png", dpi=150)
    plt.close(fig)

    # 3. Kernel Fuzzy K-Means (heatmap médio + efeito de gamma com m=2.0 e k fixos)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4))
    piv_sil = df_kfcm.pivot(index="m", columns="gamma", values="silhueta_media_k2_k5")
    sns.heatmap(piv_sil, annot=True, fmt=".4f", cmap="YlGnBu", ax=axes[0])
    axes[0].set(
        title="Kernel FCM: Silhueta média (k=2..5) por (m, gamma)",
        xlabel="gamma",
        ylabel="m",
    )
    sub_kfcm_m2 = df_kfcm_detalhe[np.isclose(df_kfcm_detalhe["m"], 2.0)]
    sns.lineplot(
        data=sub_kfcm_m2,
        x="gamma",
        y="silhueta",
        hue="k",
        marker="o",
        palette="deep",
        ax=axes[1],
    )
    axes[1].set(
        title="Kernel FCM: Efeito de gamma com m = 2,0 e k fixos",
        xlabel="gamma",
        ylabel="Silhueta",
    )
    fig.tight_layout()
    fig.savefig(diretorio_figuras / "tunagem_kernel_fuzzy_k_means.png", dpi=150)
    plt.close(fig)

    # 4. K-Medoids
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
    sub_kmed = df_kmedoids[df_kmedoids["max_iter"] == 300]
    sns.barplot(
        data=sub_kmed,
        x="init",
        y="silhueta_media_k2_k5",
        color="#2676a1",
        ax=axes[0],
    )
    axes[0].set(
        title="K-Medoids (Euclidiana): Silhueta média (k=2..5)",
        xlabel="Inicialização (init)",
        ylabel="Silhueta média (k=2..5)",
    )
    axes[0].set_ylim(0, 0.65)
    sns.barplot(
        data=sub_kmed, x="init", y="ari_k3", color="#e07a5f", ax=axes[1]
    )
    axes[1].set(
        title="K-Medoids (Euclidiana): ARI (k=3) por init",
        xlabel="Inicialização (init)",
        ylabel="ARI (k=3)",
    )
    axes[1].set_ylim(0, 0.85)
    fig.tight_layout()
    fig.savefig(diretorio_figuras / "tunagem_k_medoids.png", dpi=150)
    plt.close(fig)

    # 5. GMM / EM
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4))
    sub_gmm = df_gmm[df_gmm["init_params"] == "random_from_data"].copy()
    sub_gmm["reg_str"] = sub_gmm["reg_covar"].apply(lambda v: f"{v:.0e}")
    sns.barplot(
        data=sub_gmm,
        x="covariance_type",
        y="silhueta_media_k2_k5",
        hue="reg_str",
        ax=axes[0],
    )
    axes[0].set(
        title="GMM/EM: Silhueta média (k=2..5) por covariância",
        xlabel="Tipo de covariância",
        ylabel="Silhueta média (k=2..5)",
    )
    axes[0].set_ylim(0, 0.65)
    sns.barplot(
        data=sub_gmm,
        x="covariance_type",
        y="ari_k3",
        hue="reg_str",
        ax=axes[1],
    )
    axes[1].set(
        title="GMM/EM: ARI (k=3) por covariância e reg_covar",
        xlabel="Tipo de covariância",
        ylabel="ARI (k=3)",
    )
    axes[1].set_ylim(0, 1.0)
    fig.tight_layout()
    fig.savefig(diretorio_figuras / "tunagem_gaussian_mixture.png", dpi=150)
    plt.close(fig)

    # 6. UPGMA (cortes da árvore única)
    fig, ax = plt.subplots(figsize=(8.0, 4.3))
    sub_upgma = df_upgma[df_upgma["k"] >= 2].melt(
        id_vars="k",
        value_vars=["silhueta", "ari"],
        var_name="Métrica",
        value_name="Valor",
    )
    sns.barplot(
        data=sub_upgma,
        x="k",
        y="Valor",
        hue="Métrica",
        palette=["#2676a1", "#e07a5f"],
        ax=ax,
    )
    ax.set(
        title="UPGMA (Manhattan / average): comparação dos cortes k = 2..5",
        xlabel="Número de grupos no corte (k)",
        ylabel="Pontuação",
    )
    ax.set_ylim(0, 0.85)
    fig.tight_layout()
    fig.savefig(diretorio_figuras / "tunagem_upgma.png", dpi=150)
    plt.close(fig)

    # 7. DBSCAN
    fig, axes = plt.subplots(1, 3, figsize=(14.5, 4.3))
    sns.lineplot(
        data=df_dbscan,
        x="eps",
        y="silhueta",
        hue="min_samples",
        marker="o",
        palette="viridis",
        ax=axes[0],
    )
    axes[0].set(
        title="DBSCAN: Silhueta (sem ruído) × eps", xlabel="eps", ylabel="Silhueta"
    )
    sns.lineplot(
        data=df_dbscan,
        x="eps",
        y="ari",
        hue="min_samples",
        marker="o",
        palette="viridis",
        ax=axes[1],
    )
    axes[1].set(title="DBSCAN: ARI (sem ruído) × eps", xlabel="eps", ylabel="ARI")
    sns.lineplot(
        data=df_dbscan,
        x="eps",
        y="cobertura_pct",
        hue="min_samples",
        marker="o",
        palette="viridis",
        ax=axes[2],
    )
    axes[2].axhline(95.0, color="#c43c39", linestyle="--", label="Cobertura 95%")
    axes[2].set(
        title="DBSCAN: Cobertura (%) × eps", xlabel="eps", ylabel="Cobertura (%)"
    )
    fig.tight_layout()
    fig.savefig(diretorio_figuras / "tunagem_dbscan.png", dpi=150)
    plt.close(fig)


def executar_tunagem_completa(
    dados: np.ndarray,
    y_true: np.ndarray,
    diretorio_saida: Path = DIRETORIO_SAIDA,
    diretorio_figuras: Path = DIRETORIO_FIGURAS,
) -> dict[str, dict[str, Any]]:
    """Executa a rodada piloto (seeds 0..9), salva CSVs e figuras e retorna os ótimos."""
    diretorio_saida.mkdir(parents=True, exist_ok=True)
    diretorio_figuras.mkdir(parents=True, exist_ok=True)

    print("Executando rodada piloto de hiperparâmetros (seeds 0..9)...")
    df_km, det_km, sel_km = tunar_kmeans(dados, y_true)
    df_fcm, det_fcm, sel_fcm = tunar_fuzzy_kmeans(dados, y_true)
    df_kfcm, det_kfcm, sel_kfcm = tunar_kernel_fuzzy_kmeans(dados, y_true)
    df_kmed, det_kmed, sel_kmed = tunar_kmedoids(dados, y_true)
    df_gmm, det_gmm, sel_gmm = tunar_gaussian_mixture(dados, y_true)
    df_upgma, sel_upgma = tunar_upgma(dados, y_true)
    df_db, sel_db = tunar_dbscan(dados, y_true)

    df_particionais = pd.concat(
        [det_km, det_fcm, det_kfcm, det_kmed, det_gmm], ignore_index=True
    )
    df_particionais.to_csv(
        diretorio_saida / "particionais.csv", index=False, encoding="utf-8"
    )

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
        df_km,
        df_fcm,
        df_kfcm,
        det_kfcm,
        df_kmed,
        df_gmm,
        df_upgma,
        df_db,
        diretorio_figuras,
    )
    print(f"Rodada piloto concluída e salva em: {diretorio_saida}")
    return selecoes


def main() -> None:
    dados, y_true, _ = carregar_iris(padronizar=True)
    executar_tunagem_completa(dados, y_true)


if __name__ == "__main__":
    with threadpool_limits(limits=1):
        main()