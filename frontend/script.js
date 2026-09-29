const API_URL = "http://127.0.0.1:8000";

// Matches the order and names your model was trained on
const CLASSES = [
  "tench",
  "English_springer",
  "cassette_player",
  "chain_saw",
  "church",
  "French_horn",
  "garbage_truck",
  "gas_pump",
  "golf_ball",
  "parachute",
];

const gallery = document.getElementById("gallery");
const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const preview = document.getElementById("preview");
const status = document.getElementById("status");
const result = document.getElementById("result");
const mainLabel = document.getElementById("main-label");
const bars = document.getElementById("bars");

function renderGallery() {
  gallery.innerHTML = "";
  CLASSES.forEach((name) => {
    const card = document.createElement("div");
    card.className = "class-card";
    card.dataset.name = name;
    card.innerHTML = `<span class="name">${name.replace("_", " ")}</span>`;
    gallery.appendChild(card);
  });
}
renderGallery();

function highlightClass(label) {
  document.querySelectorAll(".class-card").forEach((card) => {
    card.classList.toggle("matched", card.dataset.name === label);
  });
}

dropZone.addEventListener("click", () => fileInput.click());

dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("hover");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("hover");
});

dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("hover");
  if (e.dataTransfer.files.length) {
    handleFiles(Array.from(e.dataTransfer.files));
  }
});

fileInput.addEventListener("change", () => {
  if (fileInput.files.length) {
    handleFiles(Array.from(fileInput.files));
  }
});

function handleFiles(files) {
  if (files.length === 1) {
    handleSingle(files[0]);
  } else {
    handleBatch(files);
  }
}

function handleSingle(file) {
  preview.src = URL.createObjectURL(file);
  preview.hidden = false;
  result.hidden = true;
  status.textContent = "Classifying...";
  status.className = "status";
  highlightClass(null);

  const formData = new FormData();
  formData.append("file", file);

  fetch(`${API_URL}/classify`, { method: "POST", body: formData })
    .then(async (res) => {
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Server error (${res.status})`);
      }
      return res.json();
    })
    .then((data) => {
      status.textContent = "";
      renderSingleResult(data);
      highlightClass(data.label);
    })
    .catch((err) => {
      status.textContent = `Error: ${err.message}`;
      status.className = "status error";
    });
}

function renderSingleResult(data) {
  mainLabel.innerHTML = `${data.label.replace("_", " ")} <span class="confidence">(${(data.confidence * 100).toFixed(1)}%)</span>`;

  bars.innerHTML = "";
  data.top3.forEach((item) => {
    const pct = (item.confidence * 100).toFixed(1);
    const row = document.createElement("div");
    row.className = "bar-row";
    row.innerHTML = `
      <div class="bar-label">${item.label.replace("_", " ")}</div>
      <div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div>
      <div class="bar-pct">${pct}%</div>
    `;
    bars.appendChild(row);
  });

  result.hidden = false;
}

function handleBatch(files) {
  preview.hidden = true;
  result.hidden = true;
  status.textContent = `Classifying ${files.length} images...`;
  status.className = "status";
  highlightClass(null);

  const formData = new FormData();
  files.forEach((f) => formData.append("files", f));

  fetch(`${API_URL}/classify-batch`, { method: "POST", body: formData })
    .then(async (res) => {
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Server error (${res.status})`);
      }
      return res.json();
    })
    .then((data) => {
      status.textContent = "";
      renderBatchResults(data.results);
    })
    .catch((err) => {
      status.textContent = `Error: ${err.message}`;
      status.className = "status error";
    });
}

function renderBatchResults(results) {
  mainLabel.textContent = `${results.length} image(s) classified`;
  bars.innerHTML = "";

  results.forEach((r) => {
    const row = document.createElement("div");
    row.className = "bar-row";
    if (r.error) {
      row.innerHTML = `
        <div class="bar-label" title="${r.filename}">${r.filename}</div>
        <div class="error">${r.error}</div>
      `;
    } else {
      const pct = (r.confidence * 100).toFixed(1);
      row.innerHTML = `
        <div class="bar-label" title="${r.filename}">${r.filename}</div>
        <div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div>
        <div class="bar-pct">${r.label.replace("_", " ")} ${pct}%</div>
      `;
    }
    bars.appendChild(row);
  });

  result.hidden = false;
}