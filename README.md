# Wavvy — A Music Guessing System Based on Audio Fingerprints

**Wavvy** is a lightweight and efficient music recognition system that uses **audio fingerprinting**, **real-time audio processing**, and **smart system architecture** — all **without any machine learning**. It emphasizes strong **data structure design**, **performance tuning**, and clean **system architecture**.

---->

##  Features

->  **Audio Fingerprinting**  
  Converts raw audio into unique, compact hashes for quick database lookup and precise matching.

->  **Real-time Matching via WebSockets**  
  Streams user audio input and responds with live track matches using a sliding-window hash matcher.

->  **FastAPI + Celery (Async + Background Workers)**  
  Non-blocking async backend with background-heavy processing handled via Celery and Redis.

-> **Thread-safe Execution**  
  CPU-bound or blocking functions (Librosa, SoundFile, etc.) handled via `run_in_threadpool` for async compatibility.

-> **Redis Caching**  
  Speeds up metadata lookup (e.g., Spotify/YouTube results) and supports hot query pre-caching.

-> **Spotify Integration**  
  Automatically fetches metadata like song title, album, and artist name using Spotify's Web API.

-> **YouTube Metadata Support**  
  Enriches results with YouTube video links for matched songs.

---->

## Why This Project?

Wavvy is ideal if you want to:

-> Explore **real-time audio processing** with no ML dependency.
-> Learn practical integrations of **Celery, Redis, FastAPI, PostgreSQL, and WebSockets**.
-> Build scalable backend systems using **data structures** over deep learning.
-> Understand how to manage **background jobs**, **concurrency**, and **performance optimizations**.

---->

## Future Improvements & Extensions

-  Add support for humming-based recognition (DTW or MFCC similarity).
-  Implement text search with `pg_trgm` (PostgreSQL) or `rapidfuzz` (Python).
-  Add metrics/analytics dashboard (Prometheus + Grafana or custom).
-  Build a frontend with React/Next.js to visualize results and spectrograms.
-  Deploy using Docker + CI/CD to platforms like Render, Railway, Fly.io, or AWS.
![Screenshot 2025-06-20 045239](https://github.com/user-attachments/assets/4a8d5172-1f3a-4595-804e-d02c30f291c8)
![Screenshot 2025-06-20 045255](https://github.com/user-attachments/assets/da96a5ba-1620-46c6-b613-42185a66fb8c)

