"""Gera tabelas e figuras do artigo a partir dos resultados experimentais."""
import json
import os
from pathlib import Path
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MPLCONFIGDIR', '/tmp/matplotlib-artigo')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.metrics.pairwise import rbf_kernel
from umap.umap_ import find_ab_params

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/artigo'
FIG = OUT / 'figuras/ieee'
RESULTADOS = ROOT / 'resultados'
TUNAGEM = RESULTADOS / 'tunagem'
q = json.loads((RESULTADOS / 'execucoes_questao_1.json').read_text())
p = json.loads((RESULTADOS / 'execucoes_questao_2.json').read_text())
metadados = json.loads((RESULTADOS / 'metadados_questao_1.json').read_text())
m = pd.read_csv(RESULTADOS / 'metricas_por_k.csv')
resumo = pd.read_csv(RESULTADOS / 'resumo_agrupamentos.csv')
particionais = pd.read_csv(TUNAGEM / 'particionais.csv')
dbscan = pd.read_csv(TUNAGEM / 'dbscan.csv')
mesma_amostra = pd.read_csv(TUNAGEM / 'comparacao_mesma_amostra.csv')
df = pd.read_csv(ROOT / 'codigo/iris/iris.data', header=None).dropna(how='all')
X = df.iloc[:, :4].to_numpy()
if metadados['preprocessamento']['padronizado']:
    X = StandardScaler().fit_transform(X)

NOMES = dict(zip(
    ['k-means', 'fuzzy-k-means', 'kernel-fuzzy-k-means', 'k-medoids',
     'gaussian-mixture', 'upgma', 'dbscan'],
    ['K-Means', 'FCM', 'Kernel FCM', 'K-Medoids', 'GMM/EM', 'UPGMA', 'DBSCAN'],
))


def fmt(x, casas=4):
    return '—' if pd.isna(x) else f'{x:.{casas}f}'.replace('.', ',')


def resumir_parametros(nome, p):
    if nome in {'k-means', 'k-medoids'}:
        return p['init']
    if nome == 'fuzzy-k-means':
        return f"m = {p['m']:g}".replace('.', ',')
    if nome == 'kernel-fuzzy-k-means':
        return f"m = {p['m']:g}; γ = {p['gamma']:g}".replace('.', ',')
    if nome == 'gaussian-mixture':
        return f"{p['covariance_type']}; reg = {p['reg_covar']:g}"
    if nome == 'upgma':
        return 'ligação média, Manhattan'
    return f"ε = {fmt(p['eps'], 3)}; min_samples = {p['min_samples']}"


def best(name, k):
    semente = m[(m.algoritmo == name) & (m.k == k)].iloc[0].seed
    return next(run for run in q[name][str(k)] if run['parametros']['seed'] == semente)


r = {'pca_singular_values': p['pca']['valores_singulares'], 'pca_mean': p['pca']['media']}
r['agrupamento'] = {
    'contagens': {k: metadados['tunagem'][k] for k in
                  ['ajustes_particionais', 'ajustes_dbscan', 'ajustes_totais',
                   'cobertura_minima_dbscan_pct']},
    'resumo': [], 'mesma_amostra': [], 'por_k': [], 'sensibilidade_k3': [],
}
g = r['agrupamento']
rotulos = {}
for linha in resumo.to_dict('records'):
    nome = linha['Algoritmo']
    n = int(linha['Amostras avaliadas'])
    k = int(linha['Clusters']) if nome == 'dbscan' else int(linha['k*'])
    if nome == 'dbscan':
        resultado = q[nome]
    elif nome == 'upgma':
        resultado = q[nome][str(k)]
    else:
        resultado = best(nome, k)
    rotulos[nome] = np.asarray(resultado['rotulos'])
    g['resumo'].append([NOMES[nome], resumir_parametros(nome, resultado['parametros']), str(k),
                        fmt(linha['Silhueta']), fmt(linha['ARI']), str(n)])

    mesma = mesma_amostra[mesma_amostra.algoritmo == nome].iloc[0]
    g['mesma_amostra'].append([NOMES[nome], fmt(mesma.silhueta), fmt(mesma.ari),
                              fmt(mesma.ari_com_dbscan)])
    if nome == 'dbscan':
        continue

    linhas_k = m[(m.algoritmo == nome) & (m.k > 1)].sort_values('k')
    g['por_k'].append([NOMES[nome], *[f'{fmt(x.silhueta)} / {fmt(x.ari)}'
                                     for x in linhas_k.itertuples()]])
    if nome in set(particionais.algoritmo):
        candidatas_k3 = particionais[(particionais.algoritmo == nome) & (particionais.k == 3)]
        validas = candidatas_k3.dropna(subset=['silhueta']).sort_values('silhueta')
        extremos = [validas.iloc[0], validas.iloc[-1]]
        g['sensibilidade_k3'].append([
            NOMES[nome],
            *[f'{resumir_parametros(nome, linha)} ({fmt(linha.silhueta)})'
              for linha in extremos],
            f'{fmt(candidatas_k3.ari.min())} a {fmt(candidatas_k3.ari.max())}',
        ])

