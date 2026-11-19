"""Busca dos hiperparâmetros de agrupamento pelo protocolo da Questão 1."""

from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from threadpoolctl import threadpool_limits

from algoritmos import (
    ResultadoAgrupamento,
    calcular_ari,
    calcular_silhueta,
    dbscan,
    executar_algoritmo,
    plt,
    salvar_json,
    selecionar_melhores_por_k,
    sns,
)

SEMENTES_PILOTO = range(42, 52)
VALORES_K = range(2, 6)
COBERTURA_MINIMA_DBSCAN = 95.0
PADRAO_DBSCAN = (0.8, 5)

NOMES_METODOS = {
    "k-means": "K-Means",
    "fuzzy-k-means": "Fuzzy K-Means",
    "kernel-fuzzy-k-means": "Kernel Fuzzy K-Means",
    "k-medoids": "K-Medoids",
    "gaussian-mixture": "GMM/EM",
}


@dataclass
class ResultadoBusca:
    particionais: pd.DataFrame
    dbscan: pd.DataFrame
    execucoes: dict[str, Any]
    metadados: dict[str, Any]


def grade_particionais() -> dict[str, list[dict[str, Any]]]:
    """Mantém o perfil de referência na primeira posição de cada grade."""
    valores_m = (2.0, 1.5, 2.5)
    return {
        "k-means": [
            {"init": inicializacao} for inicializacao in ("random", "k-means++")
        ],
        "fuzzy-k-means": [{"m": m} for m in valores_m],
        "kernel-fuzzy-k-means": [
            {"m": m, "gamma": gamma}
            for m, gamma in product(valores_m, (0.25, 0.05, 1.0))
        ],
        "k-medoids": [{"init": inicializacao} for inicializacao in ("random", "build")],
        "gaussian-mixture": [
            {"covariance_type": tipo, "reg_covar": regularizacao}
            for tipo, regularizacao in product(
                ("full", "tied", "diag", "spherical"), (1e-6, 1e-4, 1e-2)
            )
        ],
    }


def grade_dbscan(dados: np.ndarray) -> tuple[float, list[tuple]]:
    """Usa raios absolutos e relativos à mediana da distância ao quinto vizinho."""
    distancias, _ = NearestNeighbors(n_neighbors=5).fit(dados).kneighbors(dados)
    referencia = float(np.median(distancias[:, -1]))
    configuracoes = [
        ("eps_fixo", eps, min_samples, None)
        for eps, min_samples in product((0.4, 0.6, 0.8, 1.0), (3, 5, 10))
    ]
    configuracoes.extend(
        ("eps_relativo", referencia * fator, min_samples, fator)
        for fator, min_samples in product((0.75, 1.0, 1.5, 2.0), (3, 5, 10))
    )
    return referencia, configuracoes


def _ajustar_perfil(nome, dados, parametros):
    execucoes = {k: [] for k in VALORES_K}
    registros = {k: [] for k in VALORES_K}
    for k, seed in product(VALORES_K, SEMENTES_PILOTO):
        registro = dict(
            seed=seed,
            objetivo=None,
            rotulos=None,
            convergiu=None,
            iteracoes=None,
            erro=None,
        )
        try:
            resultado = executar_algoritmo(nome, dados, k=k, seed=seed, **parametros)
            if resultado.objetivo is None or not np.isfinite(resultado.objetivo):
                raise ValueError("Função objetivo indefinida ou não finita.")
        except (ValueError, FloatingPointError, np.linalg.LinAlgError) as erro:
            registro["erro"] = str(erro)
        else:
            execucoes[k].append(resultado)
            registro.update(
                objetivo=resultado.objetivo,
                rotulos=resultado.rotulos,
                convergiu=resultado.parametros.get("converged"),
                iteracoes=resultado.parametros.get("n_iter"),
            )
        registros[k].append(registro)

    melhores = selecionar_melhores_por_k(
        nome, {k: ajustes for k, ajustes in execucoes.items() if ajustes}
    )
    return execucoes, registros, melhores


