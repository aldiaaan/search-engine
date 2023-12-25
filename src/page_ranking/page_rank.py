# Reference: https://github.com/nicholaskajoh/devsearch/blob/f6d51fc478e5bae68e4ba32f3299ab20c0ffa033/devsearch/pagerank.py#L2

from src.database.database import Database
from multiprocessing import Value
import pickle
from time import perf_counter
import os
from concurrent.futures import ThreadPoolExecutor, wait
import pymysql
from itertools import repeat
from src.utils import log_execution_time


def save_initial_pagerank(db_connection, initial_pr):
    """
    Fungsi untuk menyimpan nilai initial pagerank ke database.

    Args:
        db_connection (pymysql.Connection): Koneksi database MySQL
        initial_pr (double): Initial page rank
    """
    pages = get_all_crawled_pages(db_connection)

    db_connection.ping()
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)

    for page_row in pages:
        page_id = page_row["id_page"]

        if not Database().check_value_in_table(db_connection, "pagerank", "page_id", page_id):
            query = "INSERT INTO `pagerank` (`page_id`, `pagerank_score`) VALUES (%s, %s)"
            db_cursor.execute(query, (page_id, initial_pr))
        else:
            query = "UPDATE `pagerank` SET `pagerank_score` = %s WHERE `page_id` = %s"
            db_cursor.execute(query, (initial_pr, page_id))

    db_cursor.close()


def save_one_pagerank(db_connection, page_id, pagerank):
    """
    Fungsi untuk menyimpan ranking dan nilai Page Rank yang sudah dihitung ke dalam database.

    Args:
        db_connection (pymysql.Connection): Koneksi database MySQL
        page_id (int): ID page dari table page_information
        pagerank (double): Score page rank
    """
    db_connection.ping()
    db_cursor = db_connection.cursor()

    query = "UPDATE `pagerank` SET `pagerank_score` = %s WHERE `page_id` = %s"
    db_cursor.execute(query, (pagerank, page_id))

    db_cursor.close()


def get_all_crawled_pages(db_connection):
    """
    Fungsi untuk mengambil semua halaman yang sudah dicrawl dari database.

    Args:
        db_connection (pymysql.Connection): Koneksi database MySQL

    Returns:
        list: List berisi dictionary table page_information yang didapatkan dari fungsi cursor.fetchall(), berisi empty list jika tidak ada datanya
    """
    db_connection.ping()

    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    db_cursor.execute("SELECT * FROM `page_information`")
    rows = db_cursor.fetchall()

    db_cursor.close()
    return rows


def get_one_pagerank(db_connection, page_id):
    """
    Fungsi untuk mengambil skor pagerank dari database untuk satu halaman.

    Returns:
        double: Berisi nilai skor page rank
    """
    db_connection.ping()

    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    db_cursor.execute(
        "SELECT pagerank_score FROM `pagerank` WHERE `page_id` = %s", (page_id))
    row = db_cursor.fetchone()

    db_cursor.close()
    return row["pagerank_score"]


def get_all_pagerank_by_page_ids(page_ids: list):
    """
    Fungsi untuk mengambil semua data pagerank dari database pada ID page tertentu.

    Returns:
        list: List berisi dictionary table pagerank yang didapatkan dari fungsi cursor.fetchall(), berisi empty list jika tidak ada datanya
    """
    db_connection = Database().connect()
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    page_ids_string = ",".join(map(str, page_ids))
    query = "SELECT * FROM `pagerank` WHERE `page_id` IN ({}) ORDER BY `pagerank_score` DESC".format(
        page_ids_string)
    db_cursor.execute(query)
    rows = db_cursor.fetchall()
    db_cursor.close()
    Database().close_connection(db_connection)
    return rows


