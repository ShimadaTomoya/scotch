from typing import List, Tuple, Dict, Any
from abc import ABCMeta, abstractmethod
from bs4 import BeautifulSoup

class DocHandlerBase:
  def __init__(self, arguments: List[str], options: Dict[str, Any], config: Dict[str, Any]):
    """コンストラクタ。ヘッダなどを出力する場合はこのメソッドで。
    Args:
      arguments (List[str]): 引数の配列。["プロジェクト名"]
      options (Dict[str, Any]): 辞書形式のオプション。{"continue": True, ...}
      config (Dict[str, Any]): 辞書形式のconfig.yml。{"logfile": "path/to/log", ...}
    """
    self.arguments = arguments
    self.options = options
    self.config = config

  @abstractmethod
  def seeds(self) -> List[Tuple[str, int]]:
    """クロール対象のシードURLとホップ数を返す
    Returns:
      List[Tuple[str, int]]: (シードURL, ホップ数)のリスト
    """
    pass

  @abstractmethod
  def filter(self, curr_url: str, next_url: str) -> bool:
    """ネクストURLをクロール対象とするかを判定する。
    Args:
      curr_url (str): 現在アクセスしているURL
      next_url (str): ネクストURL。このURLをクロールするかを判定する。
    Returns:
      bool: True: next_urlをクロールする, False: next_urlをクロールしない
    """
    pass

  @abstractmethod
  def handle(self, url: str, depth: int, doc: BeautifulSoup):
    """取得したdocumentを処理する
    Args:
      url (str): 取得したURL
      depth (int): シードURLからの階層
      doc (BeautifulSoup): ドキュメント
    Returns:
      void:
    """
    pass