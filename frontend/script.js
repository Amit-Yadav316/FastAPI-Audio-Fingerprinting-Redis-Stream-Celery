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

      if (!response.ok) throw new Error('Upload failed');
      const data = await response.json();
      const taskId = data.task_id;

      alert('File uploaded successfully!');
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
  const ws = new WebSocket(`ws://localhost:8000/ws/status/${taskId}`);

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const fill = document.getElementById('progressFill');
    const text = document.getElementById('progressText');

    if (data.status === "SUCCESS") {
      fill.style.width = '100%';
      fill.style.background = 'linear-gradient(to right, #00b09b, #96c93d)';
      text.textContent= '100%';

      setTimeout(() => {
        document.getElementById('loadingBar').style.display = 'none';
      }, 1200);
      ws.close();
    } else if (data.status === "FAILURE") {
      fill.style.background = 'linear-gradient(to right, #e53935, #e35d5b)';
      text.textContent = 'Failed';

      setTimeout(() => {
        document.getElementById('loadingBar').style.display = 'none';
      }, 1500);
      ws.close();
      alert("Processing failed.");
    }
  };
}
