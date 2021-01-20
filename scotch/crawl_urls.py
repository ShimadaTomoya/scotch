import sqlite3
import hashlib
from typing import Optional, List

class CrawlUrls:
  NEW = 0         # 未処理
  PROCESSING = 1  # 処理中
  COMPLETED = 2   # 処理完了
  ERROR = 3       # エラー終了
  __table = "crawl_urls"

  def __init__(self, dbname: str):
    self.__dbname = dbname
    self.__conn = sqlite3.connect(dbname)

  def __del__(self):
    self.__conn.close()

  def drop_table(self):
    """tableを削除します。
    """
    cur = self.__conn.cursor()
    cur.execute("DROP TABLE IF EXISTS `{}`".format(self.__table))
    self.__conn.commit()
    cur.close()

  def create_table(self):
    """tableが存在しなければを作成します。
    """
    sql = """
    CREATE TABLE IF NOT EXISTS `{}` (
      `url_hash` TEXT PRIMARY KEY  NOT NULL,
      `url` TEXT NOT NULL,
      `depth` INTEGER NOT NULL,
      `status` INTEGER NOT NULL DEFAULT 0,
      `created_at` NUMERIC NOT NULL DEFAULT CURRENT_TIMESTAMP,
      `updated_at` NUMERIC NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """
    cur = self.__conn.cursor()
    cur.execute(sql.format(self.__table))
    cur.execute("CREATE INDEX IF NOT EXISTS status_index ON `{}`(status);".format(self.__table))
    self.__conn.commit()
    cur.close()

  @staticmethod
  def sha512(value: str) -> str:
    """sha512を計算して返します。
    Args:
      value (str): 入力文字列
    Returns:
      str: sha512文字列
    """
    return hashlib.sha512(value.encode("utf-8")).hexdigest()

  def add_new_url(self, url: str, depth: int):
    """urlが未登録であればテーブルに挿入します。
    Args:
      url (str): url
      depth (str): 残りホップ数
    """
    sql = "INSERT OR IGNORE INTO `{}` (url_hash, url, depth) VALUES (?, ?, ?);"
    cur = self.__conn.cursor()
    cur.execute(sql.format(self.__table), (CrawlUrls.sha512(url), url, depth))
    self.__conn.commit()
    cur.close()

  def get_new_url(self) -> Optional[sqlite3.Row]:
    """テーブル内の未処理のURLを取得します。
    分離レベル: Repeatable Read
    SELECTしたデータがUPDATE句の完了まで、更新されないことを保証します。
    このメソッドは複数スレッドから同時実行されても安全です。
    Returns:
      Optional[sqlite3.Row]: 取得したレコードオブジェクトを返します。(存在しない場合は None)
    """
    cur = self.__conn.cursor()
    row = None
    try:
      cur.execute("BEGIN IMMEDIATE")
      select_one = "SELECT url, depth FROM `{}` WHERE status = 0 LIMIT 1;"
      cur.execute(select_one.format(self.__table))
      row = cur.fetchone()
      if row is not None:
        url, _ = row
        update_status = "UPDATE `{}` SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE url_hash = ?;"
        cur.execute(update_status.format(self.__table), (self.PROCESSING, CrawlUrls.sha512(url)))
      self.__conn.commit()
    except Exception as e:
      self.__conn.rollback()
      raise e
    finally:
      cur.close()
    return row

  def update_status_complete(self, url: str):
    """指定されたURLのステータスを処理完了に更新します。
    Args:
      url (str): url
    """
    sql = "UPDATE `{}` SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE url_hash = ?;".format(self.__table)
    cur = self.__conn.cursor()
    cur.execute(sql, (CrawlUrls.COMPLETED, CrawlUrls.sha512(url)))
    self.__conn.commit()
    cur.close()

  def update_status_error(self, url: str):
    """指定されたURLのステータスをエラー終了に更新します。
    Args:
      url (str): url
    """
    sql = "UPDATE `{}` SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE url_hash = ?;".format(self.__table)
    cur = self.__conn.cursor()
    cur.execute(sql, (CrawlUrls.ERROR, CrawlUrls.sha512(url)))
    self.__conn.commit()
    cur.close()

  def select_all(self) -> List[sqlite3.Row]:
    """テーブルの中身を全件取得します。
    Returns:
       List[sqlite3.Row]: レコードの配列
    """
    cur = self.__conn.cursor()
    cur.execute("SELECT * FROM {}".format(self.__table))
    rows = cur.fetchall()
    cur.close()
    return rows
