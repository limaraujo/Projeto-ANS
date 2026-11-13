"""Audita os resultados persistidos contra o protocolo da Equipe 08."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score, silhouette_score

from algoritmos import carregar_iris, salvar_json


def validar() -> None:
    raiz = Path(__file__).resolve().parent.parent / "resultados"
    q1 = json.loads((raiz / "execucoes_questao_1.json").read_text())
    q2 = json.loads((raiz / "execucoes_questao_2.json").read_text())
    X, y, _ = carregar_iris()
    metricas = pd.read_csv(raiz / "metricas_por_k.csv")
    total = 2
    for nome, por_k in q1.items():
        if nome in ("upgma", "dbscan"):
            continue
        assert set(por_k) == {"1", "2", "3", "4", "5"}
        for k, runs in por_k.items():
            assert len(runs) == 10
            assert [r["parametros"]["seed"] for r in runs] == list(range(42, 52))
            total += len(runs)
            melhor = (max if nome == "gaussian-mixture" else min)(
                runs, key=lambda r: r["objetivo"]
            )
            linha = metricas[
                (metricas.algoritmo == nome) & (metricas.k == int(k))
            ].iloc[0]
            assert np.isclose(linha.objetivo, melhor["objetivo"])
            assert np.isclose(linha.ari, adjusted_rand_score(y, melhor["rotulos"]))
            if k == "1":
                assert np.isnan(linha.silhueta)
            else:
                assert np.isclose(
                    linha.silhueta, silhouette_score(X, melhor["rotulos"])
                )
            for r in runs:
                assert len(r["rotulos"]) == 150
                for chave in ("pertinencias", "probabilidades"):
                    if r[chave] is not None:
                        u = np.array(r[chave])
                        assert u.shape == (150, int(k))
                        assert np.allclose(u.sum(axis=1), 1)
                        assert np.array_equal(u.argmax(axis=1), r["rotulos"])
    assert total == 252
    for nome, r in q2.items():
        z = np.array(r["coordenadas"])
        assert z.shape == (150, 4 if nome == "pca" else 2)
        assert np.isfinite(z).all()
        assert 0 <= r["trustworthiness_10"] <= 1
    assert np.isclose(sum(q2["pca"]["variancia_explicada"]), 1)
    assert q2["tsne"]["divergencia_kl"] >= 0
    salvar_json(
        raiz / "validacao.json",
        {
            "status": "aprovado",
            "ajustes_questao_1": total,
            "tecnicas_questao_2": len(q2),
            "verificacoes": [
                "sementes e contagens",
                "ótimos por função objetivo",
                "silhuetas e ARI recalculados",
                "normalização e argmax das pertinências e probabilidades",
                "dimensões e finitude das projeções",
                "variância PCA e KL t-SNE",
            ],
        },
    )
    print("Validação aprovada: 252 ajustes e quatro técnicas de redução.")


if __name__ == "__main__":
    validar()
