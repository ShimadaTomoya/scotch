import datetime
import os
import sys
import re
import logging
import traceback
import time
from importlib import import_module
from typing import Optional, List, Tuple, Dict
from collections import deque
from urllib.request import urlopen, Request
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import yaml
from scotch.crawl_urls import CrawlUrls
from scotch.doc_handler_base import DocHandlerBase

def crawl(urls: CrawlUrls, handler: DocHandlerBase, seed_url: str, sleep: int):
  headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
  }
  row = urls.get_new_url()
  while (row is not None):
    time.sleep(sleep)
    try:
      url, depth = row
      logging.info("url=%s, depth=%s", url, depth)
      request = Request(url = url, headers = headers)
      response = urlopen(request, timeout=10)
      doc = BeautifulSoup(response, "lxml")
      if (depth > 0):
        for link in doc.find_all("a"):
          href = urljoin(url, link["href"])
          if (handler.filter(seed_url, href)):
              urls.add_new_url(href, depth - 1)
      handler.handle(url, depth, doc)
      urls.update_status_complete(url)
    except:
      logging.warning("error: url=%s, depth=%s", url, depth)
      logging.warning(traceback.format_exc())
      urls.update_status_error(url)
    row = urls.get_new_url()

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
    elif (re.match("^(--dbfile|-d)$", arg)):
      options["dbfile"] = queue.popleft()
    else:
      arguments.append(arg)
  return (arguments, options)

if __name__ == "__main__":
  # 引数
  arguments, options = parse_args(sys.argv)
  project = arguments[0]

  # 設定の読み込み
  conf_file = os.path.join(project, "config.yml")
  with open(conf_file) as fh:
    config = yaml.safe_load(fh)

  # log_dir
  if ("log_dir" not in config):
    raise Exception("{} に log_dir が存在しません".format(conf_file))
  log_dir = config["log_dir"]
  if (not os.path.exists(log_dir)):
    os.makedirs(log_dir)

  # sleep
  sleep = config.get("sleep", 1)

  # logger
  log_format = "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s"
  log_file = os.path.join(log_dir, "scotch.log")
  logging.basicConfig(filename=log_file, format=log_format, level=logging.INFO)

  # シードURLリストの読み込み
  seeds_file = os.path.join(project, "seeds.tsv")
  with open(seeds_file) as fh:
    seeds = fh.read().splitlines()

  # db作成
  now = datetime.datetime.now()
  db_file = os.path.join(log_dir, "crawl_{}.db".format(now.strftime('%Y%m%d_%H%M%S')))
  urls = CrawlUrls(db_file)
  urls.drop_table()
  urls.create_table()

  # DocHandlerの読み込み
  doc_handler_module = import_module("{}.doc_handler".format(project))
  doc_handler = doc_handler_module.DocHandler()

  # クロール
  logging.info("project: %s", project)
  logging.info("conf_file: %s", conf_file)
  logging.info("log_file: %s", log_file)
  logging.info("seeds_file: %s", seeds_file)
  logging.info("db_file: %s", db_file)
  for seed in map(lambda l: l.split("\t"), seeds):
    seed_url, depth = seed
    urls.add_new_url(seed_url, depth)
    crawl(urls, doc_handler, seed_url, sleep)
