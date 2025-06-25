# Wavvy — A Music Guessing System Based on Audio Fingerprints

**Wavvy** is a lightweight and efficient music recognition system that uses **audio fingerprinting**, **real-time audio processing**, and **smart system architecture** — all **without any machine learning model but we can do add in future**. It emphasizes strong **data structure design**, **performance tuning**, and clean **system architecture**.

---->

##  Features

->  **Audio Fingerprinting**  
  Converts raw audio into unique, compact hashes for quick database lookup and precise matching.

->  **Real-time Matching and Streaming result on Websocket so that users know its done**  
  Streams user audio input and responds with live track matches using a sliding-window hash matcher.

->  **FastAPI + Celery (Async + Background Workers)**  
  Non-blocking async backend with background-heavy processing handled via Celery and Redis.

-> **Redis Caching**  
  Speeds up metadata lookup (e.g., Spotify/YouTube results) and supports hot query pre-caching.

-> **Spotify Integration**  
  Automatically fetches metadata like song title, album, and artist name using Spotify's Web API.

-> **YouTube Metadata Support**  
  Enriches results with YouTube video links for matched songs.

---->
![Screenshot 2025-06-25 204911](https://github.com/user-attachments/assets/8e8dcba3-dc25-4e2a-bc42-828f5a7b2b41)
![Screenshot 2025-06-25 182457](https://github.com/user-attachments/assets/2b8013b9-24bb-43f6-8dfa-9165437bd635)
![Screenshot 2025-06-25 182538](https://github.com/user-attachments/assets/2084750b-e451-4889-aa16-6979eae012bb)
![Screenshot 2025-06-25 182616](https://github.com/user-attachments/assets/37f1d868-0412-462e-8c96-383848c4341c)


## Why This Project?

Wavvy is ideal if you want to:

-> Explore **real-time audio processing** with no ML dependency.
-> Learn practical integrations of **Celery, Redis Stream, FastAPI, PostgreSQL, and WebSockets**.
-> Build scalable backend systems using **data structures** over deep learning.
-> Understand how to manage **background jobs**, **concurrency**, and **performance optimizations**.

---->
## Important Note---> this is for learning where sometime i have used things which are not as much effected as other things like redis stream for one websocket end point but for other simple async result using state but you can use redis stream for every socket but for learning of both i have used both

--->

## Future Improvements

-  Add support for humming-based recognition (DTW or MFCC similarity).
-  Implement text search with `pg_trgm` (PostgreSQL) or `rapidfuzz` (Python).
-  Add metrics/analytics dashboard (Prometheus + Grafana or custom).
-  Build a frontend with React/Next.js to visualize results and spectrograms.
-  Deploy using Docker + CI/CD to platforms like Render, Railway, Fly.io, or AWS.



