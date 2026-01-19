# Text-to-STL Generator 設計書

## 1. 概要
`IDEA.md` に基づき、テキストプロンプトからOpenSCADコードを生成し、STLファイルとプレビュー画像を出力するWebアプリケーションを構築する。

## 2. システム構成

### 2.1 アーキテクチャ
*   **Frontend / UI**: [Streamlit](https://streamlit.io/) (Python)
    *   迅速なUI構築、対話的なデータフロー、画像の表示に適しているため採用。
*   **LLM Engine**: Google Gemini API (`google-generativeai`)
    *   OpenSCADコードの生成を担当。
*   **3D Engine**: OpenSCAD CLI
    *   ローカル環境にインストールされた `openscad` コマンドを利用し、レンダリング (`.png`) と エクスポート (`.stl`) を行う。

### 2.2 データフロー
1.  **Input**: ユーザーがWeb UIで「作りたい形状」を入力。
2.  **Prompting**: アプリケーションが `OPENSCAD_PROMPT.md` の内容とユーザー入力を結合し、Geminiへの命令を作成。
3.  **Generation**: Gemini APIが `.scad` コードを生成。
4.  **Extraction**: レスポンスから `.scad` コードブロックを抽出・保存。
5.  **Rendering**:
    *   `openscad -o preview.png model.scad` を実行し、プレビュー画像を生成。
    *   `openscad -o output.stl model.scad` を実行し、STLファイルを生成。
6.  **Output**: Web UIにプレビュー画像を表示し、STLおよびSCADファイルのダウンロードリンクを提供する。

## 3. ディレクトリ構成案

```text
.
├── app.py                # Streamlit アプリケーション本体
├── generator.py          # Gemini API との通信・コード抽出ロジック
├── renderer.py           # OpenSCAD コマンドライン実行ラッパー
├── requirements.txt      # 依存ライブラリ
├── OPENSCAD_PROMPT.md    # システムプロンプト（既存）
└── output/               # 生成物の一時保存場所
    ├── model.scad
    ├── preview.png
    └── output.stl
```

## 4. 機能要件

*   **プロンプト入力**: テキストエリアによる自由入力。
*   **ジョブ実行**: 「Generate」ボタンで処理開始。
*   **結果表示**:
    *   生成されたSCADコードの表示（編集可能にすると尚良しだが、まずは表示のみ）。
    *   3Dプレビュー（静止画 PNG）。
*   **ダウンロード**: STLファイル、SCADファイルのダウンロードボタン。
*   **履歴管理（将来拡張）**: 過去の生成物の保存と参照。

## 5. 必要な準備
*   Google Gemini API Key の設定（環境変数 `GEMINI_API_KEY` または `.env` ファイル）。
*   OpenSCAD のインストール（確認済み: `version 2021.01`）。
