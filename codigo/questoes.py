"""Execução completa das Questões 1 e 2 do projeto AM-NS."""

import hashlib
import importlib.metadata
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA, KernelPCA
from sklearn.manifold import TSNE, trustworthiness
from threadpoolctl import threadpool_limits
from tunagem import (
    PADRAO_DBSCAN,
    buscar_hiperparametros,
    comparar_amostra_dbscan,
    salvar_busca,
)
from umap import UMAP

from algoritmos import (
    ResultadoAgrupamento,
    calcular_ari,
    carregar_iris,
    condensar_resultados,
    dbscan,
    executar_todas_por_k,
    plotar_dendrograma,
    plotar_silhuetas,
    plt,
    salvar_json,
    selecionar_k_por_silhueta,
    selecionar_melhores_por_k,
    sns,
    upgma,
)

ROOT = Path(__file__).resolve().parent.parent
CODIGO = Path(__file__).resolve().parent
SEMENTES_OFICIAIS = range(52, 62)


def executar_questao_1(
    padronizar: bool = True,
    eps_dbscan: float | None = None,
    min_samples_dbscan: int | None = None,
    *,
    diretorio_resultados: str | Path = ROOT / "resultados",
) -> pd.DataFrame:
    """Executa a busca piloto e a rodada oficial de agrupamentos da Questão 1."""
    diretorio_resultados = Path(diretorio_resultados)
    diretorio_tunagem = diretorio_resultados / "tunagem"
    diretorio_figuras = diretorio_resultados / "figuras"
    X, y, preprocessamento = carregar_iris(padronizar=padronizar)
    valores_k = range(1, 6)
    parametros_dbscan = None
    if eps_dbscan is not None or min_samples_dbscan is not None:
        parametros_dbscan = (
            PADRAO_DBSCAN[0] if eps_dbscan is None else eps_dbscan,
            PADRAO_DBSCAN[1] if min_samples_dbscan is None else min_samples_dbscan,
        )
    print("Rodada piloto (k de 2 a 5)...")
    busca = buscar_hiperparametros(X, parametros_dbscan)

    todas_execucoes: dict[str, Any] = {}
    melhores: dict[str, dict[int, ResultadoAgrupamento]] = {}
    ajustes_particionais = 0
    print("Rodada oficial (k de 1 a 5, sementes 52–61)...")
    with threadpool_limits(limits=1):
        for nome, escolha in busca.metadados["selecionados"].items():
            parametros = escolha["parametros"]
            print(f"Executando {nome} com {parametros}...")
            execucoes = executar_todas_por_k(
                nome, X, valores_k, seed_inicial=SEMENTES_OFICIAIS.start, **parametros
            )
            ajustes_particionais += sum(len(rodadas) for rodadas in execucoes.values())
            todas_execucoes[nome] = execucoes
            melhores[nome] = selecionar_melhores_por_k(nome, execucoes)

        print("Executando upgma (uma hierarquia e cinco cortes)...")
        resultados_upgma = upgma(X, valores_k=tuple(valores_k))
        melhores["upgma"] = resultados_upgma
        todas_execucoes["upgma"] = resultados_upgma

        escolha_dbscan = busca.metadados["dbscan"]
        print(
            f"Executando dbscan com eps={escolha_dbscan['eps']:.9g} "
            f"e min_samples={escolha_dbscan['min_samples']}..."
        )
        resultado_dbscan = dbscan(
            X, eps=escolha_dbscan["eps"], min_samples=escolha_dbscan["min_samples"]
        )
    todas_execucoes["dbscan"] = resultado_dbscan

    plotar_dendrograma(resultados_upgma[2], diretorio_figuras)

    resumo = condensar_resultados(X, y, melhores, resultado_dbscan)
    diretorio_resultados.mkdir(parents=True, exist_ok=True)
    linhas = []
    contingencias = {}
    selecionados = {}
    for nome, resultados in melhores.items():
        k_estrela, silhuetas = selecionar_k_por_silhueta(X, resultados)
        plotar_silhuetas(nome, silhuetas, k_estrela, diretorio_figuras)
        selecionados[nome] = resultados[k_estrela]
        contingencias[nome] = pd.crosstab(
            pd.Series(y, name="especie"),
            pd.Series(selecionados[nome].rotulos, name="grupo"),
        ).to_dict()
        for k in valores_k:
            resultado = resultados.get(k)
            linhas.append(
                {
                    "algoritmo": nome,
                    "k": k,
                    "seed": resultado.parametros.get("seed") if resultado else None,
                    "objetivo": resultado.objetivo if resultado else None,
                    "silhueta": silhuetas.get(k),
                    "ari": calcular_ari(y, resultado.rotulos) if resultado else None,
                    "selecionado": k == k_estrela,
                }
            )
    contingencias["dbscan"] = pd.crosstab(
        pd.Series(y), pd.Series(resultado_dbscan.rotulos)
    ).to_dict()
    salvar_json(diretorio_resultados / "contingencias.json", contingencias)
    pd.DataFrame(linhas).to_csv(
        diretorio_resultados / "metricas_por_k.csv", index=False
    )
    resumo.to_csv(diretorio_resultados / "resumo_agrupamentos.csv", index=False)
    salvar_json(diretorio_resultados / "execucoes_questao_1.json", todas_execucoes)
    salvar_busca(busca, y, diretorio_tunagem)
    comparar_amostra_dbscan(X, y, selecionados, resultado_dbscan).to_csv(
        diretorio_tunagem / "comparacao_mesma_amostra.csv", index=False
    )
    rodada_oficial = {
        "sementes": list(SEMENTES_OFICIAIS),
        "ajustes_particionais": ajustes_particionais,
        "ajustes_upgma": 1,
        "ajustes_dbscan": 1,
        "ajustes_totais": ajustes_particionais + 2,
        "criterio_k": "Maior silhueta válida, com empate pelo menor k.",
    }
    salvar_json(
        diretorio_resultados / "metadados_questao_1.json",
        {
            "base": "codigo/iris/iris.data (UCI Iris)",
            "preprocessamento": preprocessamento,
            "valores_k": list(valores_k),
            "execucoes_por_algoritmo_particional": len(SEMENTES_OFICIAIS),
            "silhueta": {"metrica": "euclidean", "k_1": "indefinida (NaN)"},
            "dbscan": {
                "eps": resultado_dbscan.parametros["eps"],
                "min_samples": resultado_dbscan.parametros["min_samples"],
                "silhueta": "pontos de ruído (-1) removidos",
                "ari": "pontos de ruído (-1) removidos",
            },
            "rodada_oficial": rodada_oficial,
            "tunagem": busca.metadados
            | {
                "ajustes_totais": (
                    busca.metadados["ajustes_particionais"]
                    + busca.metadados["ajustes_dbscan"]
                    + rodada_oficial["ajustes_totais"]
                ),
            },
            "versoes": {
                "python": sys.version,
                **{
                    pacote: importlib.metadata.version(pacote)
                    for pacote in [
                        "numpy",
                        "pandas",
                        "scikit-learn",
                        "scipy",
                        "matplotlib",
                        "seaborn",
                        "pydantic",
                        "fuzzy-c-means",
                        "kmedoids",
                    ]
                },
            },
        },
    )
    print("\nResumo dos agrupamentos:")
    print(resumo.to_string(index=False, float_format=lambda valor: f"{valor:.4f}"))
    print(f"\nResultados salvos em: {diretorio_resultados}")
    return resumo