grade_kernel = particionais[particionais.algoritmo.eq('kernel-fuzzy-k-means')]
kernel_selecionado = grade_kernel[grade_kernel.configuracao_selecionada].sort_values('k')
kernel_referencia = grade_kernel[grade_kernel.referencia].iloc[0]
g['selecao_kernel_fcm'] = {
    'perfis': int(grade_kernel.configuracao.nunique()),
    'm': fmt(kernel_selecionado.m.iloc[0], 1).removesuffix(',0'),
    'gamma': fmt(kernel_selecionado.gamma.iloc[0], 2),
    'silhuetas': [fmt(valor) for valor in kernel_selecionado.silhueta],
    'media': fmt(kernel_selecionado.silhueta_media.iloc[0]),
    'gamma_referencia': fmt(kernel_referencia.gamma, 2),
    'media_referencia': fmt(kernel_referencia.silhueta_media),
}

comparacoes = [
    ('k-means', 3, 'init', 'Inicialização', {}),
    ('fuzzy-k-means', 4, 'm', 'm', {}),
    ('kernel-fuzzy-k-means', 4, 'm', 'm', {'gamma': 0.05}),
    ('kernel-fuzzy-k-means', 4, 'gamma', 'γ', {'m': 2}),
    ('k-medoids', 3, 'init', 'Inicialização', {}),
    ('gaussian-mixture', 3, 'covariance_type', 'Covariância', {'reg_covar': 1e-2}),
    ('gaussian-mixture', 3, 'reg_covar', 'Regularização', {'covariance_type': 'full'}),
]
nomes_parametros = {'gamma': 'γ', 'm': 'm', 'reg_covar': 'reg.', 'covariance_type': 'cov.'}
g['sensibilidade_particionais'] = []
for nome, k, parametro, rotulo, fixos in comparacoes:
    linhas = particionais[particionais.algoritmo.eq(nome) & particionais.k.eq(k)]
    for chave, valor in fixos.items():
        linhas = linhas[linhas[chave].eq(valor)]
    if parametro in {'m', 'gamma', 'reg_covar'}:
        linhas = linhas.sort_values(parametro)
        valores = [f'{valor:g}'.replace('.', ',') for valor in linhas[parametro]]
    else:
        valores = linhas[parametro].tolist()
    condicoes = [f'k = {k}']
    for chave, valor in fixos.items():
        valor_formatado = f'{valor:g}'.replace('.', ',') if isinstance(valor, (int, float)) else valor
        condicoes.append(f'{nomes_parametros[chave]} = {valor_formatado}')
    g['sensibilidade_particionais'].append([
        NOMES[nome], ', '.join(condicoes), rotulo, valores,
        [fmt(valor) for valor in linhas.silhueta],
        [fmt(valor) for valor in linhas.ari],
    ])

escolhida = dbscan[dbscan.selecionado].iloc[0]
mais_alta = dbscan.dropna(subset=['silhueta']).sort_values(
    ['silhueta', 'cobertura_pct'], ascending=False).iloc[0]
