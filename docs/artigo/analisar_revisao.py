"""Diagnósticos complementares; preserva as execuções do protocolo principal."""
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
from sklearn.cluster import KMeans, DBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.metrics.pairwise import rbf_kernel
from umap.umap_ import find_ab_params

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/artigo'
FIG = OUT / 'figuras/ieee'
q = json.loads((ROOT / 'resultados/execucoes_questao_1.json').read_text())
p = json.loads((ROOT / 'resultados/execucoes_questao_2.json').read_text())
df = pd.read_csv(ROOT / 'codigo/iris/iris.data', header=None).dropna(how='all')
X = StandardScaler().fit_transform(df.iloc[:, :4])
y = df.iloc[:, 4]
def best(name, k):
    return (max if name == 'gaussian-mixture' else min)(q[name][str(k)], key=lambda r:r['objetivo'])
r = {'pca_singular_values': p['pca']['valores_singulares'], 'pca_mean': p['pca']['media']}
r['upgma_manhattan'] = {k: silhouette_score(X, q['upgma'][str(k)]['rotulos'], metric='manhattan') for k in range(2,6)}
a, b = find_ab_params(1., .1)
z = np.array(p['umap']['coordenadas'])
r['umap'] = {'shape': list(z.shape), 'min': z.min(axis=0).tolist(), 'max': z.max(axis=0).tolist(), 'a': a, 'b': b}
K = rbf_kernel(X, gamma=.25)
Kc = K - K.mean(axis=0)[None,:] - K.mean(axis=1)[:,None] + K.mean()
eig = np.linalg.eigvalsh(Kc)
assert eig.min() > -1e-10
r['kernel_pca'] = {'trace': np.trace(Kc), 'fractions': (np.array(p['kernel_pca']['autovalores'])/np.trace(Kc)).tolist()}
km = KMeans(n_clusters=3, init='random', n_init=100, random_state=42).fit(X)
r['kmeans_sensitivity'] = {'n_init':100, 'seed':42, 'objective':km.inertia_, 'ari':adjusted_rand_score(y,km.labels_), 'silhouette':silhouette_score(X,km.labels_)}
r['fuzzy_same_partition_k3'] = adjusted_rand_score(best('fuzzy-k-means',3)['rotulos'],best('kernel-fuzzy-k-means',3)['rotulos']) == 1
r['gmm'] = {}
for k in range(1,6):
    old = best('gaussian-mixture',k)
    model = GaussianMixture(n_components=k, covariance_type='full', random_state=old['parametros']['seed'], tol=1e-5, reg_covar=1e-6, n_init=1, init_params='random_from_data').fit(X)
    assert np.isclose(model.score(X)*len(X), old['objetivo'])
    r['gmm'][k] = {'weights':model.weights_.tolist(), 'counts':np.bincount(model.predict(X),minlength=k).tolist(), 'bic':model.bic(X), 'min_cov_eigenvalues':np.linalg.eigvalsh(model.covariances_).min(axis=1).tolist()}
r['dbscan'] = []
for eps in [.6,.7,.8,.9,1.]:
    labels = DBSCAN(eps=eps,min_samples=5).fit_predict(X)
    mask = labels != -1
    groups = len(set(labels[mask]))
    r['dbscan'].append({'eps':eps,'groups':groups,'noise':int((~mask).sum()),'silhouette':silhouette_score(X[mask],labels[mask]) if groups>1 else None})
(OUT/'diagnosticos_revisao.json').write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
plt.rcParams.update({'font.family':'serif','font.size':8,'axes.formatter.use_mathtext':False})
fmt = FuncFormatter(lambda x,pos:f'{x:g}'.replace('.',','))
def finish(fig,ax,name):
    ax.xaxis.set_major_formatter(fmt); ax.yaxis.set_major_formatter(fmt)
    fig.tight_layout(pad=.6); fig.savefig(FIG/name); plt.close(fig)
m = pd.read_csv(ROOT/'resultados/metricas_por_k.csv')
names = ['K-Means','FCM','Kernel FCM','K-Medoids','GMM/EM','UPGMA']
fig,ax=plt.subplots(figsize=(3.45,2.6))
for (name,rows), label, marker in zip(m.groupby('algoritmo',sort=False),names,['o','s','^','v','D','x']):
    ax.plot(rows.k,rows.silhueta,marker=marker,label=label,lw=.9,ms=3)
ax.axvline(2,ls='--',color='gray',lw=.8)
ax.set(xlabel='Número de grupos (k)',ylabel='Silhueta média',xticks=range(1,6),ylim=(.1,.64))
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
