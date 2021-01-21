from typing import List, Tuple, Dict, Any
from bs4 import BeautifulSoup
import re
#import sys
#sys.path.append('../')
from scotch.doc_handler_base import DocHandlerBase

class DocHandler(DocHandlerBase):
  def __init__(self, arguments: List[str], options: Dict[str, Any], config: Dict[str, Any]):
    """コンストラクタ。ヘッダなどを出力する場合はこのメソッドで。
    Args:
      arguments (List[str]): 引数の配列。["プロジェクト名"]
      options (Dict[str, Any]): 辞書形式のオプション。{"continue": True, ...}
      config (Dict[str, Any]): 辞書形式のconfig.yml。{"logfile": "path/to/log", ...}
    """
    header = [
      "itemid",
      "title",
      "url",
      "image",
      "number1", # カロリー
      "number2", # タンパク質(g)
      "number3", # タンパク質(kcal)
      "number4", # 脂質(g)
      "number5", # 脂質(kcal)
      "number6", # 炭水化物(g)
      "number7", # 炭水化物(kcal)
      "desc",
      ]
    if (not options.get("continue", False)):
      print("\t".join(header))
    super().__init__(arguments, options, config)

  def seeds(self) -> List[Tuple[str, int]]:
    """クロール対象のシードURLとホップ数を返す
    Returns:
      List[Tuple[str, int]]: (シードURL, ホップ数)のリスト
    """
    seeds = [
      ("https://calorie.slism.jp/", 10),
      #("https://www.asahi.com/news/", 1),
    ]
    return seeds

  def filter(self, curr_url: str, next_url: str) -> bool:
    """ネクストURLをクロール対象とするかを判定する。
    Args:
      curr_url (str): 現在アクセスしているURL
      next_url (str): ネクストURL。このURLをクロールするかを判定する。
    Returns:
      bool: True: next_urlをクロールする, False: next_urlをクロールしない
    """
    if (next_url.find("https://calorie.slism.jp/") >= 0):
      if (next_url.find("#") >= 0 or next_url.find("twitterOauth.php") >= 0):
        return False
      return True
    elif (next_url.find("https://www.asahi.com/") >= 0):
      return True
    else:
      return False

  def text_content(self, doc: BeautifulSoup, selector: str) -> str:
    v = doc.select_one(selector)
    if (v is None):
      return ""
    return v.text.replace("\n", "").strip()

  def get_attribute(self, doc: BeautifulSoup, selector: str, attribute: str) -> str:
    v = doc.select_one(selector)
    if (v is None):
      return ""
    return v.get(attribute)

  def handle(self, url: str, depth: int, doc: BeautifulSoup):
    """取得したdocumentを処理する
    Args:
      url (str): 取得したURL
      depth (int): シードURLからの階層
      doc (BeautifulSoup): ドキュメント
    Returns:
      void:
    """
    if (not re.match("^https?://calorie.slism.jp/[0-9]+/$", url)):
      return
    ret = []
    # itemid
    ret.append(url)
    # title
    ret.append(self.text_content(doc, "h1"))
    # url
    ret.append(url)
    # image
    ret.append(self.get_attribute(doc, "#itemImg img", "src"))
    # number1
    ret.append(self.text_content(doc, ".singlelistKcal"))
    # number2
    ret.append(self.text_content(doc, "#protein_content"))
    # number3
    ret.append(self.text_content(doc, "#protein_calories"))
    # number4
    ret.append(self.text_content(doc, "#fat_content"))
    # number5
    ret.append(self.text_content(doc, "#fat_calories"))
    # number6
    ret.append(self.text_content(doc, "#carb_content"))
    # number7
    ret.append(self.text_content(doc, "#carb_calories"))
    # desc
    ret.append(self.text_content(doc, ".note"))
    print("\t".join(ret))