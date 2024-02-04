# :beginner: Search Engine

Aplikasi search engine yang dibuat dengan menggunakan crawler, document ranking, dan page ranking



## Development

### Backend
1. clone project ini
2. Buka file `.env` dan ubah konfigurasinya dengan benar (akses database, konfigurasi crawler, dll)
3. Install library python yang diperlukan dengan menjalankan `pip install -r requirements.txt`
4. `python run_api.py` untuk menjalankan rest api

### Celery Workers
1. pergi ke folder `/src/celery` dan jalankan celery dengan cara menjalankan perintah `celery -A workers worker  -l INFO --pool=prefork -n SEARCH_ENGINE_WORKERS --without-heartbeat --without-gossip --without-mingle`

### Frontend
1. Clone project frontend disini `https://github.com/aldiaaan/one-search-web-client`
2. jalankan perintah `npm install` pada root directory frontend
3. isi file `.env` sesuai dengan kebutuhan
4. `npm run dev` untuk menjalankan frontend dalam mode development

## Deployment

### Backend
1. clone project ini
2. pastikan sudah mengisi env variables yang terletak pada file `.env` dengan benar 
3. register aplikasi flask pada apache dengan merujuk pada dokumentasi dari flask [Dokumentasi](https://flask.palletsprojects.com/en/2.0.x/deploying/mod_wsgi/)

### Frontend
1. Clone project frontend disini `https://github.com/aldiaaan/one-search-web-client`
2. jalankan perintah `npm install` pada root directory frontend
3. pastikan sudah mengisi env variables frontend yang terletak pada file `.env` dengan benar
4. jalankan `npm run build-only:production` pada root directory frontend 
5. pindahkan semua file yang berada `dists` ke dalam folder backend `/src/web_client`

### Daemonizing Celery Workers
untuk menjadikan proses celery menjadi daemon dengan `systemd`, sudah disediakan format `systemd` nya di file `se-workers.service` untuk lebih lengkapnya bisa merujuk pada dokumentasi asli dari celery nya [Dokumentasi](https://docs.celeryq.dev/en/stable/userguide/daemonizing.html)



## :package: Perintah


**General**

- `Python run_crawl.py` untuk menjalankan crawler
- `Python run_page_rank.py` untuk menjalankan page rank
- `Python run_tf_idf.py` untuk menjalankan tf idf
- `Python run_api.py` untuk menjalankan REST API
- `Python run_search_engine_console.py` untuk menjalankan search engine berbasis console

**Background Services**

## :notebook: File Dokumentasi

- [Entity Relationship Diagram (ERD)](https://dbdiagram.io/d/Copy-of-ERD-Crawler-65c00becac844320ae6bb6cb)
- [Class Diagram](docs/class_diagram_simplified.png)
- [Postman API Documentation](https://documenter.getpostman.com/view/11687432/2s8YerLWtg)
- [Routing Table](docs/routing_table.png)
