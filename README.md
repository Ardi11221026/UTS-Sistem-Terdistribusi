# **UTS Pub-Sub Log Aggregator (Deliverable)**

##### Isi: Project Pub-Sub Aggregator berbasis FastAPI dengan idempotent consumer dan penyimpanan duplikasi (dedup store) menggunakan SQLite.


## Struktur yang disertakan

* src/ : kode sumber aplikasi (FastAPI app, dedup store, model, consumer)
* tests/ : pengujian pytest (test_all.py berisi beberapa test)
* requirements.txt
* Dockerfile
* README.md (file ini)



##### Cara menjalankan (secara lokal, tanpa Docker)

1. ###### Buat dan aktifkan virtual environment Python 3.11+ dengan kode di Bawah ini:

* python -m venv .venv
* source .venv/bin/activate   # Linux / macOS
* .\\.venv\\Scripts\\activate    # Windows (PowerShell)
* pip install -r requirements.txt



###### 2\. Jalankan aplikasi:

export DEDUP\_DB=./data/dedup.db    # opsional, default ke ./data/dedup.db

uvicorn src.main:app --host 0.0.0.0 --port 8080

Layanan akan aktif di http://0.0.0.0:8080.



###### 3\. Contoh publikasi (satu event):

curl -X POST "http://127.0.0.1:8080/publish" -H "Content-Type: application/json" -d '\[{"topic":"t1","event\_id":"event1","timestamp":"2025-10-19T12:00:00Z","source":"unit","payload":{"msg":"hello world"}}]'



###### 4\. Cek event yang sudah diproses:

* curl "http://127.0.0.1:8080/events?topic=t1"
* curl "http://127.0.0.1:8080/stats"



##### Cara menjalankan pengujian (pytest)

* pip install -r requirements.txt
* python -m pytest -v



##### Cara build Docker image

* docker build -t uts-aggregator .
* docker run -p 8080:8080 uts-aggregator



##### Catatan

* Dedup store menggunakan SQLite di lokasi DEDUP\_DB (variabel lingkungan), default: ./data/dedup.db.
* Database bersifat persisten di antara restart aplikasi.
* Saat pengujian (pytest), digunakan database sementara di direktori /tmp agar tidak saling bertabrakan.
* Proyek ini merupakan implementasi minimal, mandiri, dan lengkap sesuai deskripsi tugas UTS.