# 概要
　このツールは、ポケットモンスタースカーレット・バイオレット(Nintendo Switch)のゲーム画面を読み込むことで、対戦時の相手ポケモンのタイプや種族値といったステータス情報を簡易的に取得・表示することを可能にする。  
　加えて、外部サイトの[ポケモン徹底攻略](https://yakkun.com/ "ポケモン徹底攻略")、[ポケモンバトルデータベース](https://sv.pokedb.tokyo/ "ポケモンバトルデータベース")へのアクセスを容易にすることで、ポケモン対戦時にプレイヤーが行っている相手ポケモンの分析を補助する。

## イメージ動画(Youtbe)
[![用イメージ動画](http://img.youtube.com/vi/CFl7r83tzaI/hqdefault.jpg)](https://youtu.be/CFl7r83tzaI)
# 使用技術
## 画像認識
### [dHash方式によるポケモン画像判別](https://note.com/kaseki_mtg/n/n6df12de8981a "openCVでdHash方式のポケモン画像判別")
- 通信対戦時の選出画面で、相手ポケモン一覧から個々のポケモンの画像を切り出す
- 二値変換を行い白黒画像に変換する
- Hash値を算出し、各ポケモンのHash値DBに照合、類似するポケモンの情報を取得

|選出画面|輪郭切り抜き|二値変換|リサイズ(9x8)
|:-:|:-:|:-:|:-:|
|<img src="https://github.com/ando1912/PkBattleTool/assets/127027317/30ce9525-4554-4e40-b063-226407d6a881" width="200">|![240114002603_2](https://github.com/ando1912/PkBattleTool/assets/127027317/a826e125-efb6-41d9-a8da-c7a49d64efd1)|![240114002603_2](https://github.com/ando1912/PkBattleTool/assets/127027317/08b8d76e-cc4e-4967-9536-de007aba4036)|![20240409141105](https://github.com/ando1912/PkBattleTool/assets/127027317/60de3b37-128a-4ecd-9e67-92993ef7eeb6)

# 使用するライブラリ
1. GUI系
   - tkinter
2. 画像処理
   - pandas
   - PIL
   - opencv2
   - numpy
   - matplotlib
   - re
3. 外部アクセス
   - webbrowser
4. システム系
   - threading
   - logging
   - datetime

# プログラムの構成について
工事中

# Todo
- [ ] 各プログラムの概要
- [ ] 残存課題の洗い出し
- [ ] 実装したい内容の書き出し
