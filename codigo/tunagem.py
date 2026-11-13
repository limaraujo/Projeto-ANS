"""Grades não supervisionadas para tunar DBSCAN e Kernel Fuzzy C-Means."""

from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
from fcmeans import KFCM
from sklearn.neighbors import NearestNeighbors
from threadpoolctl import threadpool_limits

from algoritmos import calcular_silhueta, carregar_iris, dbscan, salvar_json

RAIZ = Path(__file__).resolve().parent.parent
DIRETORIO_SAIDA = RAIZ / "resultados" / "tunagem"
SEMENTES = range(42, 52)


def _metricas(dados: np.ndarray, rotulos: np.ndarray) -> dict[str, float | int]:
    """Calcula métricas usadas para comparar configurações sem escolher pelo ARI."""
    rotulos = np.asarray(rotulos)
    return {
        "silhueta": calcular_silhueta(dados, rotulos, ignorar_ruido=True),
        "grupos": len(set(rotulos) - {-1}),
        "ruido": int(np.sum(rotulos == -1)),
    }


def grade_dbscan(dados):
    """Retorna a referência de distância e as duas grades de raios."""
    referencia = float(
        np.median(
            NearestNeighbors(n_neighbors=5).fit(dados).kneighbors(dados)[0][:, -1]
        )
    )
    configuracoes = [
        ("eps_fixo", eps, min_samples, None)
        for eps, min_samples in product([0.4, 0.6, 0.8, 1.0], [3, 5, 10])
    ]
    configuracoes.extend(
        ("eps_relativo", referencia * fator, min_samples, fator)
        for fator, min_samples in product([0.75, 1.0, 1.5, 2.0], [3, 5, 10])
    )

    return referencia, configuracoes


def ajustar_kernel_fcm(dados, k, semente, gamma):
    """Ajusta uma inicialização e calcula o objetivo no espaço do kernel."""
    modelo = KFCM(
        n_clusters=k,
        m=2.0,
        max_iter=300,
        error=1e-5,
        random_state=semente,
        gamma=gamma,
    )
    modelo.fit(dados)
    distancias_quadradas = np.sum(
        (dados[:, None, :] - modelo.centers[None, :, :]) ** 2,
        axis=2,
    )
    objetivo = float(
        np.sum(
            modelo.u**2 * 2 * (-np.expm1(-float(modelo.gamma_) * distancias_quadradas))
        )
    )
    return {
        "gamma": float(modelo.gamma_),
        "k": k,
        "seed": semente,
        "objetivo": objetivo,
        "rotulos": modelo.u.argmax(axis=1),
    }


def tunar_dbscan(dados: np.ndarray) -> pd.DataFrame:
    """Avalia uma grade de ``eps`` e ``min_samples`` para o DBSCAN."""
    referencia, configuracoes = grade_dbscan(dados)

    resultados = []
    for regra, eps, min_samples, fator in configuracoes:
        resultado = dbscan(dados, eps=eps, min_samples=min_samples)
        resultados.append(
            {
                "regra": regra,
                "eps": eps,
                "min_samples": min_samples,
                "fator": fator,
                "referencia_5_vizinhos": referencia,
                **_metricas(dados, resultado.rotulos),
            }
        )
    return pd.DataFrame(resultados)


def tunar_kernel_fcm(dados: np.ndarray) -> tuple[pd.DataFrame, list[dict]]:
    """Avalia ``gamma`` e ``k``, retendo a melhor semente por função objetivo."""
    melhores = []
    execucoes = []
    for gamma, k in product([0.05, 0.25, 1.0], range(1, 6)):
        candidatas = []
        for semente in SEMENTES:
            execucao = ajustar_kernel_fcm(dados, k, semente, gamma)
            execucao["semente"] = execucao.pop("seed")
            candidatas.append(execucao)
            execucoes.append(execucao)

        melhor = min(candidatas, key=lambda item: item["objetivo"])
        melhores.append(
            {key: value for key, value in melhor.items() if key != "rotulos"}
            | _metricas(dados, melhor["rotulos"])
        )
    return pd.DataFrame(melhores), execucoes


def main() -> None:
    """Executa somente as duas grades de tunagem e persiste seus resultados."""
    DIRETORIO_SAIDA.mkdir(parents=True, exist_ok=True)
    dados, _, _ = carregar_iris(padronizar=True)

    resultados_dbscan = tunar_dbscan(dados)
    resultados_dbscan.to_csv(
        DIRETORIO_SAIDA / "dbscan.csv", index=False, encoding="utf-8"
    )

    resultados_kernel, execucoes_kernel = tunar_kernel_fcm(dados)
    resultados_kernel.to_csv(
        DIRETORIO_SAIDA / "kernel_fcm.csv", index=False, encoding="utf-8"
    )
    salvar_json(DIRETORIO_SAIDA / "execucoes_kernel_fcm.json", execucoes_kernel)
    print(f"Tunagem concluída: {DIRETORIO_SAIDA}")


if __name__ == "__main__":
    with threadpool_limits(limits=1):
        main()
