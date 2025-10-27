const form = document.getElementById('textForm');
const resultDiv = document.getElementById('result');
const progressContainer = document.getElementById('progressContainer');
const progressBar = document.getElementById('progress');

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const text = document.getElementById('textInput').value.trim();
  resultDiv.innerHTML = '';
  progressBar.style.width = '0%';

  if (!text) {
    resultDiv.textContent = 'Please enter some text.';
    return;
  }

  // show progress bar only after clicking
  progressContainer.classList.remove('hidden');

  let progress = 0;
  const fakeProgress = setInterval(() => {
    if (progress < 90) {
      progress += Math.random() * 5;
      progressBar.style.width = `${progress}%`;
    }
  }, 500);

  try {
    const response = await fetch('/generate-video', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });

    const result = await response.json();
    clearInterval(fakeProgress);
    progressBar.style.width = '100%';

    if (result.videoUrl) {
      setTimeout(() => {
        progressContainer.classList.add('hidden');

        // show link in case user wants to re-download
        resultDiv.innerHTML = `<a href="${result.videoUrl}" download>Download Your Video</a>`;

        // trigger auto-download
        const a = document.createElement('a');
        a.href = result.videoUrl;
        a.download = '';
        document.body.appendChild(a);
        a.click();
        a.remove();
      }, 700);
    } else {
      progressContainer.classList.add('hidden');
      resultDiv.textContent = 'Error generating video.';
    }
  } catch (error) {
    clearInterval(fakeProgress);
    progressContainer.classList.add('hidden');
    resultDiv.textContent = 'Something went wrong.';
  }
});
