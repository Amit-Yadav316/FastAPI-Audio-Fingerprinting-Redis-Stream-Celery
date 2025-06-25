let mediaRecorder = null;
let isListening = false;
let ws = null;
let chunks = [];
let stopped = false;

const recordBtn = document.getElementById("recordBtn");
const micIcon = recordBtn.querySelector("i");
const resultsDiv = document.getElementById("results");
const spinner = document.getElementById("spinner");
const spinnerText = document.getElementById("spinnerText");

async function uploadFile() {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = 'audio/*';

  input.onchange = async () => {
    const file = input.files[0];
    if (!file) return;

    document.getElementById('loadingBar').style.display = 'block';
    startLoadingBar();

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      const taskId = data.task;

      listenToTaskStatus(taskId);
    } catch (error) {
      alert('Upload failed: ' + error.message);
    }
  };

  input.click();
}

function startLoadingBar() {
  const fill = document.getElementById('progressFill');
  const text = document.getElementById('progressText');
  fill.style.width = '0%';
  text.textContent = '0%';

  let width = 0;
  const interval = setInterval(() => {
    width = Math.min(width + 5, 95);
    fill.style.width = width + '%';
    text.textContent = width + '%';
    if (width >= 95) clearInterval(interval);
  }, 300);
}

function listenToTaskStatus(taskId) {
  ws = new WebSocket(`ws://localhost:8000/ws/status/${taskId}`);

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const fill = document.getElementById('progressFill');
    const text = document.getElementById('progressText');

    if (data.status === "SUCCESS") {
      fill.style.width = '100%';
      fill.style.background = 'green';
      text.textContent = '100%';
      setTimeout(() => document.getElementById('loadingBar').style.display = 'none', 1200);
      ws.close();
    } else if (data.status === "FAILURE") {
      fill.style.background = 'red';
      text.textContent = 'Failed';
      setTimeout(() => document.getElementById('loadingBar').style.display = 'none', 1500);
      ws.close();
      alert("Processing failed.");
    }
  };
}

async function toggleListening() {
  if (isListening) {
    stopRecording();
  } else {
    startListening();
  }
}

async function startListening() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    isListening = true;
    updateMicIcon(true);
    showSpinner();
    resultsDiv.innerHTML = "<p>Listening...</p>";
    stopped = false;
    chunks = [];


    const taskRes = await fetch("http://localhost:8000/new-task-id");
    const { task_id } = await taskRes.json();
    connectWebSocket(task_id);
    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) chunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
      const blob = new Blob(chunks, { type: "audio/webm" });
      const formData = new FormData();
      formData.append("file", blob, "recorded.webm");
      formData.append("task_id", task_id);  

      try {
        const res = await fetch("http://localhost:8000/match", {
          method: "POST",
          body: formData,
        });

        if (!res.ok) {
          const errText = await res.text();
          throw new Error(`Upload failed: ${errText}`);
        }
      } catch (err) {
        resultsDiv.innerHTML = "<p>Failed to upload audio.</p>";
        hideSpinner();
        updateMicIcon(false);
        console.error(err);
      }
    };

    mediaRecorder.start();
    setTimeout(() => stopRecording(), 10000);

  } catch (err) {
    alert("Please allow mic access.");
    console.error("Mic access error:", err);
    hideSpinner();
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== "inactive" && !stopped) {
    stopped = true;
    updateMicIcon(false);
    resultsDiv.innerHTML = "<p>Processing audio...</p>";
    mediaRecorder.stop();
  }
}

async function connectWebSocket(task_id) {
  ws = new WebSocket(`ws://localhost:8000/ws/subscribe/${task_id}`);

  ws.onopen = () => {
    console.log("WebSocket subscribed to task:", task_id);
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    hideSpinner();

    if (data.status === "success" && data.matches?.length) {
      resultsDiv.innerHTML = "<p>Match found!</p>";
      console.log("Matches:", data.matches);
    } else {
      resultsDiv.innerHTML = `<p>${data.message || "No match found."}</p>`;
    }

    closeSocket();
  };

  ws.onerror = (err) => {
    console.error("WebSocket error:", err);
    resultsDiv.innerHTML = "<p>WebSocket error occurred.</p>";
    hideSpinner();
    closeSocket();
  };

  ws.onclose = () => {
    console.warn("WebSocket closed");
    hideSpinner();
    updateMicIcon(false);
  };
}

function closeSocket() {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.close();
  }
  isListening = false;
  updateMicIcon(false);
}

function updateMicIcon(active) {
  if (active) {
    micIcon.classList.remove("fa-microphone");
    micIcon.classList.add("fa-circle-stop");
    recordBtn.style.backgroundColor = "#e53e3e";
  } else {
    micIcon.classList.remove("fa-circle-stop");
    micIcon.classList.add("fa-microphone");
    recordBtn.style.backgroundColor = "";
  }
}

function showSpinner() {
  spinner.classList.remove("hidden");
  spinnerText.classList.remove("hidden");
}

function hideSpinner() {
  spinner.classList.add("hidden");
  spinnerText.classList.add("hidden");
}
