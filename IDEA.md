# やりたいこと
* プロンプトを入力し、ジョブ投入する
* 実行するとSTLとプレビューが出来上がる
* 結果を見てプロンプトを入力して再編集ができる
  * 3Dプリンタへの投入もできる（後日拡張）

# 構成案
* gemini CLIをwebから叩く
* OpenSCADのファイルを生成してもらう
  * OPENSCAD_PROMPT.mdも参照のこと
* openscad_mcpを用いてrenderする
  * なお、任意視点からのrenderの追加など、openscad_mcp側の拡張リクエストを出すのもOK。