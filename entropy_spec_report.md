# Digraph Entropy Calculation Analysis Report

## 概要
本レポートは，`digraph-inout-analysis` リポジトリにおける有向グラフのエントロピー計算の仕様（`AGENTS.md`）と，その実装（`src/digraph_inout_analysis/core.py`）の対応関係を数理的観点から整理したものです．
（※ユーザーの指摘に基づき，実装ロジックを修正・再確認した最新版です）

## 1. エントロピー計算の数理的仕様

有向グラフ上の**各エッジ**に対して，以下の手順でエントロピーを定義・計算します．

### 記号の定義
- $G = (V, E)$: 有向グラフ
- $A \to B$: 着目している有向辺
- $w_{AB}$: 辺 $A \to B$ の重み（入力の強さ）
- $\{C_i\}$: ノード $B$ から遷移する先のノード群
- $w_{BC_i}$: 辺 $B \to C_i$ の重み（出力の強さ）

### Step 1: 遷移確率的指標の計算
有向辺 $A \to B$ の重み $w_{AB}$ を基準（分母）として，ノード $B$ からの各出力方向への強さの比率を計算します．

$$ r_i(A \to B) = \frac{w_{BC_i}}{w_{AB}} $$

この $r_i$ は確率（総和が1）になるとは限りませんが，次のステップで分布の形状として評価されます．

### Step 2: Shannon Entropy の計算
各辺 $A \to B$ に割り当てるエントロピー $H(A \to B)$ は，上記の比率の分布 $\{r_i\}_i$ の Shannon entropy として定義されます．計算時には正規化が行われます．

$$ p_i = \frac{r_i}{\sum_k r_k} = \frac{w_{BC_i}}{\sum_k w_{BC_k}} $$
$$ H(A \to B) = - \sum_{i} p_i \log_2 p_i $$

> **Note**: 数学的には，Shannon entropy の計算過程で正規化（$\sum p=1$）を行う場合，分母の $w_{AB}$ はキャンセルされ，結果的に「$B$ からの出力重みの分布」のエントロピーと一致します．しかし，意味論として「$A$ からの入力 $w_{AB}$ が $B$ でどのように分散するか」を評価している構造になっています．

## 2. 実装との対応

Python モジュール `src/digraph_inout_analysis/core.py` 内の `calculate_io_entropy` 関数は，以下の通り実装されています．

### コード詳細

```python
def calculate_io_entropy(G):
    # 事前に全ノードの出力重みを取得
    node_out_weights = {}
    for node in G.nodes():
        node_out_weights[node] = [weight for ... in out_edges(node)]

    # 全エッジ(u->v)について個別に計算
    for u, v, data in G.edges(data=True):
        # [分母] 着目しているエッジの重み in_weight = w_uv
        in_weight = data['weight']
        
        # [分子] 遷移先の重みリスト out_weights = {w_vCi}
        out_weights = node_out_weights[v]
            
        # [比率計算]
        probs = [w / in_weight for w in out_weights]
        
        # [エントロピー計算]
        # scipy.stats.entropy により自動正規化され計算される
        data['entropy'] = entropy(probs, base=2)
        
    return G
```

### 修正のポイント
以前の実装では「ノード $B$ ごとに In-Degree 総和を分母として計算し，それを全ての入ってくる辺にコピーする」というアプローチでしたが，現在の実装では**「各エッジ $A \to B$ ごとに，そのエッジの重みを分母として計算する」**形に厳密に修正されました．これにより，$A$ からの入力に対する依存関係がコード上で明確になっています．