def _buscar_particionais(dados):
    selecionados, registros = {}, {}
    linhas = []
    for nome, perfis in grade_particionais().items():
        print(f"Testando {len(perfis)} perfis de {NOMES_METODOS[nome]}...")
        registros[nome] = []
        medias = {}
        linhas_perfis = {}
        for configuracao, parametros in enumerate(perfis, start=1):
            execucoes, registros_perfil, melhores = _ajustar_perfil(
                nome, dados, parametros
            )
            registros[nome].append(
                {
                    "configuracao": configuracao,
                    "parametros": parametros,
                    "referencia": configuracao == 1,
                    "execucoes": registros_perfil,
                }
            )
            linhas_perfil = []
            for k in VALORES_K:
                melhor = melhores.get(k)
                convergencias = [
                    r["convergiu"]
                    for r in registros_perfil[k]
                    if r["convergiu"] is not None
                ]
                linhas_perfil.append(
                    {
                        "algoritmo": nome,
                        "configuracao": configuracao,
                        "k": k,
                        **parametros,
                        "seed": melhor.parametros["seed"] if melhor else None,
                        "objetivo": melhor.objetivo if melhor else None,
                        "grupos": len(np.unique(melhor.rotulos)) if melhor else None,
                        "silhueta": (
                            calcular_silhueta(dados, melhor.rotulos)
                            if melhor
                            else np.nan
                        ),
                        "convergidas": sum(convergencias) if convergencias else None,
                        "falhas": len(SEMENTES_PILOTO) - len(execucoes[k]),
                        "referencia": configuracao == 1,
                    }
                )
            linhas_perfis[configuracao] = linhas_perfil
            silhuetas = [linha["silhueta"] for linha in linhas_perfil]
            if np.isfinite(silhuetas).all():
                medias[configuracao] = float(np.mean(silhuetas))

        if not medias:
            raise ValueError(
                f"Nenhum perfil de {nome} tem silhuetas válidas em todos os k."
            )
        # A primeira configuração na ordem da grade é a referência.
        configuracao = max(medias, key=medias.__getitem__)
        selecionados[nome] = {
            "configuracao": configuracao,
            "parametros": perfis[configuracao - 1],
            "silhueta_media": medias[configuracao],
        }
        for id_perfil, linhas_perfil in linhas_perfis.items():
            for linha in linhas_perfil:
                linha.update(
                    silhueta_media=medias.get(id_perfil, np.nan),
                    configuracao_selecionada=id_perfil == configuracao,
                )
            linhas.extend(linhas_perfil)
    return selecionados, registros, pd.DataFrame(linhas)


def _buscar_dbscan(dados, parametros_manuais):
    referencia, configuracoes = grade_dbscan(dados)
    if parametros_manuais and all(
        (eps, min_samples) != parametros_manuais
        for _, eps, min_samples, _ in configuracoes
    ):
        configuracoes.append(("manual", *parametros_manuais, None))

    resultados, linhas = [], []
    for configuracao, (regra, eps, min_samples, fator) in enumerate(
        configuracoes, start=1
    ):
        resultado = dbscan(dados, eps=eps, min_samples=min_samples)
        resultados.append(resultado)
        retidos = len(dados) - resultado.ruido
        cobertura = 100 * retidos / len(dados)
        silhueta = calcular_silhueta(dados, resultado.rotulos, ignorar_ruido=True)
        linhas.append(
            {
                "configuracao": configuracao,
                "regra": regra,
                "eps": eps,
                "min_samples": min_samples,
                "fator": fator,
                "referencia_5_vizinhos": referencia,
                "grupos": len(np.unique(resultado.rotulos[resultado.rotulos != -1])),
                "ruido": resultado.ruido,
                "amostras_avaliadas": retidos,
                "cobertura_pct": cobertura,
                "silhueta": silhueta,
                "elegivel": bool(
                    np.isfinite(silhueta) and cobertura >= COBERTURA_MINIMA_DBSCAN
                ),
            }
        )
    if parametros_manuais:
        melhor = next(
            linha
            for linha in linhas
            if (linha["eps"], linha["min_samples"]) == parametros_manuais
        )
    else:
        elegiveis = [linha for linha in linhas if linha["elegivel"]]
        if not elegiveis:
            raise ValueError(
                "A grade DBSCAN não encontrou uma silhueta válida com cobertura de "
                f"pelo menos {COBERTURA_MINIMA_DBSCAN:g}%."
            )
        melhor = max(
            elegiveis,
            key=lambda linha: (
                linha["silhueta"],
                linha["cobertura_pct"],
                -linha["configuracao"],
            ),
        )

    for linha in linhas:
        linha["selecionado"] = linha is melhor
    registros = [
        {"configuracao": linha["configuracao"], "rotulos": resultado.rotulos}
        for linha, resultado in zip(linhas, resultados, strict=True)
    ]
    return melhor, registros, pd.DataFrame(linhas)


