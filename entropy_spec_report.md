# Digraph Entropy Calculation Analysis Report

## 概要
本レポートは，`digraph-inout-analysis` リポジトリにおける有向グラフのエントロピー計算の仕様（`AGENTS.md`）と，その実装（`src/digraph_inout_analysis/core.py`）の対応関係を数理的観点から整理したものです．
（※ユーザーの指摘に基づき，2階マルコフ過程（条件付き確率）に基づく実装へ修正した最終版です）

## 1. エントロピー計算の数理的仕様

単純なノード間の遷移確率（1階マルコフ過程）ではなく，**「どこから来たか」の履歴を考慮した条件付き確率**（2階マルコフ過程）に基づいてエントロピーを計算します．

### 記号の定義
- $X_t$: 時刻 $t$ における状態（ノード）
- $A \to B \to C$: 連続する3つの状態遷移（$X_{t-1}=A, X_t=B, X_{t+1}=C$）
- $Count(A \to B)$: 遷移 $A \to B$ の観測回数
- $Count(A \to B \to C)$: 軌道 $A \to B \to C$ の観測回数

### Step 1: 条件付き確率分布の計算
「現在 $B$ にいて，かつ直前に $A$ から遷移してきた」という条件の下で，次に $C_i$ へ遷移する確率 $P(C_i | B, A)$ を推定します．

$$ P(C_i | B, A) = P(X_{t+1}=C_i \mid X_t=B, X_{t-1}=A) \approx \frac{Count(A \to B \to C_i)}{\sum_{k} Count(A \to B \to C_k)} $$

### Step 2: Shannon Entropy の計算
各有向辺 $A \to B$ に対して，この条件付き確率分布のエントロピーを計算し，割り当てます．

$$ H(A \to B) = - \sum_{i} P(C_i | B, A) \log_2 P(C_i | B, A) $$

これにより，同じノード $B$ に到達する辺であっても，前状態（$A$ vs $X$）によって次の挙動予測の不確実性が異なる場合，それぞれ異なるエントロピー値が付与されます．

## 2. 実装詳細

### データ構造の拡張
`networkx.DiGraph` のエッジ属性として，単純な重みだけでなく，次のステップへのカウント情報を保持します．

- Edge $(u, v)$ attributes:
    - `'weight'`: $Count(u \to v)$
    - `'next_counts'`: 辞書 `{w: count}`．$Count(u \to v \to w)$ を保持．

### アルゴリズム (`src/digraph_inout_analysis/core.py`)

1.  **グラフ構築 (`build_transition_digraph`)**:
    与えられた単語列から3連続の並び（トリプレット）$(u, v, w)$ を走査し，エッジ $u \to v$ の `next_counts` 属性に $w$ の出現回数を加算記録します．

2.  **エントロピー計算 (`calculate_io_entropy`)**:
    各有向辺 $u \to v$ について：
    -   `next_counts` を取得（分布 $\{Count(u \to v \to w)\}_w$）．
    -   `scipy.stats.entropy` を用いてエントロピーを計算．
    -   結果を属性 `entropy` として保存．

### 検証結果
検証スクリプト (`examples/simple_entropy_check.py`) により，以下の挙動を確認済みです．
- パターン1: $A \to B \to C$
- パターン2: $X \to B \to D$
この2つのフローが混在する場合：
- 従来手法（1階）：$B$ からの分岐は $C, D$ のランダム遷移とみなされ，エントロピーは 1.0 bit．
- **現在手法（2階）**:
    - $A \to B$ の次は必ず $C$ であるため，エントロピーは **0.0 bit**．
    - $X \to B$ の次は必ず $D$ であるため，エントロピーは **0.0 bit**．

文脈依存の決定論的な遷移を正しく「不確実性ゼロ」として評価できています．
