# Quantum ESPRESSO 7.4.1（富岳）

指定された builtin の `package.py` を基に、必要箇所だけを修正しています。
クラス構成（`CMakePackage, Package`）、variant、依存関係、
`GenericBuilder.install()` の処理を維持しています。

builtin からの変更は次のとおりです。

- バージョン宣言を 7.4.1 に限定。
- 旧レシピと同じ `make all epw` → `make install` を使うため、
  build_system のデフォルトを `generic` に変更。
- `target=a64fx %fj` で旧レシピの最適化フラグ、BEEF、
  `--host=aarch64-linux-gnu`、逐次 make を設定。
  MPI・ScaLAPACK・FFTW などの定義は configure に任せ、builtin の variant と連動。
- builtin が扱っていない Fujitsu FFTW の include・リンク行を、
  仮想依存 `fftw-api` の spec から取得。
- Fujitsu FFTW / SSL II が選ばれた場合だけ、対応する MPI / OpenMP variant を要求。
- 旧富岳用の 3 修正を `fugaku-7.4.1.patch` として公式ソースへ移植。
  builtin の古い FoX パッチを 7.4.1 に適用しないよう条件を修正。

MPI・BLAS・LAPACK・ScaLAPACK・FFTW の依存宣言は builtin と同じ
`mpi`、`blas`、`lapack`、`scalapack`、`fftw-api@3` です。
プロバイダは固定していません。BLAS / LAPACK / ScaLAPACK のリンク行も
builtin と同じく、選択された仮想依存の `.libs` から取得します。
旧レシピの `-SSL2MPI` などを QE レシピへ直接指定する処理は外しています。

旧構成を選ぶ指定例です。富岳計算ノード用の Spack 環境で利用してください。

```sh
spack install fugaku.local.quantum-espresso@7.4.1 build_system=generic \
    target=a64fx +mpi+openmp+scalapack+epw %fj \
    ^fujitsu-mpi ^fujitsu-ssl2+parallel \
    ^fujitsu-fftw+mpi+openmp precision=double
```

外部ソースの取得方法も builtin と同じです。前回追加した resource とその配置処理は削除しました。
追加した `fugaku-7.4.1.patch` 以外の builtin 由来のパッチファイルは、変更せず同梱しています。

ログインノードではレシピの読み込み、生成される引数と依存宣言、
7.4.1 ソースへのパッチ適用を確認します。
`spack spec` / concretize、A64FX 用コードのビルド・実行は行っていません。
実ビルド・計算結果の確認は計算ノード上で必要です。
