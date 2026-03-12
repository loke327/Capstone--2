function submitReport() {
  const summary = document.getElementById("summary").value;
  const status = document.getElementById("status");

  status.innerText = "🔐 Digitally signing...";

  fetch("/write_report", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ summary })
  })
  .then(res => res.json())
  .then(data => {
    status.innerText = "✅ Signed\nHash:\n" + data.hash;
  });
}
function goToReview() {
  const data = {
    case_id: document.getElementById("case_id").value,
    case_name: document.getElementById("case_name").value,
    investigation_id: document.getElementById("investigation_id").value,
    doctor_id: document.getElementById("doctor_id").value,
    doctor_name: document.getElementById("doctor_name").value,
    doctor_org: document.getElementById("doctor_org").value,
    summary: document.getElementById("summary").value
  };

  fetch("/save_temp", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  })
  .then(() => window.location.href = "/review");
}


function verifyReport() {
  const id = document.getElementById("reportId").value;
  const result = document.getElementById("result");

  fetch(`http://127.0.0.1:5000/court_verify/${id}`)
    .then(res => res.json())
    .then(data => {
      result.innerText = JSON.stringify(data, null, 2);
    });
}
