# pocker-cli
`docker ps`や`docker images`をもっと見やすくするpython製のツール

---
## アイデア
下記のコマンドを実装したい

```bash
# docker ps をテーブル表示にして見やすく
$ pocker ps
# ↑のall版。allつけたときだけ表示されているものの区別をつける
$ pocker ps -a
# pocker ps のimages版。
$ pocker images
# pocker ps -a のimages版。
$ pocker images -a
```

---
## 参考になりそうなサイト

### テーブル表示
https://vaaaaaanquish.hatenablog.com/entry/2018/05/03/231201