def comparar_amostra_dbscan(
    dados: np.ndarray,
    rotulos_verdadeiros: np.ndarray,
    selecionados: dict[str, ResultadoAgrupamento],
    resultado_dbscan: ResultadoAgrupamento,
) -> pd.DataFrame:
    """Avalia as partições já ajustadas no subconjunto retido pelo DBSCAN."""
    mascara = resultado_dbscan.rotulos != -1
    dados_retidos = dados[mascara]
    verdadeiros_retidos = rotulos_verdadeiros[mascara]
    dbscan_retidos = resultado_dbscan.rotulos[mascara]
    total = len(dados_retidos)
    linhas = []
    for nome, resultado in (selecionados | {"dbscan": resultado_dbscan}).items():
        rotulos = resultado.rotulos[mascara]
        linhas.append(
            {
                "algoritmo": nome,
                "grupos": len(np.unique(rotulos)),
                "amostras_avaliadas": total,
                "silhueta": (
                    calcular_silhueta(dados_retidos, rotulos) if total >= 2 else np.nan
                ),
                "ari": (
                    calcular_ari(verdadeiros_retidos, rotulos) if total >= 2 else np.nan
                ),
                "ari_com_dbscan": (
                    calcular_ari(dbscan_retidos, rotulos) if total >= 2 else np.nan
                ),
            }
        )
    return pd.DataFrame(linhas)


