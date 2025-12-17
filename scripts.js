async function uploadDocument() {
  const fileInput = document.getElementById("file");

  if (!fileInput.files.length) {
    alert("Please select a file to upload.");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  try {
    const response = await fetch("http://127.0.0.1:5000/upload", {
      method: "POST",
      body: formData
    });

    await response.json();
    alert("File uploaded successfully!");
  } catch (error) {
    alert("File upload failed.");
    console.error(error);
  }
}

async function getSummary() {
  try {
    const response = await fetch("http://127.0.0.1:5000/summary");
    const result = await response.json();
    document.getElementById("summary").innerText = result.summary;
  } catch (error) {
    document.getElementById("summary").innerText = "Error fetching summary.";
    console.error(error);
  }
}

async function askQuestion() {
  const userQuestion = document.getElementById("question").value.trim();

  if (!userQuestion) {
    alert("Please enter a question.");
    return;
  }

  try {
    const response = await fetch("http://127.0.0.1:5000/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: userQuestion })
    });

    const result = await response.json();
    document.getElementById("answer").innerText = result.answer;
  } catch (error) {
    document.getElementById("answer").innerText = "Error getting answer.";
    console.error(error);
  }
}
