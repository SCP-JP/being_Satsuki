﻿# 開発版SCP-JP用Bot : Tachibana

ここは、製作者の不手際と知識不足で肥大化してしまったsatsukiを再構成するための開発版Bot、Tachibanaの開発のための場です。

## 何を目的とするか？
そもそも専門が情報系でないSatsukiの製作者は公式リファレンスを読み落とし前述の通り、非効率的なソースコードを書いてしまっています。このため、これを再構成し効率の良いシステムを構築し、開発効率を高め、効率性と冗長性を確保するためにgithubを利用するものです。  
完成し次第、Satsukiにソースコードを移設します。

### いいわけ
参考にしたコードが小規模のものであった＋そもそもBot開発を始めたのがasync版であったため、動きはするが正しくないシステムになってしまいました。このため本来の機能が使えない、新機能の追加に手間取る、コマンドに持たせる事ができるはずの機能が実装できないなどの問題が発生しています。これを解消するためにSatsuki本体を、発生してくるバグや仕様変更などに対応しつつ根本的な構造を直していくことは容易ではないので、１から書き直してしまおうというのがこのプロジェクトです。

## 現在の状況について

見ての通りTachibana本体にはまだ手を付けていません。ゆっくり開発していきます。

### ayame
~~2019-05-29:現在、改修が終わっているのはデータベース更新プログラムであるAyameのみです。これは現在のSatsukiでは細かく分割しているCSVをそれぞれ1つにまとめたものです。これにより検索を実装することを容易にしました。~~

2019-06-22:記事について対応しました。また、国コードを変換することが可能になりました。

### data
データやログを入れる場所です

## その他
もとから試験実装の役割についていたもう一つのBot、Tachibanaの名前をこのプロジェクトに引き継がせます。Discordbotのシステム上、tokenの漏洩は絶対に避けなくてはならないためリポジトリ自体を分割することにしました。しかし、製作者である私がしばらく多忙なため、更新はゆっくりになるかと思います。（そもそもSatsuki優先です）

## ライセンス
ロゴ画像の素材はこちらからお借りしました。  
提供元：http://scp-jp-archive.wdfiles.com/local--resized-images/foundation-universe/Internal%20department2.png/small.jpg  
作者：Nanimono Demonai さん  

Tachibana ©︎︎ being241 2019 CC BY-SA 3.0


## 参考文献
https://discordpy.readthedocs.io/ja/latest/index.html#  
https://qiita.com/Lazialize/items/81f1430d9cd57fbd82fb
