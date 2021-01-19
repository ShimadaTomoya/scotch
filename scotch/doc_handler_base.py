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
    pass

  @abstractmethod
  def filter(self, seed_url: str, url: str) -> bool:
    pass

  @abstractmethod
  def handle(self, url: str, depth: int, doc: BeautifulSoup):
    pass