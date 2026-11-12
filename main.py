"""Ponto de entrada reproduzível das Questões 1 e 2 da Equipe 08."""
import argparse
from questoes import executar_questao_1, executar_questao_2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--questao', choices=['1', '2', 'todas'], default='todas')
    parser.add_argument('--sem-padronizar', action='store_true')
    parser.add_argument('--eps', type=float, default=0.8)
    parser.add_argument('--min-samples', type=int, default=5)
    parser.add_argument('--seed', type=int, default=42, help='Semente das projeções; Q1 usa 42–51')
    parser.add_argument('--gamma', type=float, default=0.25, help='Gamma da Kernel PCA')
    parser.add_argument('--perplexidade', type=float, default=30)
    parser.add_argument('--vizinhos', type=int, default=15)
    parser.add_argument('--min-dist', type=float, default=0.1)
    args = parser.parse_args()
    if args.questao in ('1', 'todas'):
        executar_questao_1(not args.sem_padronizar, args.eps, args.min_samples)
    if args.questao in ('2', 'todas'):
        executar_questao_2(not args.sem_padronizar, args.seed, args.gamma,
                          args.perplexidade, args.vizinhos, args.min_dist)


if __name__ == '__main__':
    main()
