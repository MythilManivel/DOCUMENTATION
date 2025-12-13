async function uploadDocument() {
  const fileInput = document.getElementById("file");
  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  const response = await fetch("http://127.0.0.1:5000/upload", {
    method: "POST",
    body: formData
  });

  const result = await response.json();
  alert("File uploaded successfully!");
}

async function getSummary() {
  const response = await fetch("http://127.0.0.1:5000/summary");
  const data = await response.json();
  document.getElementById("summary").innerText = data.summary;
}

async function askQuestion() {
  const question = document.getElementById("question").value;

  const response = await fetch("http://127.0.0.1:5000/ask", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ question: question })
  });

  const data = await response.json();
  document.getElementById("answer").innerText = data.answer;
}
