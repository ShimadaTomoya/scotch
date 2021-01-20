from typing import List, Tuple, Dict, Any
from abc import ABCMeta, abstractmethod
from bs4 import BeautifulSoup

class DocHandlerBase:
  def __init__(self, arguments: List[str], options: Dict[str, Any], config: Dict[str, Any]):
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