def get_all_pagerank_for_api(start=None, length=None):
    """
    Fungsi untuk mengambil semua data pagerank dari database (untuk keperluan API).

    Args:
        start (int): Indeks awal (optional, untuk pagination)
        length (int): Total data (optional, untuk pagination)

    Returns:
        list: List berisi dictionary table pagerank yang didapatkan dari fungsi cursor.fetchall(), berisi empty list jika tidak ada datanya
    """
    db_connection = Database().connect()
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    if start is None or length is None:
        db_cursor.execute(
            "SELECT `pagerank`.`id_pagerank`,`pagerank`.`pagerank_score`,`pagerank`.`page_id`,`page_information`.`url` FROM `pagerank` INNER JOIN `page_information` ON `pagerank`.`page_id` = `page_information`.`id_page` ORDER BY `pagerank`.`pagerank_score` DESC"
        )
    else:
        db_cursor.execute(
            "SELECT `pagerank`.`id_pagerank`,`pagerank`.`pagerank_score`,`pagerank`.`page_id`,`page_information`.`url` FROM `pagerank` INNER JOIN `page_information` ON `pagerank`.`page_id` = `page_information`.`id_page` ORDER BY `pagerank`.`pagerank_score` DESC LIMIT %s, %s",
            (start, length),
        )
    rows = db_cursor.fetchall()
    db_cursor.close()
    Database().close_connection(db_connection)
    return rows


def log_pagerank_change(page_id, iteration, pagerank_change, db_connection):
    db_connection = db_connection or Database().connect()
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)

    query = "INSERT INTO `pagerank_changes` (`page_id`, `iteration`, `pagerank_change`) VALUES (%s, %s, %s)"
    db_cursor.execute(query, (page_id, iteration, pagerank_change))

    db_cursor.close()


def get_iteration_count():
    file = open('page_ranking_service_state', 'rb')
    iteration = pickle.load(file)
    return iteration


def run_background_service(options: dict = dict()):
    """
    Fungsi utama yang digunakan untuk melakukan perangkingan halaman Page Rank.
    """
    def noop():
        return
    
    on_iteration_change = options.get('on_iteration_change') or noop

    print('start pageranking (non-threaded)....')

    max_iterations = options.get('max_iterations') or 20
    damping_factor = options.get('damping_factor') or 0.85
    db_connection = Database().connect()
    N = Database().count_rows(db_connection, "page_information")
    initial_pr = 1 / N
    print('saving initial pagerank...')
    save_initial_pagerank(db_connection, initial_pr)
    
    print('finished saving initial pagerank...')
    
    # Database().connect_threaded()


    def process_page(page_row, db_connection = None):   
        db_connection = db_connection or Database().connect_threaded()
        t1 = perf_counter()
        page_id = page_row["id_page"]
        page_url = page_row["url"]
        current_pagerank = log_execution_time(get_one_pagerank, (db_connection, page_id))

        new_pagerank = 0
        db_cursor2 = db_connection.cursor(pymysql.cursors.DictCursor)

        # db_cursor2.execute(
        #     "SELECT DISTINCT(`page_id`) FROM `page_linking` WHERE `outgoing_link` = %s",
        #     (page_url),
        # )
        # backlink_ids = db_cursor2.fetchall()

        # for page_linking_row in db_cursor2.fetchall():
        #     backlink_ids.add(page_linking_row["page_id"])

        log_execution_time(lambda: db_cursor2.execute(
            "SELECT `pagerank`.`page_id`, `pagerank`.`pagerank_score`, COUNT(*) FROM `page_linking` INNER JOIN `pagerank` ON `page_linking`.`page_id` = `pagerank`.`page_id` WHERE `pagerank`.`page_id` IN (SELECT DISTINCT(`page_id`) FROM `page_linking` WHERE `outgoing_link` = %s) GROUP by `pagerank`.`page_id`",
            [page_url],
        ))
        for backlink_link_count in db_cursor2.fetchall():
            new_pagerank += backlink_link_count["pagerank_score"] / \
                backlink_link_count["COUNT(*)"]
        db_cursor2.close()

        new_pagerank = ((1 - damping_factor) / N) + \
            (damping_factor * new_pagerank)

        save_one_pagerank(db_connection, page_id, new_pagerank)

        pr_change = abs(new_pagerank - current_pagerank) / current_pagerank
        log_pagerank_change(page_id, iteration, pr_change, db_connection)
        
        db_connection.close()
        db_cursor2.close()

        t2 = perf_counter()
        # avg += (t2 - t1)
        print(f"processing page_id {page_id} took {t2-t1} seconds (avg: --)")
        # print(
        #     f"[{t2 - t1} secs] iteration: {iteration}, page_id: {page_id}, pagerank score: {new_pagerank}, url: {page_url}, pr_change: {pr_change}"
        # )

        return pr_change, t2 - t1

    for iteration in range(max_iterations):
        on_iteration_change(iteration)        
        iteration_t1 = perf_counter()
        pr_change_sum = 0
        # state = open('page_ranking_service_state', 'wb')
        # pickle.dump(iteration, state)
        # state.close()
        pages = get_all_crawled_pages(db_connection)
        avg = 0
        idx = 0
        for index,page_row in enumerate(pages):            
            pr_change, time = process_page(page_row, db_connection)
            pr_change_sum += pr_change        
        average_pr_change = pr_change_sum / N
        if average_pr_change < 0.0001:
            print(f"convergent with average pr change: {average_pr_change}")
            break
        
        iteration_t2 = perf_counter()
        print(f"iteration took {iteration_t2 - iteration_t1} seconds!!")
    Database().close_connection(db_connection)
    print("PageRank Background Service - Completed.")


