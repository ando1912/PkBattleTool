ポケモン対戦支援ツール

---
# 概要
- ポケモンSVの対戦画面を読み込み、相手の手持ちポケモンの情報を簡単に表示できる対戦支援ツール
- [ポケモンバトルデータベース](https://sv.pokedb.tokyo/ "ポケモンバトルデータベース")へのアクセスを簡略化し、プレイヤー自身で調べる手間を減らす

[![用イメージ動画](http://img.youtube.com/vi/CFl7r83tzaI/hqdefault.jpg)](https://youtu.be/CFl7r83tzaI)

# 開発環境
- Python 3.11.9
- Anaconda

## 環境構築
```console
cd pkbattletool
pip install -r requirements.txt
```

## 実行
```concole
python main.py
```

---
# 使用技術
## 画像認識
### [dHash方式によるポケモン画像判別](https://note.com/kaseki_mtg/n/n6df12de8981a "openCVでdHash方式のポケモン画像判別")
1. 相手の手持ち選出画面を切り抜く
2. 各ポケモンを切り抜く
3. 二値変換を行う
4. 9x8サイズにリサイズする
5. Hash値を求める
6. DBと照合し、Hash値が類似するポケモンを調べる

|選出画面|輪郭切り抜き|二値変換|リサイズ(9x8)|Hash|
|:-:|:-:|:-:|:-:|:-:|
|<img src="https://github.com/ando1912/PkBattleTool/assets/127027317/30ce9525-4554-4e40-b063-226407d6a881" width="200">|![240114002603_2](https://github.com/ando1912/PkBattleTool/assets/127027317/a826e125-efb6-41d9-a8da-c7a49d64efd1)|![240114002603_2](https://github.com/ando1912/PkBattleTool/assets/127027317/08b8d76e-cc4e-4967-9536-de007aba4036)|![20240409141105](https://github.com/ando1912/PkBattleTool/assets/127027317/60de3b37-128a-4ecd-9e67-92993ef7eeb6)|F0 28 B0 F1 E6 F0 F0 F1|

---
# これから開発したいなーと思ってること
- 画像認識精度のブラッシュアップ
  - 選出画面アイコンでの判別から、3Dグラフィックからの画像認識へ
- ユーザーのソフトウェア操作の削減
  - 盤面に出ているポケモンの判別で、自動的に情報を表示
- 相手パーティーの分析
  - パーティー構築の予測を出せるようにしたい
