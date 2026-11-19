"""Algoritmos, métricas e persistência usados nos experimentos da base Iris."""

import json
from pathlib import Path
from typing import Any, Literal

import matplotlib
import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from fcmeans import FCM, KFCM
from kmedoids import pam
from scipy.cluster.hierarchy import cut_tree, dendrogram, linkage
from scipy.spatial.distance import cdist, pdist
from sklearn.cluster import DBSCAN, KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler


class ResultadoAgrupamento(BaseModel):
    """Representa o resultado de um algoritmo de agrupamento."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    algoritmo: str
    tipo: Literal["crisp", "fuzzy", "probabilistico", "hierarquico", "densidade"]
    rotulos: np.ndarray
    objetivo: float | None = None
    parametros: dict[str, Any] = Field(default_factory=dict)
    centros: np.ndarray | None = None
    pertinencias: np.ndarray | None = None  # Fuzzy K-Means
    probabilidades: np.ndarray | None = None  # GMM/EM
    hierarquia: np.ndarray | None = None  # Matriz de ligações para o dendrograma
    ruido: int = 0


experimental_algorithms: dict[str, dict[str, Any]] = {}
CAMINHO_IRIS_PADRAO = Path(__file__).with_name("iris") / "iris.data"


def algoritmo(
    nome: str,
    execucoes: int = 10,
    objetivo: Literal["minimizar", "maximizar"] = "minimizar",
):
    """Registra uma função de agrupamento para execução pelo seu nome."""

    def decorator(func):
        experimental_algorithms[nome] = {
            "funcao": func,
            "execucoes": execucoes,
            "objetivo": objetivo,
        }
        return func

    return decorator


def executar_algoritmo(nome: str, *args: Any, **kwargs: Any) -> Any:
    """Executa o algoritmo registrado em ``nome``."""
    try:
        funcao = experimental_algorithms[nome]["funcao"]
    except KeyError as erro:
        raise ValueError(f"Algoritmo desconhecido: {nome}") from erro
    return funcao(*args, **kwargs)


def executar_melhores_por_k(
    nome: str,
    data: np.ndarray,
    valores_k: range = range(1, 6),
    seed_inicial: int = 42,
    **kwargs: Any,
) -> dict[int, ResultadoAgrupamento]:
    """Executa um algoritmo particional e retém o melhor resultado de cada ``k``."""
    todas_execucoes = executar_todas_por_k(
        nome, data, valores_k, seed_inicial, **kwargs
    )
    return selecionar_melhores_por_k(nome, todas_execucoes)


def executar_todas_por_k(
    nome: str,
    data: np.ndarray,
    valores_k: range = range(1, 6),
    seed_inicial: int = 42,
    **kwargs: Any,
) -> dict[int, list[ResultadoAgrupamento]]:
    """Executa e mantém todas as dez inicializações de cada ``k``."""
    try:
        quantidade_execucoes = experimental_algorithms[nome]["execucoes"]
    except KeyError as erro:
        raise ValueError(f"Algoritmo desconhecido: {nome}") from erro
    if quantidade_execucoes <= 1:
        raise ValueError(f"{nome} não é um algoritmo particional com reinicializações.")

    return {
        k: [
            executar_algoritmo(
                nome, data, k=k, seed=seed_inicial + tentativa, **kwargs
            )
            for tentativa in range(quantidade_execucoes)
        ]
        for k in valores_k
    }


def selecionar_melhores_por_k(
    nome: str,
    todas_execucoes: dict[int, list[ResultadoAgrupamento]],
) -> dict[int, ResultadoAgrupamento]:
    """Seleciona a melhor inicialização de cada ``k`` pela função objetivo."""
    try:
        registro = experimental_algorithms[nome]
    except KeyError as erro:
        raise ValueError(f"Algoritmo desconhecido: {nome}") from erro

    seletor = max if registro["objetivo"] == "maximizar" else min
    melhores: dict[int, ResultadoAgrupamento] = {}
    for k, resultados in todas_execucoes.items():
        if not resultados or any(resultado.objetivo is None for resultado in resultados):
            raise ValueError(f"{nome} não fornece função objetivo para seleção.")
        melhores[k] = seletor(resultados, key=lambda resultado: resultado.objetivo)
    return melhores


def calcular_silhueta(
    data: np.ndarray,
    rotulos: np.ndarray,
    ignorar_ruido: bool = False,
) -> float:
    """Calcula a silhueta média de uma partição crisp.

    Retorna ``np.nan`` quando a métrica não é definida (como k = 1).
    Para DBSCAN, use ``ignorar_ruido=True`` para excluir pontos ``-1``.
    """
    X = np.asarray(data, dtype=float)
    labels = np.asarray(rotulos)

    if X.ndim != 2 or X.shape[0] == 0 or X.shape[1] == 0:
        raise ValueError("data deve ser uma matriz bidimensional não vazia.")
    if not np.isfinite(X).all():
        raise ValueError("data não pode conter NaN ou valores infinitos.")
    if labels.ndim != 1 or len(labels) != len(X):
        raise ValueError("rotulos deve ter um rótulo para cada amostra de data.")

    if ignorar_ruido:
        mascara = labels != -1
        X, labels = X[mascara], labels[mascara]

    quantidade_clusters = len(np.unique(labels))
    if len(X) < 2 or quantidade_clusters < 2 or quantidade_clusters >= len(X):
        return float("nan")

    return float(silhouette_score(X, labels, metric="euclidean"))


def selecionar_k_por_silhueta(
    data: np.ndarray,
    resultados: dict[int, ResultadoAgrupamento],
) -> tuple[int, dict[int, float]]:
    """Calcula Sil(k) para k em {2..5} (k=1 indefinido) e retorna k*."""
    silhuetas = {
        k: calcular_silhueta(data, resultado.rotulos)
        for k, resultado in resultados.items()
    }
    valores_validos = {k: sil for k, sil in silhuetas.items() if not np.isnan(sil)}
    if not valores_validos:
        raise ValueError("Nenhuma partição possui silhueta definida.")

    k_estrela = max(valores_validos, key=valores_validos.get)
    return k_estrela, silhuetas


def calcular_ari(
    rotulos_verdadeiros: np.ndarray,
    rotulos_preditos: np.ndarray,
    ignorar_ruido: bool = False,
) -> float:
    """Calcula o Índice de Rand Ajustado (ARI) entre espécies e clusters.

    Para DBSCAN, use ``ignorar_ruido=True`` para excluir os pontos com rótulo
    ``-1`` antes do cálculo.
    """
    y_true = np.asarray(rotulos_verdadeiros)
    y_pred = np.asarray(rotulos_preditos)
    if y_true.ndim != 1 or y_pred.ndim != 1 or len(y_true) != len(y_pred):
        raise ValueError(
            "Os dois vetores de rótulos devem ser unidimensionais e ter o mesmo tamanho."
        )
    if ignorar_ruido:
        mascara = y_pred != -1
        y_true, y_pred = y_true[mascara], y_pred[mascara]
    if len(y_true) == 0:
        return float("nan")
    return float(adjusted_rand_score(y_true, y_pred))


def condensar_resultados(
    data: np.ndarray,
    rotulos_verdadeiros: np.ndarray,
    resultados_por_algoritmo: dict[str, dict[int, ResultadoAgrupamento]],
    resultado_dbscan: ResultadoAgrupamento | None = None,
) -> pd.DataFrame:
    """Cria a tabela comparativa dos resultados selecionados dos 7 algoritmos."""
    linhas: list[dict[str, Any]] = []
    for nome, resultados in resultados_por_algoritmo.items():
        k_estrela, silhuetas = selecionar_k_por_silhueta(data, resultados)
        resultado = resultados[k_estrela]
        linhas.append(
            {
                "Algoritmo": nome,
                "k*": k_estrela,
                "Silhueta": silhuetas[k_estrela],
                "ARI": calcular_ari(rotulos_verdadeiros, resultado.rotulos),
                "Clusters": len(np.unique(resultado.rotulos)),
                "Ruído": 0,
                "Ruído (%)": 0.0,
            }
        )

    if resultado_dbscan is not None:
        rotulos = resultado_dbscan.rotulos
        quantidade_clusters = len(set(rotulos) - {-1})
        quantidade_ruido = int(np.sum(rotulos == -1))
        linhas.append(
            {
                "Algoritmo": "dbscan",
                "k*": "automático",
                "Silhueta": calcular_silhueta(data, rotulos, ignorar_ruido=True),
                "ARI": calcular_ari(rotulos_verdadeiros, rotulos, ignorar_ruido=True),
                "Clusters": quantidade_clusters,
                "Ruído": quantidade_ruido,
                "Ruído (%)": 100 * quantidade_ruido / len(rotulos),
            }
        )

    return pd.DataFrame(linhas)


def plotar_silhuetas(
    nome_algoritmo: str,
    silhuetas: dict[int, float],
    k_estrela: int,
    diretorio_saida: str | Path = "figuras",
) -> Path:
    """Salva o gráfico Sil × k (k=1 marcado como indefinido)."""
    diretorio = Path(diretorio_saida)
    diretorio.mkdir(parents=True, exist_ok=True)

    ks = sorted(silhuetas)
    ks_validos = [k for k in ks if not np.isnan(silhuetas[k])]
    valores_validos = [silhuetas[k] for k in ks_validos]

    sns.set_theme(style="whitegrid", context="notebook")
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sns.lineplot(
        x=ks_validos,
        y=valores_validos,
        marker="o",
        linewidth=2,
        color="#2676a1",
        ax=ax,
    )
    ax.axvline(k_estrela, color="#c43c39", linestyle="--", label=f"k* = {k_estrela}")
    ax.scatter(k_estrela, silhuetas[k_estrela], color="#c43c39", s=70, zorder=3)

    for k in ks:
        if np.isnan(silhuetas[k]):
            ax.annotate(
                "indefinida",
                xy=(k, min(valores_validos)),
                xytext=(0, 8),
                textcoords="offset points",
                ha="center",
                color="#666666",
                fontsize=9,
            )

    ax.set(
        title=f"Silhueta × k — {nome_algoritmo}",
        xlabel="Número de clusters (k)",
        ylabel="Silhueta média",
        xticks=ks,
    )
    ax.legend()
    fig.tight_layout()

    nome_arquivo = f"silhueta_{nome_algoritmo.lower().replace(' ', '_').replace('-', '_')}.png"
    caminho_saida = diretorio / nome_arquivo
    fig.savefig(caminho_saida, dpi=150)
    plt.close(fig)
    return caminho_saida


def plotar_comparacao_algoritmos(
    resumo: pd.DataFrame,
    metricas_por_k: pd.DataFrame,
    diretorio_saida: str | Path = "figuras",
) -> Path:
    """Gera gráfico comparativo de Silhueta e ARI entre os 7 algoritmos."""
    diretorio = Path(diretorio_saida)
    diretorio.mkdir(parents=True, exist_ok=True)

    rotulos_legiveis = {
        "k-means": "K-Means",
        "fuzzy-k-means": "Fuzzy K-Means",
        "kernel-fuzzy-k-means": "Kernel FCM",
        "k-medoids": "K-Medoids",
        "gaussian-mixture": "GMM/EM",
        "upgma": "UPGMA",
        "dbscan": "DBSCAN",
    }

    sns.set_theme(style="whitegrid", context="notebook")
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.2), sharey=True)

    df_k_star = resumo.copy()
    df_k_star["Método"] = df_k_star["Algoritmo"].map(rotulos_legiveis)
    melt_star = df_k_star.melt(
        id_vars="Método",
        value_vars=["Silhueta", "ARI"],
        var_name="Métrica",
        value_name="Valor",
    )
    sns.barplot(
        data=melt_star,
        x="Método",
        y="Valor",
        hue="Métrica",
        palette=["#2676a1", "#e07a5f"],
        ax=axes[0],
    )
    axes[0].set_title("Desempenho em k* (selecionado pela Silhueta)")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Pontuação")
    axes[0].set_ylim(0, 1.05)
    axes[0].tick_params(axis="x", rotation=25)
    for container in axes[0].containers:
        axes[0].bar_label(container, fmt="%.2f", fontsize=8, padding=2)

    df_k3 = metricas_por_k[metricas_por_k["k"] == 3][
        ["algoritmo", "silhueta", "ari"]
    ].rename(columns={"algoritmo": "Algoritmo", "silhueta": "Silhueta", "ari": "ARI"})
    df_db = resumo[resumo["Algoritmo"] == "dbscan"][["Algoritmo", "Silhueta", "ARI"]]
    df_comp_k3 = pd.concat([df_k3, df_db], ignore_index=True)
    df_comp_k3["Método"] = df_comp_k3["Algoritmo"].map(rotulos_legiveis)
    melt_k3 = df_comp_k3.melt(
        id_vars="Método",
        value_vars=["Silhueta", "ARI"],
        var_name="Métrica",
        value_name="Valor",
    )
    sns.barplot(
        data=melt_k3,
        x="Método",
        y="Valor",
        hue="Métrica",
        palette=["#2676a1", "#e07a5f"],
        ax=axes[1],
    )
    axes[1].set_title("Desempenho em k = 3 (espécies reais) vs. DBSCAN")
    axes[1].set_xlabel("")
    axes[1].tick_params(axis="x", rotation=25)
    for container in axes[1].containers:
        axes[1].bar_label(container, fmt="%.2f", fontsize=8, padding=2)

    fig.tight_layout()
    caminho_saida = diretorio / "comparacao_algoritmos.png"
    fig.savefig(caminho_saida, dpi=160)
    plt.close(fig)
    return caminho_saida


def carregar_iris(
    caminho: str | Path | None = None,
    padronizar: bool = True,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """Carrega a Iris local, separa ``X`` e ``y`` e opcionalmente padroniza X."""
    caminho = CAMINHO_IRIS_PADRAO if caminho is None else Path(caminho)
    colunas = ["sepal_length", "sepal_width", "petal_length", "petal_width", "species"]
    dados = pd.read_csv(caminho, header=None, names=colunas).dropna(how="all")
    if dados.shape[0] != 150:
        raise ValueError(
            f"A base Iris deve conter 150 observações; foram lidas {dados.shape[0]}."
        )

    X = dados[colunas[:-1]].to_numpy(dtype=float)
    y = dados["species"].to_numpy()
    configuracao: dict[str, Any] = {
        "padronizado": padronizar,
        "atributos": colunas[:-1],
    }
    if padronizar:
        scaler = StandardScaler()
        X = scaler.fit_transform(X)
        configuracao["media_original"] = scaler.mean_.tolist()
        configuracao["escala_original"] = scaler.scale_.tolist()
    return X, y, configuracao


def plotar_dendrograma(
    resultado_upgma: ResultadoAgrupamento,
    diretorio_saida: str | Path = "figuras",
) -> Path:
    """Salva o dendrograma UPGMA Manhattan com estilo visual do Seaborn."""
    if resultado_upgma.hierarquia is None:
        raise ValueError("O resultado não contém uma matriz de ligações hierárquicas.")
    diretorio = Path(diretorio_saida)
    diretorio.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="notebook")
    fig, ax = plt.subplots(figsize=(12, 5))
    dendrogram(resultado_upgma.hierarquia, no_labels=True, ax=ax, color_threshold=0)
    ax.set(
        title="Dendrograma — UPGMA (Manhattan / city-block)",
        xlabel="Observações",
        ylabel="Distância",
    )
    fig.tight_layout()
    caminho_saida = diretorio / "dendrograma_upgma.png"
    fig.savefig(caminho_saida, dpi=150)
    plt.close(fig)
    return caminho_saida


def _para_json(valor: Any) -> Any:
    """Converte arrays e escalares NumPy em valores serializáveis em JSON."""
    if isinstance(valor, BaseModel):
        return _para_json(valor.model_dump())
    if isinstance(valor, np.ndarray):
        return _para_json(valor.tolist())
    if isinstance(valor, np.generic):
        return _para_json(valor.item())
    if isinstance(valor, dict):
        return {str(chave): _para_json(item) for chave, item in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [_para_json(item) for item in valor]
    if isinstance(valor, float) and not np.isfinite(valor):
        return None
    return valor


def salvar_json(caminho: str | Path, conteudo: Any) -> Path:
    """Persiste resultados estruturados de forma legível e reprodutível."""
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", encoding="utf-8") as arquivo:
        json.dump(
            _para_json(conteudo), arquivo, ensure_ascii=False, indent=2, allow_nan=False
        )
    return destino


def _validar_entrada(data: np.ndarray, k: int) -> np.ndarray:
    """Converte os dados para matriz numérica e valida ``k``."""
    X = np.asarray(data, dtype=float)
    if X.ndim != 2 or X.shape[0] == 0 or X.shape[1] == 0:
        raise ValueError("data deve ser uma matriz bidimensional não vazia.")
    if not np.isfinite(X).all():
        raise ValueError("data não pode conter NaN ou valores infinitos.")
    if not isinstance(k, (int, np.integer)) or not 1 <= k <= X.shape[0]:
        raise ValueError("k deve ser um inteiro entre 1 e o número de amostras.")
    return X


@algoritmo("k-means")
def k_means(
    data: np.ndarray,
    k: int,
    seed: int,
    init: str = "k-means++",
    tol: float = 1e-4,
    max_iter: int = 300,
) -> ResultadoAgrupamento:
    """Agrupa os dados com K-Means e retorna os rótulos e centros encontrados."""
    X = _validar_entrada(data, k)
    modelo = KMeans(
        n_clusters=k,
        n_init=1,
        init=init,
        tol=tol,
        max_iter=max_iter,
        random_state=seed,
    ).fit(X)
    return ResultadoAgrupamento(
        algoritmo="k-means",
        tipo="crisp",
        rotulos=modelo.labels_.copy(),
        objetivo=float(modelo.inertia_),
        parametros={
            "k": k,
            "seed": seed,
            "n_init": 1,
            "init": init,
            "tol": tol,
            "max_iter": max_iter,
            "n_iter": int(modelo.n_iter_),
        },
        centros=modelo.cluster_centers_.copy(),
    )


def _executar_fuzzy(
    data: np.ndarray,
    k: int,
    seed: int,
    m: float = 2.0,
    max_iter: int = 300,
    error: float = 1e-5,
    gamma: float | None = None,
) -> ResultadoAgrupamento:
    """Compartilha ajuste e conversão crisp dos dois métodos fuzzy."""
    X = _validar_entrada(data, k)
    parametros: dict[str, Any] = {
        "k": k,
        "seed": seed,
        "m": float(m),
        "max_iter": int(max_iter),
        "error": float(error),
    }
    opcoes = dict(
        n_clusters=k,
        m=float(m),
        max_iter=int(max_iter),
        error=float(error),
        random_state=seed,
    )
    modelo = FCM(**opcoes) if gamma is None else KFCM(**opcoes, gamma=float(gamma))
    modelo.fit(X)
    centros, pertinencias = modelo.centers.copy(), modelo.u.copy()
    distancias = np.sum((X[:, None, :] - centros[None, :, :]) ** 2, axis=2)
    nome = "fuzzy-k-means"
    if gamma is not None:
        nome = "kernel-fuzzy-k-means"
        parametros.update(gamma=float(modelo.gamma_), kernel="rbf")
        distancias = 2 * (1 - np.exp(-parametros["gamma"] * distancias))
    return ResultadoAgrupamento(
        algoritmo=nome,
        tipo="fuzzy",
        rotulos=np.argmax(pertinencias, axis=1),
        objetivo=float(np.sum((pertinencias ** float(m)) * distancias)),
        parametros=parametros,
        centros=centros,
        pertinencias=pertinencias,
    )


@algoritmo("fuzzy-k-means")
def fuzzy_k_means(
    data: np.ndarray,
    k: int,
    seed: int,
    m: float = 2.0,
    max_iter: int = 300,
    error: float = 1e-5,
) -> ResultadoAgrupamento:
    """Executa uma inicialização do Fuzzy C-Means."""
    return _executar_fuzzy(data, k, seed, m=m, max_iter=max_iter, error=error)


@algoritmo("kernel-fuzzy-k-means")
def kernel_fuzzy_k_means(
    data: np.ndarray,
    k: int,
    seed: int,
    gamma: float = 0.25,
    m: float = 2.0,
    max_iter: int = 300,
    error: float = 1e-5,
) -> ResultadoAgrupamento:
    """Executa uma inicialização do Kernel Fuzzy C-Means com kernel RBF."""
    return _executar_fuzzy(
        data, k, seed, m=m, max_iter=max_iter, error=error, gamma=gamma
    )


@algoritmo("k-medoids")
def kmedoids(
    data: np.ndarray,
    k: int,
    seed: int,
    init: str = "random",
    max_iter: int = 300,
) -> ResultadoAgrupamento:
    """Executa PAM com distância euclidiana (protocolo Equipe 08)."""
    X = _validar_entrada(data, k)
    distancias = cdist(X, X, metric="euclidean")
    if k == 1:
        indices_medoides = np.array([np.argmin(distancias.sum(axis=0))], dtype=int)
        rotulos = np.zeros(len(X), dtype=int)
        objetivo = float(distancias[:, indices_medoides[0]].sum())
    else:
        if init == "first":
            medoides_iniciais = np.arange(k, dtype=np.uintp)
            modelo = pam(distancias, medoides_iniciais, max_iter=max_iter)
        else:
            modelo = pam(
                distancias,
                k,
                init=init,
                max_iter=max_iter,
                random_state=seed,
            )
        indices_medoides = np.asarray(modelo.medoids, dtype=int)
        rotulos = np.asarray(modelo.labels, dtype=int).copy()
        objetivo = float(modelo.loss)

    centros = X[indices_medoides].copy()

    return ResultadoAgrupamento(
        algoritmo="k-medoids",
        tipo="crisp",
        rotulos=rotulos,
        objetivo=objetivo,
        parametros={
            "k": k,
            "seed": seed,
            "metric": "euclidean",
            "method": "pam",
            "init": init if k > 1 else "exhaustive",
            "max_iter": max_iter if k > 1 else None,
            "medoid_indices": indices_medoides.tolist(),
        },
        centros=centros,
    )


@algoritmo("gaussian-mixture", objetivo="maximizar")
def gaussian_mixture(
    data: np.ndarray,
    k: int,
    seed: int,
    covariance_type: str = "full",
    reg_covar: float = 1e-6,
    tol: float = 1e-5,
    max_iter: int = 100,
    init_params: str = "random_from_data",
) -> ResultadoAgrupamento:
    """Agrupa os dados com Gaussian Mixture Model (EM)."""
    X = _validar_entrada(data, k)
    modelo = GaussianMixture(
        n_components=k,
        covariance_type=covariance_type,
        random_state=seed,
        tol=tol,
        reg_covar=reg_covar,
        max_iter=max_iter,
        n_init=1,
        init_params=init_params,
    ).fit(X)

    probabilidades = modelo.predict_proba(X)
    objetivo = float(modelo.score(X) * len(X))

    return ResultadoAgrupamento(
        algoritmo="gaussian-mixture",
        tipo="probabilistico",
        rotulos=np.argmax(probabilidades, axis=1),
        objetivo=objetivo,
        parametros={
            "k": k,
            "seed": seed,
            "covariance_type": covariance_type,
            "tol": tol,
            "reg_covar": reg_covar,
            "max_iter": max_iter,
            "n_init": 1,
            "init_params": init_params,
            "converged": modelo.converged_,
            "n_iter": modelo.n_iter_,
        },
        centros=np.array(modelo.means_, copy=True),
        probabilidades=probabilidades,
    )


@algoritmo("upgma", execucoes=1)
def upgma(
    data: np.ndarray,
    valores_k: tuple[int, ...] = (1, 2, 3, 4, 5),
) -> dict[int, ResultadoAgrupamento]:
    """Constrói uma única árvore UPGMA com distância Manhattan (protocolo Equipe 08)."""
    X = _validar_entrada(data, 1)
    if len(X) < 2:
        raise ValueError("UPGMA requer pelo menos duas amostras.")
    if not valores_k:
        raise ValueError("valores_k deve conter ao menos um valor.")
    for k in valores_k:
        _validar_entrada(X, k)

    hierarquia = linkage(pdist(X, metric="cityblock"), method="average")
    cortes = cut_tree(hierarquia, n_clusters=list(valores_k))
    return {
        k: ResultadoAgrupamento(
            algoritmo="upgma",
            tipo="hierarquico",
            rotulos=cortes[:, i].copy(),
            parametros={"k": k, "metric": "manhattan", "linkage": "average"},
            hierarquia=hierarquia.copy(),
        )
        for i, k in enumerate(valores_k)
    }


@algoritmo("dbscan", execucoes=1)
def dbscan(
    data: np.ndarray,
    eps: float = 0.8,
    min_samples: int = 5,
) -> ResultadoAgrupamento:
    """Executa DBSCAN com distância euclidiana."""
    X = np.asarray(data, dtype=float)
    if X.ndim != 2 or X.shape[0] == 0 or X.shape[1] == 0:
        raise ValueError("data deve ser uma matriz bidimensional não vazia.")
    if not np.isfinite(X).all():
        raise ValueError("data não pode conter NaN ou valores infinitos.")

    modelo = DBSCAN(
        eps=eps,
        min_samples=min_samples,
        metric="euclidean",
    )
    rotulos = modelo.fit_predict(X)
    ruido = int(np.sum(rotulos == -1))

    return ResultadoAgrupamento(
        algoritmo="dbscan",
        tipo="densidade",
        rotulos=rotulos.copy(),
        objetivo=None,
        parametros={
            "eps": float(eps),
            "min_samples": int(min_samples),
            "metric": "euclidean",
        },
        ruido=ruido,
    )