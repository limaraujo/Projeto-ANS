#!/usr/bin/env python3
"""Aplica a revisão editorial mantendo 18 slides e a narrativa original."""

from __future__ import annotations

import json
from pathlib import Path


DECK = Path(__file__).resolve().parents[1] / "deck.json"


def main():
    spec = json.loads(DECK.read_text(encoding="utf-8"))
    slides = spec["slides"]

    # Identificadores de rastreabilidade deixam de aparecer nos rodapés.
    for slide in slides:
        slide.pop("citations", None)

    spec["plan"]["sources"][0]["path"] = "artigo_iris_ieee_revisado.pdf"
    spec["plan"]["sources"][0]["sections"] = (
        "Artigo IEEE revisado; métodos, protocolo, variabilidade, sensibilidade, resultados e referências."
    )
    spec["plan"]["assumptions"][1] = "Fonte científica principal: artigo IEEE revisado da equipe."

    slides[7].update({
        "title": "Tunagem: perfis escolhidos em amarelo",
        "path": "assets/input/figure-8-revised.png",
        "alt": (
            "Kernel FCM, GMM/EM e DBSCAN. Amarelo identifica m=2 e gamma=0,05; "
            "GMM esferico com regularizacao 10^-2; e DBSCAN com epsilon 0,694 e min_samples 3."
        ),
        "caption": (
            "Escolhidas: Kernel FCM m = 2, γ = 0,05; GMM spherical, reg = 10⁻²; "
            "DBSCAN ε = 0,694, min_samples = 3."
        ),
        "attribution": "Fonte: artigo IEEE revisado da equipe; visualização dos registros existentes.",
        "notes": (
            "Tempo: 2 min. Amarelo marca somente os perfis efetivamente escolhidos. "
            "O Kernel FCM selecionou m = 2 e gamma = 0,05. O GMM selecionou covariância spherical "
            "e regularização 0,01; em k = 3, esse perfil obteve silhueta 0,4568 e ARI 0,6199. "
            "Esses valores não pertencem ao perfil full. O DBSCAN selecionou epsilon 0,694 e "
            "min_samples 3 sob piso de 95% de cobertura."
        ),
    })

    slides[9].update({
        "path": "assets/input/figure-10-revised.png",
        "alt": (
            "Dendrograma UPGMA condensado em doze subárvores, com cortes visíveis para dois e "
            "três grupos e explicação das contagens entre parênteses."
        ),
        "caption": "Manhattan; em k = 3: ARI = 0,7184 e silhueta = 0,4517.",
        "attribution": "Fonte: artigo IEEE revisado da equipe; topologia e valores preservados.",
        "notes": (
            "Tempo: 1 min. O UPGMA usa ligação média e distância Manhattan para construir uma "
            "única árvore. As folhas mostradas são subárvores agregadas; os números entre parênteses "
            "são contagens de observações, não identificadores. As linhas marcam os cortes em dois e "
            "três grupos. Em k = 3, ARI = 0,7184 e silhueta euclidiana = 0,4517."
        ),
    })

    slides[10] = {
        "layout": "figure",
        "title": "DBSCAN: cobertura muda a leitura da silhueta",
        "path": "assets/input/figure-11-revised.png",
        "alt": (
            "Tabela de sensibilidade do DBSCAN para pisos de cobertura de 97, 95, 94, 85 e 75 por cento; "
            "a linha de 95 por cento está destacada."
        ),
        "caption": "Configuração escolhida: 2 grupos; ruído = 1 setosa, 1 versicolor e 4 virginica.",
        "attribution": "Fonte: artigo IEEE revisado da equipe; mesma grade experimental, sem novos ajustes.",
        "notes": (
            "Tempo: 1 min. O piso de 95% foi fixado antes da seleção dos hiperparâmetros. Os pisos "
            "inferiores foram examinados depois como análise de sensibilidade. Quando o DBSCAN descarta "
            "mais flores, a silhueta aumenta, mas as métricas passam a descrever amostras diferentes. "
            "Por isso, silhuetas sob coberturas distintas não devem ser comparadas sem considerar quais "
            "observações foram retidas. A configuração escolhida formou dois grupos e marcou seis flores "
            "como ruído: uma setosa, uma versicolor e quatro virginica."
        ),
    }

    slides[15] = {
        "layout": "figure",
        "title": "Inicializações alteram o ARI em k = 3",
        "path": "assets/input/figure-16-revised.png",
        "alt": (
            "Intervalos observados de ARI para K-Means, de 0,4290 a 0,6451, e GMM/EM, "
            "de 0,4199 a 0,6199, em dez inicializações."
        ),
        "caption": "Amplitude entre sementes na mesma base; as faixas não são intervalos de confiança.",
        "attribution": "Fonte: artigo IEEE revisado da equipe; rodada final, sementes 52–61.",
        "notes": (
            "Tempo: 1 min. Em k = 3, o K-Means atingiu o melhor objetivo em 1 de 10 execuções e o "
            "ARI variou de 0,4290 a 0,6451. No GMM, o ARI variou de 0,4199 a 0,6199. Considerando como "
            "equivalentes os objetivos a até 10^-3 do melhor valor, 6 de 10 execuções do GMM atingiram "
            "o melhor objetivo; as log-verossimilhanças são próximas, não exatamente iguais. Dez "
            "inicializações não equivalem a dez amostras independentes do conjunto de dados."
        ),
    }

    slides[17] = {
        "layout": "TwoColumnSlide",
        "title": "Referências acadêmicas",
        "compact": True,
        "columns": [
            {
                "title": "ESTUDO E DADOS",
                "bullets": [
                    "Araújo, F.; Gomes, R. Agrupamento e Redução de Dimensionalidade na Base Iris. UFPE, 2026.",
                    "Fisher, R. A. Iris. UCI ML Repository, 1936. DOI: 10.24432/C56C76.",
                ],
            },
            {
                "title": "MÉTRICAS E DENSIDADE",
                "bullets": [
                    "Rousseeuw (1987). Silhouettes. JCAM 20:53–65. DOI: 10.1016/0377-0427(87)90125-7.",
                    "Hubert & Arabie (1985). Comparing partitions. J. Classification 2:193–218.",
                    "Ester et al. (1996). DBSCAN. Proc. KDD, pp. 226–231.",
                ],
            },
        ],
        "notes": (
            "Material de apoio. As referências foram preservadas do artigo IEEE revisado. "
            "Não são exibidos caminhos, diretórios ou identificadores internos do projeto."
        ),
    }

    spec["references"] = []
    DECK.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