base_dbscan = dbscan[np.isclose(dbscan.eps, .8) & dbscan.min_samples.eq(5)].iloc[0]
raio_relativo = dbscan[dbscan.fator.eq(1.5)]
mais_vizinhos = raio_relativo[raio_relativo.min_samples.eq(5)].iloc[0]
raio_maior = dbscan[dbscan.eps.eq(.8) & dbscan.min_samples.eq(3)].iloc[0]
g['dbscan'] = {
    'eps': fmt(escolhida.eps, 3), 'min_samples': int(escolhida.min_samples),
    'cobertura': fmt(escolhida.cobertura_pct, 2), 'n': int(escolhida.amostras_avaliadas),
    'ruido': int(escolhida.ruido), 'grupos': int(escolhida.grupos),
    'silhueta': fmt(escolhida.silhueta), 'ari': fmt(escolhida.ari),
    'tabela': [[nome, fmt(linha.eps, 6 if linha.regra == 'eps_relativo' else 1),
                str(linha.min_samples), str(linha.grupos),
                fmt(linha.cobertura_pct, 2), fmt(linha.silhueta), fmt(linha.ari)]
               for nome, linha in [('Escolhida', escolhida), ('Referência', base_dbscan),
                                  ('Maior Sil', mais_alta), ('Mesmo raio', mais_vizinhos),
                                  ('Mesmo mínimo', raio_maior)]],
}
g['amostra_igual'] = bool(mesma_amostra.ari_com_dbscan.eq(1).all())
g['particao_comum'] = all(
    adjusted_rand_score(rotulos['k-means'], rotulo) == 1
    for nome, rotulo in rotulos.items() if nome != 'dbscan'
)
g['estrutura_setosa'] = adjusted_rand_score(
    df.iloc[:, 4] == 'Iris-setosa', rotulos['k-means']
) == 1
gmm_k3 = m[(m.algoritmo == 'gaussian-mixture') & (m.k == 3)].iloc[0]
maior_ari_k3 = m[m.k == 3].sort_values('ari', ascending=False).iloc[0]
g['em_k3'] = {'silhueta': fmt(gmm_k3.silhueta), 'ari': fmt(gmm_k3.ari)}
g['maior_ari_k3'] = {'nome': NOMES[maior_ari_k3.algoritmo], 'ari': fmt(maior_ari_k3.ari)}
r['upgma_manhattan'] = {k: silhouette_score(X, q['upgma'][str(k)]['rotulos'], metric='manhattan') for k in range(2,6)}
a, b = find_ab_params(1., .1)
z = np.array(p['umap']['coordenadas'])
r['umap'] = {'shape': list(z.shape), 'min': z.min(axis=0).tolist(), 'max': z.max(axis=0).tolist(), 'a': a, 'b': b}
K = rbf_kernel(X, gamma=.25)
Kc = K - K.mean(axis=0)[None,:] - K.mean(axis=1)[:,None] + K.mean()
eig = np.linalg.eigvalsh(Kc)
assert eig.min() > -1e-10
r['kernel_pca'] = {'trace': np.trace(Kc), 'fractions': (np.array(p['kernel_pca']['autovalores'])/np.trace(Kc)).tolist()}
r['fuzzy_same_partition_k3'] = adjusted_rand_score(best('fuzzy-k-means',3)['rotulos'],best('kernel-fuzzy-k-means',3)['rotulos']) == 1
(OUT/'diagnosticos_revisao.json').write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
plt.rcParams.update({'font.family':'serif','font.size':8,'axes.formatter.use_mathtext':False})
fmt = FuncFormatter(lambda x,pos:f'{x:g}'.replace('.',','))
def finish(fig,ax,name):
    ax.xaxis.set_major_formatter(fmt); ax.yaxis.set_major_formatter(fmt)
    fig.tight_layout(pad=.6); fig.savefig(FIG/name); plt.close(fig)
fig,ax=plt.subplots(figsize=(3.45,2.6))
for (name,rows), marker in zip(m.groupby('algoritmo',sort=False),['o','s','^','v','D','x']):
    ax.plot(rows.k,rows.silhueta,marker=marker,label=NOMES[name],lw=.9,ms=3)
ax.set(xlabel='Número de grupos (k)',ylabel='Silhueta média',xticks=range(1,6))
ax.legend(ncol=2,fontsize=6.5); ax.grid(alpha=.2)
finish(fig,ax,'silhuetas_comparadas.pdf')
Z=np.array(q['upgma']['2']['hierarquia'])
fig,ax=plt.subplots(figsize=(3.45,2.5))
dendrogram(Z,truncate_mode='lastp',p=12,show_leaf_counts=True,leaf_label_func=lambda node: f'({int(Z[node-len(X),3])})' if node >= len(X) else '(1)',leaf_rotation=90,leaf_font_size=7,ax=ax,color_threshold=0,above_threshold_color='#2676a1')
for k,col in [(2,'#b32c34'),(3,'#438745')]:
    height=(Z[-k,2]+Z[-k+1,2])/2
    ax.axhline(height,ls='--',lw=.8,color=col,label=f'corte k = {k}')
ax.set(xlabel='Subárvores (contagens entre parênteses)',ylabel='Distância Manhattan'); ax.legend(fontsize=6)
ax.yaxis.set_major_formatter(fmt)
fig.tight_layout(pad=.6); fig.savefig(FIG/'dendrograma_upgma.pdf'); plt.close(fig)
for name in ['pca','kernel_pca','tsne','umap']:
    d=pd.read_csv(ROOT/f'resultados/coordenadas_{name}.csv')
    fig,ax=plt.subplots(figsize=(3.45,2.35))
    for species,color,marker in zip(d.especie.unique(),['#2676a1','#c55b26','#438745'],['o','x','s']):
        sub=d[d.especie==species]
        ax.scatter(sub.componente_1,sub.componente_2,s=9,c=color,marker=marker,label=species.replace('Iris-',''),linewidths=.5)
    ax.set(xlabel='Componente 1',ylabel='Componente 2')
    if name=='pca': ax.set(xlabel='PC1 (72,77%)',ylabel='PC2 (23,03%)')
    ax.legend(fontsize=6.5); ax.grid(alpha=.15)
    finish(fig,ax,f'{name}.pdf')
print(json.dumps(r,ensure_ascii=False,indent=2))
