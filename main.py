import datetime
import os
import sys
import re
import logging
import traceback
import time
from importlib import import_module
from typing import Optional, List, Tuple, Dict, Any
from collections import deque
from urllib.request import urlopen, Request
from urllib.parse import urljoin
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import yaml
from scotch.crawl_urls import CrawlUrls
from scotch.doc_handler_base import DocHandlerBase

def crawl(table: CrawlUrls, handler: DocHandlerBase, config: Dict[str, Any]):
  headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
  }
  row = table.get_new_url()
  while (row is not None):
    time.sleep(config.get("sleep", 1))
    try:
      url, depth = row
      logging.info("url=%s, depth=%s", url, depth)
      request = Request(url = url, headers = headers)
      response = urlopen(request, timeout=10)
      doc = BeautifulSoup(response, "lxml")
      if (depth > 0):
        for link in doc.find_all("a"):
          try:
            next_url = urljoin(url, link.get("href", ""))
            if (handler.filter(url, next_url)):
                table.add_new_url(next_url, depth - 1)
          except:
            logging.warning("ネクストURL追加中にエラーが発生しました。(next_url=%s, depth=%s)", next_url, depth - 1)
            logging.warning(traceback.format_exc())
      handler.handle(url, depth, doc)
      table.update_status_complete(url)
    except HTTPError:
      logging.warning("URLへのアクセスに失敗しました。(url=%s, depth=%s)", url, depth)
      logging.warning(traceback.format_exc())
      table.update_status_error(url)
    except Exception:
      logging.warning("クロール処理でエラーが発生しました。(url=%s, depth=%s)", url, depth)
      logging.warning(traceback.format_exc())
      table.update_status_error(url)
    row = table.get_new_url()

def script_dir():
  return os.path.abspath(os.path.dirname(__file__))

def parse_args(args: List[str]) -> Tuple[List[str], Dict[str, str]]:
  options = {}
  arguments = []
  queue = deque(args)
  queue.popleft() # コマンド
  while (len(queue) != 0):
    arg = queue.popleft()
    if (re.match("^(--*|-*)$", arg)):
      raise Exception("不明なオプション: {}".format(arg))
    elif (re.match("^(--continue|-c)$", arg)):
      options["continue"] = True
    elif (re.match("^(--help|-h)$", arg)):
      # TODO: usage
      pass
    else:
      arguments.append(arg)
  return (arguments, options)

if __name__ == "__main__":
  # 引数
  arguments, options = parse_args(sys.argv)
  if (len(arguments) != 1):
    # TODO: usage
    raise Exception("不正な引数です")
  project = arguments[0]
  conf_file = os.path.join(project, "config.yml")

  # 設定の読み込み
  with open(conf_file) as fh:
    config = yaml.safe_load(fh)

  # DocHandlerの読み込み
  doc_handler_module = import_module("{}.doc_handler".format(project))
  doc_handler = doc_handler_module.DocHandler(arguments, options, config)

  # log_dir
  log_file = config.get("logfile", "log/crawl.log")
  log_dir = os.path.basename(log_file)
  if (not os.path.exists(log_dir)):
    os.makedirs(log_dir)

  # logger
  log_format = "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s"
  logging.basicConfig(filename=log_file, format=log_format, level=logging.INFO)

  # db作成
  db_file = config.get("dbfile", "log/crawl.db")
  table = CrawlUrls(db_file)
  if (options.get("continue", False) is False):
    table.drop_table()
  table.create_table()

  # seedsの登録
  for seed in doc_handler.seeds():
    url, depth = seed
    table.add_new_url(url, depth)

  # クロール
  logging.info("project: %s", project)
  logging.info("conf_file: %s", conf_file)
  logging.info("log_file: %s", log_file)
  logging.info("db_file: %s", db_file)
  crawl(table, doc_handler, config)
