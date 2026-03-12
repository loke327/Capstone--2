function verifyCase() {
  const caseId = document.getElementById("caseId").value;

  fetch("/court_verify_case/" + caseId)
    .then(res => res.json())
    .then(data => {

      if (data.error) {
        document.getElementById("result").innerText = data.error;
        return;
      }

      document.getElementById("result").innerText =
        "CASE DETAILS\n\n" + data.full_details +
        "\n\nHASH KEY:\n" + data.hash;

      // 🔎 Extract video path from summary text
      const match = data.full_details.match(/Video Evidence:\s*(.*)/);

      if (match) {
        const video = document.getElementById("video");
        video.src = "/" + match[1].trim();
        video.style.display = "block";
      }
    });
}
