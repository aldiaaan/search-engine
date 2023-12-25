from typing import Any, List
from src.database.database import Database
from src.crawling.crawl_utils import CrawlUtils
from src.crawling.crawl_utils import CustomThreadPoolExecutor
from datetime import datetime
from urllib.parse import urljoin
import bs4
import threading
import queue
import time
import re


class ModifiedSimilarityBased:
    """
    Kelas yang digunakan untuk melakukan crawling dengan metode Modified Similarity Based Crawling.

    Args:
        crawl_id (int): ID crawling (table crawling di database)
        url_queue (queue.Queue): Kumpulan URL antrian
        visited_urls (list): Kumpulan URL yang sudah dikunjungi
        list_urls (list): Kumpulan outgoing URL untuk keperluan reorder di MSB
        keyword (str): Keyword yang digunakan untuk prioritas antrian MSB
        duration_sec (int): Durasi MSB crawler dalam detik
        max_threads (int): Maksimal threads yang akan digunakan
    """

    def __init__(
        self,
        crawl_id: int,
        url_queue: queue.Queue,
        visited_urls: List[str],
        list_urls: List[str],
        keyword: str,
        duration_sec: int,
        max_threads: int,
    ) -> None:
        self.crawl_id: int = crawl_id
        self.visited_urls: List[str] = visited_urls
        self.keyword: str = keyword
        self.duration_sec: int = duration_sec
        self.max_threads: int = max_threads
        self.db = Database()
        self.crawl_utils = CrawlUtils()
        self.lock: threading.Lock = threading.Lock()
        self.start_time: float = time.time()
        self.list_urls: List[str] = list_urls
        self.hot_queue: queue.Queue = queue.Queue()
        self.url_queue: queue.Queue = self.reorder_queue(url_queue)
        
    def run(self) -> None:
        """
        Fungsi utama yang berfungsi untuk menjalankan proses crawling MSB.
        """
        executor = CustomThreadPoolExecutor(max_workers=self.max_threads)        
        futures = []
        while True:
            try:
                time_now = time.time() - self.start_time
                time_now_int = int(time_now)
                if time_now_int >= self.duration_sec:
                    print("Stopped because exceeded time limit...")
                    break
                if self.hot_queue.qsize() > 0:
                    target_url = self.hot_queue.get()
                else:
                    target_url = self.url_queue.get()
                if target_url not in self.visited_urls:
                    self.visited_urls.append(target_url)
                    futures.append(
                        executor.submit(self.scrape_page, target_url))

                self.hot_queue = self.reorder_queue(self.hot_queue)
                self.url_queue = self.reorder_queue(self.url_queue)
            except queue.Empty:
                if self.crawl_utils.running_thread_count(futures) > 0:
                    continue
                else:
                    print("Stopped because empty queue...")
                    break
            except KeyboardInterrupt:
                print("Stopped because keyboard interrupt...")
                break
            except Exception as e:
                print(e)
                continue

        executor.shutdown39(wait=False, cancel_futures=True)

    def scrape_page(self, url: str) -> None:
        """
        Fungsi untuk menyimpan konten yang ada pada suatu halaman ke database.

        Args:
            url (str): URL halaman yang ingin discrape
        """
        try:
            page_start_time = time.time()
            response = self.crawl_utils.get_page(url)
            if response and response.status_code == 200:
                db_connection = self.db.connect()
                self.lock.acquire()
                now = datetime.now()
                print(url, "| MSB |", now.strftime("%d/%m/%Y %H:%M:%S"))
                self.lock.release()
                soup = bs4.BeautifulSoup(response.text, "html.parser")
                title = soup.title.string
                article_html5 = soup.find("article")
                if article_html5 is None:
                    # extract text content from html4
                    html5 = 0
                    texts = soup.find("body").findAll(text=True)
                    visible_texts = filter(self.tag_visible, texts)
                    text = " ".join(t.strip() for t in visible_texts)
                    text = text.lstrip().rstrip()
                    text = text.split(",")
                    clean_text = ""
                    for sen in text:
                        if sen:
                            sen = sen.rstrip().lstrip()
                            clean_text += sen + ","
                    complete_text = clean_text
                else:
                    # extract text content from html5
                    html5 = 1
                    texts = article_html5.findAll(text=True)
                    visible_texts = filter(self.tag_visible, texts)
                    text = " ".join(t.strip() for t in visible_texts)
                    text = text.lstrip().rstrip()
                    text = text.split(",")
                    clean_text = ""
                    for sen in text:
                        if sen:
                            sen = sen.rstrip().lstrip()
                            clean_text += sen + ","
                    complete_text = clean_text

                # get meta description
                description = soup.find("meta", attrs={"name": "description"})
                if description is None:
                    description = "-"
                else:
                    description = description.get("content")

                # get meta keywords
                keywords = soup.find("meta", attrs={"name": "keywords"})
                if keywords is None:
                    keywords = "-"
                else:
                    keywords = keywords.get("content")

                # check hot_url
                hot_link = 0
                if (self.crawl_utils.count_keyword_in_text(
                        complete_text, self.keyword)
                        >= 10) or (self.crawl_utils.count_keyword_in_text(
                            title, self.keyword) >= 1):
                    hot_link = 1

                # check if the page information already exist
                if self.db.check_value_in_table(db_connection,
                                                "page_information", "url",
                                                url):
                    self.db.close_connection(db_connection)
                    return

                # extract outgoing link
                links = soup.findAll("a", href=True)
                for i in links:
                    # Complete relative URLs and strip trailing slash
                    complete_url = urljoin(url, i["href"]).rstrip("/")

                    self.list_urls.append(complete_url)
                    self.crawl_utils.insert_page_linking(
                        db_connection, self.crawl_id, url, complete_url)

                    self.lock.acquire()
                    if self.crawl_utils.is_valid_url(
                            complete_url
                    ) and complete_url not in self.visited_urls:
                        if hot_link == 1 or self.keyword in url:
                            self.hot_queue.put(complete_url)
                        else:
                            self.url_queue.put(complete_url)
                    self.lock.release()

                # size of the page
                size_bytes = len(response.content)

                # extract tables
                try:
                    for table in soup.findAll("table"):
                        self.crawl_utils.insert_page_table(
                            db_connection, url, table)
                except:
                    pass

                # extract lists
                try:
                    for lists in soup.findAll("li"):
                        self.crawl_utils.insert_page_list(
                            db_connection, url, lists)
                except:
                    pass

                # extract forms
                try:
                    for form in soup.findAll("form"):
                        self.crawl_utils.insert_page_form(
                            db_connection, url, form)
                except:
                    pass

                try:
                    # extract images
                    for image in soup.findAll("img"):
                        self.crawl_utils.insert_page_image(
                            db_connection, url, image)
                except:
                    pass

                try:
                    # extract style
                    for style in soup.findAll("style"):
                        self.crawl_utils.insert_page_style(
                            db_connection, url, style)
                except:
                    pass

                try:
                    # extract script
                    for script in soup.findAll("script"):
                        self.crawl_utils.insert_page_script(
                            db_connection, url, script)
                except:
                    pass

                page_duration_crawl = time.time() - page_start_time
                self.crawl_utils.insert_page_information(
                    db_connection,
                    url,
                    self.crawl_id,
                    html5,
                    title,
                    description,
                    keywords,
                    complete_text,
                    hot_link,
                    size_bytes,
                    "MSB crawling",
                    int(page_duration_crawl),
                )
                self.db.close_connection(db_connection)
                return
            return
        except Exception as e:
            print(e, "~ Error in thread")
            return

    def tag_visible(self, element: Any) -> bool:
        """
        Fungsi untuk merapihkan konten teks.

        Args:
            element (Any): Elemen HTML
        """
        if element.parent.name in [
                "style", "script", "head", "title", "meta", "[document]"
        ]:
            return False
        if isinstance(element, bs4.element.Comment):
            return False
        if re.match(r"[\n]+", str(element)):
            return False
        return True

    def reorder_queue(self, q: queue.Queue) -> queue.Queue:
        """
        Fungsi untuk melakukan mengurutkan ulang antrian link pada crawler.

        Args:
            q (queue.Queue): Queue yang ingin diurutkan

        Returns:
            queue.Queue: Queue yang sudah diurutkan
        """
        value_backlink = []
        for u in list(q.queue):
            # menentukan nilai backlink_count
            backlink_count = self.list_urls.count(u)
            # print(backlink_count)
            # memasukan backlink_count ke array value_backlink
            value_backlink.append(backlink_count)

        # membuat dictionary backlink untuk proses sorting
        backlink_dictionary = dict(zip(q.queue, value_backlink))

        # sorting backlink_dictionary
        sort_orders = sorted(backlink_dictionary.items(),
                             key=lambda x: x[1],
                             reverse=True)
        # mengkosongkan queue
        with q.mutex:
            q.queue.clear()

        # membuat queue yang sudah di sort
        for i in sort_orders:
            q.put(i[0])

        return q