def executar_questao_2(
    padronizar: bool = True,
    seed: int = 42,
    gamma: float = 0.25,
    perplexidade: float = 30.0,
    vizinhos: int = 15,
    min_dist: float = 0.1,
) -> dict[str, Any]:
    """Executa PCA, Kernel PCA, t-SNE e UMAP da Questão 2."""
    diretorio_resultados = ROOT / "resultados"
    diretorio_figuras = ROOT / "resultados" / "figuras"
    diretorio_resultados.mkdir(exist_ok=True)
    diretorio_figuras.mkdir(exist_ok=True)
    X, y, prep = carregar_iris(padronizar=padronizar)
    modelos = {
        "pca": PCA(n_components=4, svd_solver="full"),
        "kernel_pca": KernelPCA(
            n_components=2, kernel="rbf", gamma=gamma, eigen_solver="dense"
        ),
        "tsne": TSNE(
            n_components=2,
            perplexity=perplexidade,
            learning_rate="auto",
            init="pca",
            max_iter=1000,
            random_state=seed,
        ),
        "umap": UMAP(
            n_components=2,
            n_neighbors=vizinhos,
            min_dist=min_dist,
            metric="euclidean",
            random_state=seed,
            n_jobs=1,
        ),
    }
    resultados = {}
    for nome, modelo in modelos.items():
        print(f"Executando {nome}...", flush=True)
        Z = modelo.fit_transform(X)
        tabela = pd.DataFrame(
            Z, columns=[f"componente_{i+1}" for i in range(Z.shape[1])]
        )
        tabela.insert(0, "observacao", np.arange(1, len(X) + 1))
        tabela["especie"] = y
        tabela.to_csv(diretorio_resultados / f"coordenadas_{nome}.csv", index=False)
        resultado = {
            "parametros": modelo.get_params(),
            "coordenadas": Z,
            "trustworthiness_10": trustworthiness(X, Z[:, :2], n_neighbors=10),
        }
        if nome == "pca":
            resultado.update(
                componentes=modelo.components_,
                autovalores=modelo.explained_variance_,
                variancia_explicada=modelo.explained_variance_ratio_,
                variancia_acumulada=np.cumsum(modelo.explained_variance_ratio_),
                valores_singulares=modelo.singular_values_,
                media=modelo.mean_,
                loadings=modelo.components_.T * np.sqrt(modelo.explained_variance_),
                convencao_loadings="autovetores multiplicados pela raiz do autovalor",
            )
            pd.DataFrame(
                modelo.components_.T,
                index=prep["atributos"],
                columns=["PC1", "PC2", "PC3", "PC4"],
            ).to_csv(diretorio_resultados / "pca_componentes.csv")
            pd.DataFrame(
                resultado["loadings"],
                index=prep["atributos"],
                columns=["PC1", "PC2", "PC3", "PC4"],
            ).to_csv(diretorio_resultados / "pca_loadings.csv")
        elif nome == "kernel_pca":
            resultado.update(
                autovalores=modelo.eigenvalues_, autovetores=modelo.eigenvectors_
            )
        elif nome == "tsne":
            resultado.update(
                divergencia_kl=modelo.kl_divergence_,
                iteracoes=modelo.n_iter_,
                taxa_aprendizado_efetiva=modelo.learning_rate_,
            )
        resultados[nome] = resultado
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.scatterplot(x=Z[:, 0], y=Z[:, 1], hue=y, style=y, s=48, ax=ax)
        ax.set(
            title=(
                nome.upper().replace("_", " ") + " — Iris padronizada"
                if padronizar
                else nome.upper()
            ),
            xlabel="Componente 1",
            ylabel="Componente 2",
        )
        if nome == "pca":
            ax.set_xlabel(f"PC1 ({modelo.explained_variance_ratio_[0]:.2%})")
            ax.set_ylabel(f"PC2 ({modelo.explained_variance_ratio_[1]:.2%})")
        ax.legend(title="Espécie", fontsize=8)
        fig.tight_layout()
        fig.savefig(diretorio_figuras / f"{nome}.png", dpi=170)
        plt.close(fig)
    salvar_json(diretorio_resultados / "execucoes_questao_2.json", resultados)
    salvar_json(
        diretorio_resultados / "metadados_questao_2.json",
        {
            "preprocessamento": prep,
            "seed": seed,
            "python": sys.version,
            "fonte_requisitos": "Projeto-AMG-NS-2026-2.pdf; Equipe 08",
            "sha256_dados": hashlib.sha256(
                (CODIGO / "iris/iris.data").read_bytes()
            ).hexdigest(),
            "versoes": {
                pacote: importlib.metadata.version(pacote)
                for pacote in [
                    "numpy",
                    "pandas",
                    "scikit-learn",
                    "scipy",
                    "umap-learn",
                    "numba",
                    "matplotlib",
                ]
            },
        },
    )
    return resultados
