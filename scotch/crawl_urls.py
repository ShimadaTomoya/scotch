import sqlite3
import hashlib
import traceback
from typing import Optional, List

class CrawlUrls:
    NEW = 0
    PROCESSING = 1
    COMPLETED = 2
    __table = "crawl_urls"

    def __init__(self, dbname: str):
        self.__dbname = dbname
        self.__conn = sqlite3.connect(dbname)

    def __del__(self):
        self.__conn.close()

    def drop_table(self):
        cur = self.__conn.cursor()
        cur.execute("DROP TABLE IF EXISTS `{}`".format(self.__table))
        self.__conn.commit()
        cur.close()

    def create_table(self):
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
        cur.execute(
            "CREATE INDEX status_index ON `{}`(status);".format(self.__table))
        self.__conn.commit()
        cur.close()

    @staticmethod
    def sha512(value: str):
        return hashlib.sha512(value.encode("utf-8")).hexdigest()

    def add_new_url(self, url: str, depth: int):
        sql = "INSERT OR IGNORE INTO `{}` (url_hash, url, depth) VALUES (?, ?, ?);"
        cur = self.__conn.cursor()
        cur.execute(sql.format(self.__table), (CrawlUrls.sha512(url), url, depth))
        self.__conn.commit()
        cur.close()

    def get_new_url(self) -> Optional[sqlite3.Row]:
        cur = self.__conn.cursor()
        row = None
        try:
            cur.execute("BEGIN IMMEDIATE")
            select_one = "SELECT * FROM `{}` WHERE status = 0 LIMIT 1;"
            cur.execute(select_one.format(self.__table))
            row = cur.fetchone()
            if row is not None:
                url_hash = row[0]
                update_status = "UPDATE `{}` SET status = ? WHERE url_hash = ?;"
                cur.execute(update_status.format(self.__table), (self.PROCESSING, url_hash))
            self.__conn.commit()
        except Exception as e:
            self.__conn.rollback()
            raise e
        finally:
            cur.close()
        return row

    def complete(self, url: str):
        sql = "UPDATE `{}` SET status = ? WHERE url_hash = ?;".format(self.__table)
        cur = self.__conn.cursor()
        cur.execute(sql, (CrawlUrls.COMPLETED, CrawlUrls.sha512(url)))
        self.__conn.commit()
        cur.close()

    def select_all(self) -> List[sqlite3.Row]:
        cur = self.__conn.cursor()
        cur.execute("SELECT * FROM {}".format(self.__table))
        rows = cur.fetchall()
        cur.close()
        return rows
