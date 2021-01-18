from abc import ABCMeta, abstractmethod
from bs4 import BeautifulSoup

class DocHandlerBase:
  @abstractmethod
  def filter(self, seed_url: str, url: str) -> bool:
    pass

  @abstractmethod
  def handle(self, url: str, depth: int, doc: BeautifulSoup):
    pass