from typing import List, Tuple, Dict, Any
from bs4 import BeautifulSoup
import re
#import sys
#sys.path.append('../')
from scotch.doc_handler_base import DocHandlerBase

class DocHandler(DocHandlerBase):
  def __init__(self, arguments: List[str], options: Dict[str, Any], config: Dict[str, Any]):
    super().__init__(arguments, options, config)

  def seeds(self) -> List[Tuple[str, int]]:
    seeds = [
      ("https://calorie.slism.jp/", 1),
      ("https://www.asahi.com/news/", 1),
    ]
    return seeds

  def filter(self, seed_url: str, url: str) -> bool:
    if (url.find("/calorie.slism.jp/") >= 0):
      return True
    elif (url.find("/www.asahi.com/") >= 0):
      return True
    else:
      return False

  def handle(self, url: str, depth: int, doc: BeautifulSoup):
    print(doc.title)