def _salvar_figura(fig, caminho):
    fig.savefig(caminho.with_suffix(".png"), dpi=160, bbox_inches="tight")
    fig.savefig(caminho.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def _plotar_particionais(diretorio, tabela):
    cruzados = {
        "kernel-fuzzy-k-means": ("m", "gamma"),
        "gaussian-mixture": ("covariance_type", "reg_covar"),
    }
    with sns.axes_style("whitegrid"):
        for nome, linhas in tabela.groupby("algoritmo", sort=False):
            caminho = diretorio / f"sensibilidade_{nome.replace('-', '_')}"
            selecionadas = linhas.loc[linhas["configuracao_selecionada"]]
            if nome in cruzados:
                linha, coluna = cruzados[nome]
                selecionada = selecionadas.iloc[0]
                fig, eixos = plt.subplots(2, 2, figsize=(8, 5), layout="constrained")
                limites = (linhas["silhueta"].min(), linhas["silhueta"].max())
                for k, eixo in zip(VALORES_K, eixos.flat, strict=True):
                    matriz = linhas.loc[linhas["k"] == k].pivot(
                        index=linha, columns=coluna, values="silhueta"
                    )
                    sns.heatmap(
                        matriz,
                        ax=eixo,
                        annot=True,
                        fmt=".3f",
                        cmap="YlGnBu",
                        cbar=False,
                        vmin=limites[0],
                        vmax=limites[1],
                        linewidths=0.5,
                    )
                    y = matriz.index.get_loc(selecionada[linha])
                    x = matriz.columns.get_loc(selecionada[coluna])
                    eixo.scatter(
                        x + 0.5,
                        y + 0.5,
                        s=250,
                        marker="s",
                        facecolor="none",
                        edgecolor="#c43c39",
                        linewidth=1.5,
                    )
                    eixo.set_title(f"k = {k}")
                fig.suptitle(f"{NOMES_METODOS[nome]} · Silhueta por configuração")
            else:
                fig, eixo = plt.subplots(figsize=(6, 3.5), layout="constrained")
                chave = "m" if nome == "fuzzy-k-means" else "init"
                sns.lineplot(
                    linhas, x="k", y="silhueta", hue=chave, marker="o", ax=eixo
                )
                eixo.scatter(
                    selecionadas["k"],
                    selecionadas["silhueta"],
                    s=120,
                    facecolor="none",
                    edgecolor="#c43c39",
                    linewidth=1.5,
                    zorder=5,
                )
                eixo.set(
                    xticks=list(VALORES_K),
                    xlabel="Número de grupos (k)",
                    ylabel="Silhueta",
                    title=f"{NOMES_METODOS[nome]} · {chave}",
                )
            _salvar_figura(fig, caminho)


def _plotar_dbscan(diretorio, tabela):
    with sns.axes_style("whitegrid"):
        fig, eixos = plt.subplots(1, 2, figsize=(8, 3.6), layout="constrained")
        escolhida = tabela.loc[tabela["selecionado"]].iloc[0]
        for eixo, metrica, nome in zip(
            eixos, ("silhueta", "ari"), ("Silhueta", "ARI"), strict=True
        ):
            sns.scatterplot(
                tabela,
                x="cobertura_pct",
                y=metrica,
                hue="min_samples",
                style="regra",
                ax=eixo,
            )
            eixo.axvline(
                COBERTURA_MINIMA_DBSCAN, color="#666666", linestyle="--", linewidth=1
            )
            if np.isfinite(escolhida[metrica]):
                eixo.scatter(
                    escolhida["cobertura_pct"],
                    escolhida[metrica],
                    s=120,
                    facecolor="none",
                    edgecolor="#c43c39",
                    linewidth=1.5,
                    zorder=5,
                )
            eixo.set(xlabel="Cobertura (%)", ylabel=nome)
        fig.suptitle("DBSCAN · Métricas e cobertura")
        _salvar_figura(fig, diretorio / "sensibilidade_dbscan")


def buscar_hiperparametros(
    dados: np.ndarray,
    parametros_dbscan: tuple[float, int] | None = None,
) -> ResultadoBusca:
    """Avalia as grades piloto e escolhe uma configuração por algoritmo."""
    with threadpool_limits(limits=1):
        selecionados, registros_particionais, tabela_particionais = (
            _buscar_particionais(dados)
        )
        escolha_dbscan, registros_dbscan, tabela_dbscan = _buscar_dbscan(
            dados, parametros_dbscan
        )

    return ResultadoBusca(
        tabela_particionais,
        tabela_dbscan,
        {"particionais": registros_particionais, "dbscan": registros_dbscan},
        {
            "valores_k": list(VALORES_K),
            "sementes": list(SEMENTES_PILOTO),
            "cobertura_minima_dbscan_pct": COBERTURA_MINIMA_DBSCAN,
            "criterio_particionais": (
                "Melhor objetivo finito entre as sementes, com empate pela menor semente. "
                "Maior média aritmética das quatro silhuetas em k de 2 a 5. "
                "Empates favorecem o perfil de referência e depois a ordem da grade."
            ),
            "criterio_dbscan": (
                "Maior silhueta válida com ao menos 95% de cobertura, com empate pela "
                "maior cobertura e pela primeira configuração na grade."
            ),
            "ajustes_particionais": len(tabela_particionais) * len(SEMENTES_PILOTO),
            "ajustes_dbscan": len(tabela_dbscan),
            "selecionados": selecionados,
            "dbscan": escolha_dbscan,
            "dbscan_modo": "manual" if parametros_dbscan else "automatico",
        },
    )


def salvar_busca(
    busca: ResultadoBusca, rotulos_verdadeiros: np.ndarray, diretorio: Path
) -> None:
    """Acrescenta o ARI descritivo ao registro piloto após a rodada oficial."""
    rotulos_particionais = {
        (nome, perfil["configuracao"], k, rodada["seed"]): rodada["rotulos"]
        for nome, perfis in busca.execucoes["particionais"].items()
        for perfil in perfis
        for k, rodadas in perfil["execucoes"].items()
        for rodada in rodadas
    }
    tabela_particionais = busca.particionais.assign(
        ari=[
            (
                calcular_ari(
                    rotulos_verdadeiros,
                    rotulos_particionais[
                        (linha.algoritmo, linha.configuracao, linha.k, linha.seed)
                    ],
                )
                if pd.notna(linha.seed)
                else np.nan
            )
            for linha in busca.particionais.itertuples(index=False)
        ]
    )
    tabela_dbscan = busca.dbscan.assign(
        ari=[
            calcular_ari(rotulos_verdadeiros, rodada["rotulos"], ignorar_ruido=True)
            for rodada in busca.execucoes["dbscan"]
        ]
    )
    diretorio_figuras = diretorio / "figuras"
    diretorio_figuras.mkdir(parents=True, exist_ok=True)
    tabela_particionais.to_csv(diretorio / "particionais.csv", index=False)
    tabela_dbscan.to_csv(diretorio / "dbscan.csv", index=False)
    salvar_json(diretorio / "execucoes.json", busca.execucoes)
    _plotar_particionais(diretorio_figuras, tabela_particionais)
    _plotar_dbscan(diretorio_figuras, tabela_dbscan)


if __name__ == "__main__":
    from questoes import executar_questao_1

    executar_questao_1()
