from typing import List, Tuple, Dict, Any
from bs4 import BeautifulSoup
import re
#import sys
#sys.path.append('../')
from scotch.doc_handler_base import DocHandlerBase

class DocHandler(DocHandlerBase):
  def __init__(self, arguments: List[str], options: Dict[str, Any], config: Dict[str, Any]):
    header = [
      "title"      , "energy"  , "protein",
      "protein_cal", "fat"     , "fat_cal",
      "carb"       , "carb_cal", "desc",
      ]
    if (not options.get("continue", False)):
      print("\t".join(header))
    super().__init__(arguments, options, config)

  def seeds(self) -> List[Tuple[str, int]]:
    seeds = [
      ("https://calorie.slism.jp/", 10),
      #("https://www.asahi.com/news/", 1),
    ]
    return seeds

  def filter(self, seed_url: str, url: str) -> bool:
    if (url.find("/calorie.slism.jp/") >= 0):
      if (url.find("#") >= 0):
        return False
      return True
    elif (url.find("/www.asahi.com/") >= 0):
      return True
    else:
      return False

  def select_one(self, doc: BeautifulSoup, selector: str) -> str:
    v = doc.select_one(selector).text
    if (v is None):
      return ""
    return v.replace("\n", "").strip()

    return "" if (v is None) else v

  def handle(self, url: str, depth: int, doc: BeautifulSoup):
    if (not re.match("^https://calorie.slism.jp/[0-9]+/$", url)):
      return
    ret = []
    ret.append(self.select_one(doc, "h1"))
    ret.append(self.select_one(doc, "#mainData .label + td"))
    ret.append(self.select_one(doc, "#protein_content"))
    ret.append(self.select_one(doc, "#protein_calories"))
    ret.append(self.select_one(doc, "#fat_content"))
    ret.append(self.select_one(doc, "#fat_calories"))
    ret.append(self.select_one(doc, "#carb_content"))
    ret.append(self.select_one(doc, "#carb_calories"))
    ret.append(self.select_one(doc, "#data > div:not(#main) .note02"))
    print("\t".join(ret))