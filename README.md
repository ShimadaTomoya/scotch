# ■ Scotch
Scotch は webクロールフレームワークです。<br>

# ■ Quick Start

pipenvをインストールします。<br>
```bash
pip install pipenv
```

example プロジェクトを実行<br>
```bash
cd scotch
pipenv run crawl example > log/result.tsv
```

example プロジェクトを中断して再開<br>
```bash
<ctrl + c>
pipenv run crawl example --continue >> log/result.tsv
```

# ■ Create New Project
## ◎ example プロジェクトをコピーして new_project を作成します。
```bash
cd scotch
cp -r example cp new_project
```

## ◎ config.yml を編集します。
```bash
vim new_project/config.yml
```
- logfile<br>
実行ログの出力パスです。クロールの進捗や、実行時エラーなどが出力されます。
- dbfile<br>
URLのアクセス状況を管理するためのdbファイルを作成するパスです。
- sleep<br>
次のURLにアクセスするまでの待ち時間です。(0には設定しないでください。)

## ◎ doc_handler.py を実装します。
doc_handler.py はクロール対象のURLの判定や、取得したドキュメントからデータの読み込みを行います。<br>
```bash
vim new_project/doc_handler.py
```

以下のメソッドを実装してください<br>
### 0. コンストラクタ
コンストラクタ。ファイルオブジェクトの生成やヘッダなどの出力はこちらで行ってください。<br>
```python
def __init__(self, arguments: List[str], options: Dict[str, Any], config: Dict[str, Any]):
    """コンストラクタ。ヘッダなどを出力する場合はこのメソッドで。
    Args:
      arguments (List[str]): 引数の配列。["プロジェクト名"]
      options (Dict[str, Any]): 辞書形式のオプション。{"continue": True, ...}
      config (Dict[str, Any]): 辞書形式のconfig.yml。{"logfile": "path/to/log", ...}
    """
    super().__init__(arguments, options, config)
```

### 1. seedメソッド
クロール対象のシードURLとホップ数を返すメソッドです。<br>
```python
def seeds(self) -> List[Tuple[str, int]]:
  """クロール対象のシードURLとホップ数を返す
  Returns:
    List[Tuple[str, int]]: (シードURL, ホップ数)のリスト
  """
```

### 2. filterメソッド
next_urlをクロール対象とするかどうかを判定するメソッドです。<br>
クロール対象とする場合は `True` , しない場合は `False` を返します。<br>
```python
def filter(self, curr_url: str, next_url: str) -> bool:
  """ネクストURLをクロール対象とするかを判定する。
  Args:
    curr_url (str): 現在アクセスしているURL
    next_url (str): ネクストURL。このURLをクロールするかを判定する。
  Returns:
    bool: True: next_urlをクロールする, False: next_urlをクロールしない
  """
```

### 3. handleメソッド
取得したドキュメントを処理するメソッドです。<br>
こちらのメソッドで出力(標準出力 or ファイル)まで行ってください。<br>
ドキュメントのパースにはBeautifulSoup4を利用しています。[ドキュメントはこちら](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)<br>
```python
def handle(self, url: str, depth: int, doc: BeautifulSoup):
  """取得したdocumentを処理する
  Args:
    url (str): 取得したURL
    depth (int): シードURLからの階層
    doc (BeautifulSoup): ドキュメント
  Returns:
    void:
  """
```