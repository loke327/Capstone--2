fetch("/get_temp")
  .then(res => res.json())
  .then(data => {
    document.getElementById("overview").innerText =
      `Case ID: ${data.case_id}
Case Name: ${data.case_name}
Investigation ID: ${data.investigation_id}

Doctor ID: ${data.doctor_id}
Doctor Name: ${data.doctor_name}
Working At: ${data.doctor_org}

Summary:
${data.summary}`;
  });

function finalSubmit() {
  const signed_name = document.getElementById("signed_name").value;

  fetch("/write_report", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ signed_name })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById("result").innerText =
      "✅ Digitally Signed\nHash:\n" + data.hash;
  });
}
