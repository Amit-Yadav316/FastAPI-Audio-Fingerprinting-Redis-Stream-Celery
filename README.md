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

--->  
##  Getting Started
Step 1 : git clone URL into directory and code . In Windows Powershell
![Screenshot 2025-06-25 211204](https://github.com/user-attachments/assets/ad282679-f072-4728-b158-79d7f1f42370)

Step 2 : Create virtual environment
![Screenshot 2025-06-25 210747](https://github.com/user-attachments/assets/aea5f096-bec6-46e4-a7bb-cc9e0f9ddf12)

Step 3 : Activate it and Run this (if you are on WINDOWS >> venv\Scripts\activate)
![Screenshot 2025-06-25 210814](https://github.com/user-attachments/assets/61b45c33-6382-450e-a1e8-790b09fb9b01)

Step 3 : Install all requirements
![Screenshot 2025-06-25 210927](https://github.com/user-attachments/assets/a3e8207c-93bd-42b8-838c-c92166238662)

Step 4 : Run this for Server
![Screenshot 2025-06-25 210955](https://github.com/user-attachments/assets/b0a2b6c6-4061-4657-8264-8739ae9f4d8d)

Step 5 : Click on the link you will directly be on the server
![Screenshot 2025-06-25 212824](https://github.com/user-attachments/assets/5e8ffd04-bef6-4303-baa9-4f69c6dc8dc0)

Step 6 : Then type /doc just like I did
![Screenshot 2025-06-25 213022](https://github.com/user-attachments/assets/9a93ff6d-a334-44a5-895f-a55975e17569)

Step 7: You will at Swagger docs where you can test Endpoint Or you can use (POSTMAN BUT BEFORE THAT YOU SET UP CELERY)
![Screenshot 2025-06-25 213242](https://github.com/user-attachments/assets/7d3b4ad1-58a7-4f33-8896-804d84b507b8)

STEP 8 : THEN COME BACK TO VS CODE AND THEN --> Open another terminal in vscode powershell and run this (if you are on WINDOWS >> venv\Scripts\activate >> celery -A celery_worker.celery_app worker --loglevel=info --pool=solo )
![Screenshot 2025-06-25 211047](https://github.com/user-attachments/assets/53bf465f-1273-4c35-9d67-6457c15de0d9)

Step 9 : Use POSTMAN to test endpoints 
These are my results
---->
![Screenshot 2025-06-25 182457](https://github.com/user-attachments/assets/2b8013b9-24bb-43f6-8dfa-9165437bd635)
![Screenshot 2025-06-25 182538](https://github.com/user-attachments/assets/2084750b-e451-4889-aa16-6979eae012bb)
![Screenshot 2025-06-25 182616](https://github.com/user-attachments/assets/37f1d868-0412-462e-8c96-383848c4341c)

Step 10 : You can create your front end and test and integrate and new things like fuzzy search , humming detection etc..
BOOM YOU ARE DONE!!


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