def run_background_service_threaded(options: dict = dict()):
    """
    Fungsi utama yang digunakan untuk melakukan perangkingan halaman Page Rank.
    """
    
    print('starting pageranking....')

    max_iterations = options.get('max_iterations') or 20
    damping_factor = options.get('damping_factor') or 0.85
    db_connection = Database().connect()
    N = Database().count_rows(db_connection, "page_information")
    initial_pr = 1 / N
    save_initial_pagerank(db_connection, initial_pr)
    
    Database().connect_threaded()


    def process_page(page_row):
        db_connection = Database().connect_threaded()
        t1 = perf_counter()
        page_id = page_row["id_page"]
        page_url = page_row["url"]
        current_pagerank = get_one_pagerank(db_connection, page_id)

        new_pagerank = 0
        db_cursor2 = db_connection.cursor(pymysql.cursors.DictCursor)

        # db_cursor2.execute(
        #     "SELECT DISTINCT(`page_id`) FROM `page_linking` WHERE `outgoing_link` = %s",
        #     (page_url),
        # )
        # backlink_ids = db_cursor2.fetchall()

        # for page_linking_row in db_cursor2.fetchall():
        #     backlink_ids.add(page_linking_row["page_id"])

        log_execution_time(lambda: db_cursor2.execute(
            "SELECT `pagerank`.`page_id`, `pagerank`.`pagerank_score`, COUNT(*) FROM `page_linking` INNER JOIN `pagerank` ON `page_linking`.`page_id` = `pagerank`.`page_id` WHERE `pagerank`.`page_id` IN (SELECT DISTINCT(`page_id`) FROM `page_linking` WHERE `outgoing_link` = %s) GROUP by `pagerank`.`page_id`",
            [page_url],
        ))
        for backlink_link_count in db_cursor2.fetchall():
            new_pagerank += backlink_link_count["pagerank_score"] / \
                backlink_link_count["COUNT(*)"]
        db_cursor2.close()

        new_pagerank = ((1 - damping_factor) / N) + \
            (damping_factor * new_pagerank)

        save_one_pagerank(db_connection, page_id, new_pagerank)

        pr_change = abs(new_pagerank - current_pagerank) / current_pagerank
        log_pagerank_change(page_id, iteration, pr_change, db_connection)
        
        db_connection.close()
        db_cursor2.close()

        t2 = perf_counter()
        # avg += (t2 - t1)
        print(f"processing page_id {page_id} took {t2-t1} seconds (avg: --)")
        # print(
        #     f"[{t2 - t1} secs] iteration: {iteration}, page_id: {page_id}, pagerank score: {new_pagerank}, url: {page_url}, pr_change: {pr_change}"
        # )

        return pr_change, t2 - t1

    for iteration in range(max_iterations):
        iteration_t1 = perf_counter()
        pr_change_sum = 0
        # state = open('page_ranking_service_state', 'wb')
        # pickle.dump(iteration, state)
        # state.close()
        pages = get_all_crawled_pages(db_connection)
        avg = 0
        idx = 0
        # for index,page_row in enumerate(pages):
        with ThreadPoolExecutor(16) as executor:
            for result, t in executor.map(process_page, pages):
                # retrieve the result
                pr_change_sum += result

        average_pr_change = pr_change_sum / N
        if average_pr_change < 0.0001:
            print(f"convergent with average pr change: {average_pr_change}")
            break
        
        iteration_t2 = perf_counter()
        print(f"iteration took {iteration_t2 - iteration_t1} seconds!!")

    state.close()
    Database().close_connection(db_connection)
    print("PageRank Background Service - Completed.")
