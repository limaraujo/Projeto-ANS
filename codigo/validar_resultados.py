"""Audita os resultados persistidos contra o protocolo da Equipe 08."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import cut_tree, linkage
from scipy.spatial.distance import pdist
from sklearn.metrics import adjusted_rand_score, silhouette_score
from threadpoolctl import threadpool_limits

from algoritmos import carregar_iris, salvar_json

DIRETORIO_RESULTADOS = Path(__file__).resolve().parent.parent / "resultados"


def _ler_json(caminho: Path):
    return json.loads(caminho.read_text(encoding="utf-8"))


def _ler_csv(caminho: Path, indice: str | list[str]) -> pd.DataFrame:
    tabela = pd.read_csv(caminho, index_col=indice, float_precision="round_trip")
    assert tabela.index.is_unique, caminho
    return tabela


def _metricas(X, y, rotulos) -> tuple[float, float]:
    return (
        silhouette_score(X, rotulos)
        if 2 <= len(np.unique(rotulos)) < len(X)
        else np.nan,
        adjusted_rand_score(y, rotulos) if len(X) >= 2 else np.nan,
    )


def _melhor(nome, execucoes):
    validas = [
        r
        for r in execucoes
        if r["objetivo"] is not None
        and np.isfinite(r["objetivo"])
        and r["rotulos"] is not None
    ]
    selecionar = max if nome == "gaussian-mixture" else min
    return selecionar(validas, key=lambda r: r["objetivo"], default=None)


def _conferir_metricas(linha, X, y, rotulos) -> None:
    silhueta, ari = _metricas(X, y, rotulos)
    assert np.isclose(linha.silhueta, silhueta, equal_nan=True)
    assert np.isclose(linha.ari, ari, equal_nan=True)


def _validar_particionais(X, y, q1, metricas, metadados, diretorio):
    grade = _ler_csv(diretorio / "particionais.csv", ["algoritmo", "configuracao", "k"])
    execucoes = _ler_json(diretorio / "execucoes.json")
    busca = metadados["tunagem"]
    ks = list(range(2, 6))
    sementes = list(range(42, 52))
    assert busca["valores_k"] == ks
    assert busca["sementes"] == sementes
    assert list(grade.index.unique("algoritmo")) == list(execucoes["particionais"])

    vistas = set()
    contagem = 0
    for nome, perfis in execucoes["particionais"].items():
        for perfil in perfis:
            id_perfil = perfil["configuracao"]
            assert set(perfil["execucoes"]) == set(map(str, ks))
            for k in ks:
                chave = (nome, id_perfil, k)
                vistas.add(chave)
                rodadas = perfil["execucoes"][str(k)]
                assert [r["seed"] for r in rodadas] == sementes
                contagem += len(rodadas)
                linha = grade.loc[chave]
                assert linha.referencia == perfil["referencia"]
                assert linha.falhas == sum(r["erro"] is not None for r in rodadas), (
                    chave
                )
                convergencias = [
                    r["convergiu"] for r in rodadas if r["convergiu"] is not None
                ]
                convergidas = sum(convergencias) if convergencias else np.nan
                assert np.isclose(linha.convergidas, convergidas, equal_nan=True), chave
                for parametro, valor in perfil["parametros"].items():
                    assert linha[parametro] == valor, (chave, parametro)
                melhor = _melhor(nome, rodadas)
                if melhor is None:
                    assert pd.isna(linha.silhueta) and pd.isna(linha.ari), chave
                    continue
                assert melhor["seed"] == linha.seed, chave
                assert np.isclose(melhor["objetivo"], linha.objetivo), chave
                rotulos = np.array(melhor["rotulos"])
                assert len(rotulos) == len(X), chave
                assert linha.grupos == len(np.unique(rotulos)), chave
                _conferir_metricas(linha, X, y, rotulos)

        linhas = grade.loc[nome].dropna(subset=["silhueta"]).reset_index()
        vencedora = linhas.sort_values(
            ["silhueta", "k", "configuracao"], ascending=[False, True, True]
        ).iloc[0]
        selecao = busca["selecionados"][nome]
        assert vencedora.configuracao == selecao["configuracao"], nome
        assert vencedora.k == selecao["k"], nome
        marcado = grade.loc[nome]
        assert list(marcado[marcado.selecionado].index) == [
            (selecao["configuracao"], selecao["k"])
        ], nome
        assert list(marcado[marcado.configuracao_selecionada].index) == [
            (selecao["configuracao"], k) for k in ks
        ], nome

        perfil = next(p for p in perfis if p["configuracao"] == selecao["configuracao"])
        assert perfil["parametros"] == selecao["parametros"], nome
        for k in ks:
            for final, candidata in zip(
                q1[nome][str(k)], perfil["execucoes"][str(k)], strict=True
            ):
                assert final["parametros"]["seed"] == candidata["seed"], (nome, k)
                assert final["rotulos"] == candidata["rotulos"], (nome, k)
                assert np.isclose(final["objetivo"], candidata["objetivo"]), (nome, k)

        assert metricas.loc[(nome, selecao["k"])].selecionado, nome

    assert vistas == set(grade.index)
    assert contagem == busca["ajustes_particionais"]
    return execucoes, contagem


def _validar_dbscan(X, y, resultado, execucoes, busca, diretorio):
    grade = _ler_csv(diretorio / "dbscan.csv", "configuracao")
    ids = [r["configuracao"] for r in execucoes]
    assert set(ids) == set(grade.index) and len(ids) == len(grade)
    minima = busca["cobertura_minima_dbscan_pct"]
    assert minima == 95
    for r in execucoes:
        linha = grade.loc[r["configuracao"]]
        rotulos = np.array(r["rotulos"])
        assert len(rotulos) == len(X)
        mascara = rotulos != -1
        assert linha.amostras_avaliadas == mascara.sum()
        assert linha.ruido == (~mascara).sum()
        assert linha.grupos == len(np.unique(rotulos[mascara]))
        assert np.isclose(linha.cobertura_pct, 100 * mascara.mean())
        _conferir_metricas(linha, X[mascara], y[mascara], rotulos[mascara])
        assert linha.elegivel == (
            linha.cobertura_pct >= minima and pd.notna(linha.silhueta)
        )

    selecionadas = grade[grade.selecionado]
    assert len(selecionadas) == 1
    escolhida = selecionadas.iloc[0]
    assert escolhida.name == busca["dbscan"]["configuracao"]
    assert busca["dbscan_modo"] in ("automatico", "manual")
    if busca["dbscan_modo"] == "automatico":
        elegiveis = grade[grade.elegivel].reset_index()
        vencedora = elegiveis.sort_values(
            ["silhueta", "cobertura_pct", "configuracao"],
            ascending=[False, False, True],
        ).iloc[0]
        assert vencedora.configuracao == escolhida.name
    assert np.isclose(escolhida.eps, resultado["parametros"]["eps"])
    assert escolhida.min_samples == resultado["parametros"]["min_samples"]
    assert resultado["rotulos"] == next(
        r["rotulos"] for r in execucoes if r["configuracao"] == escolhida.name
    )
    assert len(grade) == busca["ajustes_dbscan"]
    return len(grade)


def _validar_protocolo(X, y, q1, metricas, resumo):
    particoes = {}
    total = 2
    ks = list(range(1, 6))
    sementes = list(range(42, 52))
    for nome, por_k in q1.items():
        if nome == "dbscan":
            continue
        assert set(por_k) == set(map(str, ks)), nome
        silhuetas = {}
        selecionadas = {}
        if nome == "upgma":
            hierarquia = linkage(pdist(X, metric="cityblock"), method="average")
            cortes = cut_tree(hierarquia, n_clusters=ks)
        for i, k in enumerate(ks):
            linha = metricas.loc[(nome, k)]
            if nome == "upgma":
                melhor = por_k[str(k)]
                assert np.allclose(melhor["hierarquia"], hierarquia)
                assert np.array_equal(melhor["rotulos"], cortes[:, i])
            else:
                rodadas = por_k[str(k)]
                assert [r["parametros"]["seed"] for r in rodadas] == sementes, (nome, k)
                total += len(rodadas)
                melhor = _melhor(nome, rodadas)
                assert melhor is not None, (nome, k)
                assert linha.seed == melhor["parametros"]["seed"], (nome, k)
                assert np.isclose(linha.objetivo, melhor["objetivo"]), (nome, k)
                for r in rodadas:
                    assert len(r["rotulos"]) == len(X), (nome, k)
                    for chave in ("pertinencias", "probabilidades"):
                        if r[chave] is not None:
                            pesos = np.array(r[chave])
                            assert pesos.shape == (len(X), k), (nome, k)
                            assert np.allclose(pesos.sum(axis=1), 1), (nome, k)
                            assert np.array_equal(pesos.argmax(axis=1), r["rotulos"]), (
                                nome,
                                k,
                            )

            rotulos = np.array(melhor["rotulos"])
            _conferir_metricas(linha, X, y, rotulos)
            if k == 1:
                assert pd.isna(linha.silhueta), nome
            selecionadas[k] = rotulos
            silhuetas[k] = linha.silhueta

        k_estrela = max(
            (k for k in ks if np.isfinite(silhuetas[k])),
            key=lambda k: (silhuetas[k], -k),
        )
        assert list(metricas.loc[nome].query("selecionado").index) == [k_estrela], nome
        assert int(resumo.loc[nome, "k*"]) == k_estrela, nome
        particoes[nome] = selecionadas[k_estrela]

    particoes["dbscan"] = np.array(q1["dbscan"]["rotulos"])
    assert len(particoes) == 7
    assert total == 252
    assert len(metricas) == 30
    return particoes, total


def _validar_resumos(X, y, resumo, particoes, diretorio):
    comum = _ler_csv(diretorio / "comparacao_mesma_amostra.csv", "algoritmo")
    assert set(resumo.index) == set(comum.index) == set(particoes)
    dbscan = particoes["dbscan"]
    mascara = dbscan != -1
    for nome, rotulos in particoes.items():
        linha = resumo.loc[nome]
        mantidos = rotulos != -1
        silhueta, ari = _metricas(X[mantidos], y[mantidos], rotulos[mantidos])
        assert np.isclose(linha["Silhueta"], silhueta, equal_nan=True), nome
        assert np.isclose(linha["ARI"], ari, equal_nan=True), nome
        assert linha["Clusters"] == len(np.unique(rotulos[mantidos])), nome
        assert linha["Ruído"] == (~mantidos).sum(), nome
        assert linha["Amostras avaliadas"] == mantidos.sum(), nome
        assert np.isclose(linha["Cobertura (%)"], 100 * mantidos.mean()), nome
        assert np.isclose(linha["Ruído (%)"], 100 * (~mantidos).mean()), nome

        linha_comum = comum.loc[nome]
        _conferir_metricas(linha_comum, X[mascara], y[mascara], rotulos[mascara])
        assert linha_comum.amostras_avaliadas == mascara.sum(), nome
        assert linha_comum.grupos == len(np.unique(rotulos[mascara])), nome
        acordo = (
            adjusted_rand_score(dbscan[mascara], rotulos[mascara])
            if mascara.sum() >= 2
            else np.nan
        )
        assert np.isclose(linha_comum.ari_com_dbscan, acordo, equal_nan=True), nome


def _validar_q2(raiz: Path) -> int:
    caminho = raiz / "execucoes_questao_2.json"
    if not caminho.is_file() and raiz != DIRETORIO_RESULTADOS:
        return 0
    q2 = _ler_json(caminho)
    assert set(q2) == {"pca", "kernel_pca", "tsne", "umap"}
    for nome, r in q2.items():
        z = np.array(r["coordenadas"])
        assert z.shape == (150, 4 if nome == "pca" else 2)
        assert np.isfinite(z).all()
        assert 0 <= r["trustworthiness_10"] <= 1
    assert np.isclose(sum(q2["pca"]["variancia_explicada"]), 1)
    assert q2["tsne"]["divergencia_kl"] >= 0
    return len(q2)


def validar(raiz: Path = DIRETORIO_RESULTADOS) -> None:
    q1 = _ler_json(raiz / "execucoes_questao_1.json")
    metadados = _ler_json(raiz / "metadados_questao_1.json")
    X, y, _ = carregar_iris(padronizar=metadados["preprocessamento"]["padronizado"])
    metricas = _ler_csv(raiz / "metricas_por_k.csv", ["algoritmo", "k"])
    resumo = _ler_csv(raiz / "resumo_agrupamentos.csv", "Algoritmo")
    pasta_tunagem = raiz / "tunagem"
    particoes, total = _validar_protocolo(X, y, q1, metricas, resumo)
    execucoes, ajustes_particionais = _validar_particionais(
        X, y, q1, metricas, metadados, pasta_tunagem
    )
    busca = metadados["tunagem"]
    ajustes_dbscan = _validar_dbscan(
        X, y, q1["dbscan"], execucoes["dbscan"], busca, pasta_tunagem
    )
    _validar_resumos(X, y, resumo, particoes, pasta_tunagem)
    assert busca["ajustes_k1"] == 50
    assert busca["ajustes_upgma"] == 1
    total_real = (
        ajustes_particionais
        + ajustes_dbscan
        + busca["ajustes_k1"]
        + busca["ajustes_upgma"]
    )
    assert total_real == busca["ajustes_totais"]

    tecnicas = _validar_q2(raiz)
    verificacoes = [
        "sementes e contagens da grade e do protocolo final",
        "ótimos por função objetivo e seleção por silhueta",
        "normalização e argmax das pertinências e probabilidades",
        "árvore UPGMA Manhattan e cinco cortes",
        "silhuetas, ARI e cobertura do DBSCAN recalculados sem ruído",
        "silhuetas e ARI comparados na mesma amostra",
    ]
    if tecnicas:
        verificacoes.extend(
            ["dimensões e finitude das projeções", "variância PCA e KL t-SNE"]
        )

    salvar_json(
        raiz / "validacao.json",
        {
            "status": "aprovado",
            "ajustes_questao_1": total,
            "ajustes_grade_particional": ajustes_particionais,
            "ajustes_grade_dbscan": ajustes_dbscan,
            "ajustes_questao_1_com_busca": total_real,
            "tecnicas_questao_2": tecnicas,
            "verificacoes": verificacoes,
        },
    )
    print(
        f"Validação aprovada. {total} execuções no protocolo final e {total_real} com a busca."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--diretorio-resultados", type=Path, default=DIRETORIO_RESULTADOS
    )
    with threadpool_limits(limits=1):
        validar(parser.parse_args().diretorio_resultados)
