// ============================================================
// TAB SWITCHING
// ============================================================
document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById("panel-" + btn.dataset.tab).classList.add("active");
  });
});

// ============================================================
// CHART.JS SETUP (one line chart per problem)
// ============================================================
function makeChart(canvasId, label1, color1, label2, color2, yTitle) {
  const ctx = document.getElementById(canvasId).getContext("2d");
  return new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        { label: label1, data: [], borderColor: color1, borderWidth: 2, pointRadius: 0, tension: 0.2 },
        { label: label2, data: [], borderColor: color2, borderWidth: 2, pointRadius: 0, tension: 0.2 },
      ],
    },
    options: {
      animation: false,
      responsive: true,
      scales: {
        x: { title: { display: true, text: "Update #" } },
        y: { title: { display: true, text: yTitle }, beginAtZero: true },
      },
    },
  });
}

const charts = {
  producer_consumer: makeChart("pc_chart", "Produced", "#4CAF50", "Consumed", "#E91E63", "Items"),
  dining_philosopher: makeChart("dp_chart", "Meals", "#4CAF50", "Eating now", "#E91E63", "Count"),
  reader_writer: makeChart("rw_chart", "Reads", "#2196F3", "Writes", "#E91E63", "Ops"),
};

function pushChartPoint(problem, v1, v2) {
  const c = charts[problem];
  const n = c.data.labels.length;
  c.data.labels.push(n);
  c.data.datasets[0].data.push(v1);
  c.data.datasets[1].data.push(v2);
  if (c.data.labels.length > 120) {
    c.data.labels.shift();
    c.data.datasets[0].data.shift();
    c.data.datasets[1].data.shift();
  }
  c.update("none");
}

function resetChart(problem) {
  const c = charts[problem];
  c.data.labels = [];
  c.data.datasets[0].data = [];
  c.data.datasets[1].data = [];
  c.update("none");
}

// ============================================================
// CANVAS DRAWING — mirrors the Tkinter canvas visuals
// ============================================================
function drawBuffer(bufferSize, itemsInBuffer) {
  const canvas = document.getElementById("pc_canvas");
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const padding = 3;
  const cellW = Math.max(6, Math.min(50, Math.floor((canvas.width - padding * (bufferSize + 1)) / bufferSize)));
  const cellH = cellW < 30 ? cellW : 42;
  for (let i = 0; i < bufferSize; i++) {
    const x = padding + i * (cellW + padding);
    const y = padding;
    const filled = i < itemsInBuffer;
    ctx.fillStyle = filled ? "#4CAF50" : "#EEEEEE";
    ctx.strokeStyle = "#888888";
    ctx.fillRect(x, y, cellW, cellH);
    ctx.strokeRect(x, y, cellW, cellH);
    if (cellW >= 18) {
      ctx.fillStyle = filled ? "white" : "#666666";
      ctx.font = `bold ${Math.max(6, Math.floor(cellW / 4))}px Consolas, monospace`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(String(i + 1), x + cellW / 2, y + cellH / 2);
    }
  }
}

function drawPhilosophers(n, eatingArray) {
  const canvas = document.getElementById("dp_canvas");
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const size = canvas.width;
  const center = size / 2;
  const radius = size / 2 - 30;
  const philR = Math.max(4, Math.min(20, 100 / (Math.floor(n / 3) + 1)));
  const forkR = Math.max(2, philR / 3);

  // forks
  for (let i = 0; i < n; i++) {
    const angle = (2 * Math.PI * i) / n;
    const fx = center + radius * Math.cos(angle);
    const fy = center + radius * Math.sin(angle);
    const held = eatingArray[i] || eatingArray[(i - 1 + n) % n];
    ctx.fillStyle = held ? "#4CAF50" : "#CCCCCC";
    ctx.strokeStyle = "#666666";
    ctx.beginPath();
    ctx.arc(fx, fy, forkR, 0, 2 * Math.PI);
    ctx.fill();
    ctx.stroke();
  }

  // philosophers
  for (let i = 0; i < n; i++) {
    const angle = (2 * Math.PI * i) / n - Math.PI / 2;
    const px = center + (radius - 40) * Math.cos(angle);
    const py = center + (radius - 40) * Math.sin(angle);
    ctx.fillStyle = eatingArray[i] ? "#4CAF50" : "#90A4AE";
    ctx.strokeStyle = "#444444";
    ctx.beginPath();
    ctx.arc(px, py, philR, 0, 2 * Math.PI);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = "white";
    ctx.font = `bold ${Math.max(7, philR)}px Consolas, monospace`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(String(i), px, py);
  }
}

function drawReaderWriter(numReaders, numWriters, activeReaders, writerActive) {
  const canvas = document.getElementById("rw_canvas");
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const slotW = 50, slotH = 40, gap = 10;
  ctx.font = "11px Consolas, monospace";
  ctx.textAlign = "center";

  // readers row
  for (let i = 0; i < numReaders; i++) {
    const x = 10 + i * (slotW + gap);
    const y = 10;
    const active = i < activeReaders;
    ctx.fillStyle = active ? "#2196F3" : "#EEEEEE";
    ctx.strokeStyle = "#888888";
    ctx.fillRect(x, y, slotW, slotH);
    ctx.strokeRect(x, y, slotW, slotH);
    ctx.fillStyle = active ? "white" : "#666666";
    ctx.fillText("R" + i, x + slotW / 2, y + slotH / 2 + 4);
  }

  // writers row
  for (let i = 0; i < numWriters; i++) {
    const x = 10 + i * (slotW + gap);
    const y = 60;
    const active = writerActive && i === 0;
    ctx.fillStyle = active ? "#E91E63" : "#EEEEEE";
    ctx.strokeStyle = "#888888";
    ctx.fillRect(x, y, slotW, slotH);
    ctx.strokeRect(x, y, slotW, slotH);
    ctx.fillStyle = active ? "white" : "#666666";
    ctx.fillText("W" + i, x + slotW / 2, y + slotH / 2 + 4);
  }
}

// ============================================================
// SIMULATION CONTROL + POLLING
// ============================================================
let pollTimers = {};

async function startSim(problem) {
  let payload = {};
  if (problem === "producer_consumer") {
    payload = {
      buffer_size: +document.getElementById("pc_buffer_size").value,
      num_producers: +document.getElementById("pc_num_producers").value,
      num_consumers: +document.getElementById("pc_num_consumers").value,
      items_per_producer: +document.getElementById("pc_items_per_producer").value,
    };
    resetChart("producer_consumer");
  } else if (problem === "dining_philosopher") {
    payload = {
      num_philosophers: +document.getElementById("dp_num_philosophers").value,
      eat_count: +document.getElementById("dp_eat_count").value,
      naive: document.getElementById("dp_naive").checked,
    };
    document.getElementById("dp_banner").textContent = "";
    resetChart("dining_philosopher");
  } else {
    payload = {
      num_readers: +document.getElementById("rw_num_readers").value,
      num_writers: +document.getElementById("rw_num_writers").value,
      read_times: +document.getElementById("rw_read_times").value,
      write_times: +document.getElementById("rw_write_times").value,
    };
    resetChart("reader_writer");
  }

  const res = await fetch("/api/start/" + problem, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) {
    alert(data.error || "Could not start simulation");
    return;
  }
  document.getElementById(shortName(problem) + "_output").value = "";
  poll(problem);
}

function shortName(problem) {
  return problem === "producer_consumer" ? "pc" : problem === "dining_philosopher" ? "dp" : "rw";
}

function poll(problem) {
  clearTimeout(pollTimers[problem]);

  fetch("/api/output/" + problem)
    .then(r => r.json())
    .then(data => {
      const short = shortName(problem);
      const outputBox = document.getElementById(short + "_output");
      outputBox.value = data.output;
      outputBox.scrollTop = outputBox.scrollHeight;

      if (problem === "producer_consumer") {
        const produced = (data.output.match(/produced:/g) || []).length;
        const consumed = (data.output.match(/consumed:/g) || []).length;
        const inFlight = produced - consumed;
        const bufferSize = +document.getElementById("pc_buffer_size").value;
        drawBuffer(bufferSize, inFlight);
        document.getElementById("pc_stats").textContent =
          `Produced: ${produced} | Consumed: ${consumed} | In-flight: ${inFlight}`;
        pushChartPoint("producer_consumer", produced, consumed);
      } else if (problem === "dining_philosopher") {
        const n = +document.getElementById("dp_num_philosophers").value;
        const meals = (data.output.match(/is eating using forks/g) || []).length;
        const recentLines = data.output.trim().split("\n").slice(-40);
        const eatingArray = new Array(n).fill(false);
        let eatingNow = 0;
        for (const line of recentLines) {
          const m = line.match(/Philosopher (\d+) is eating using forks/);
          if (m) {
            const id = +m[1];
            if (id < n) { eatingArray[id] = true; eatingNow++; }
          }
          const r = line.match(/Philosopher (\d+) released forks/);
          if (r) {
            const id = +r[1];
            if (id < n) eatingArray[id] = false;
          }
        }
        drawPhilosophers(n, eatingArray);
        document.getElementById("dp_stats").textContent = `Meals served: ${meals}`;
        pushChartPoint("dining_philosopher", meals, eatingNow);

        if (document.getElementById("dp_naive").checked && data.running && meals === 0 &&
            data.output.includes("tries to pick up fork")) {
          document.getElementById("dp_banner").textContent =
            "⚠ Possible deadlock — philosophers stuck waiting for forks";
        }
      } else {
        const reads = (data.output.match(/is reading/g) || []).length;
        const writes = (data.output.match(/is writing/g) || []).length;
        const numReaders = +document.getElementById("rw_num_readers").value;
        const numWriters = +document.getElementById("rw_num_writers").value;

        const recentLines = data.output.trim().split("\n").slice(-20);
        let activeReaders = 0;
        let writerActive = false;
        for (const line of recentLines) {
          if (line.includes("is reading...")) activeReaders++;
          if (line.includes("finished reading")) activeReaders = Math.max(0, activeReaders - 1);
          if (line.includes("is writing...")) writerActive = true;
          if (line.includes("finished writing")) writerActive = false;
        }
        drawReaderWriter(numReaders, numWriters, activeReaders, writerActive);
        document.getElementById("rw_stats").textContent = `Reads: ${reads} | Writes: ${writes}`;
        pushChartPoint("reader_writer", reads, writes);
      }

      if (data.running) {
        pollTimers[problem] = setTimeout(() => poll(problem), 400);
      }
    });
}

function control(action) {
  fetch("/api/control/" + action, { method: "POST" });
}

function quitServer() {
  if (!confirm("This stops the local server. You'll need to run 'python app.py' again to restart it. Continue?")) {
    return;
  }
  fetch("/api/shutdown", { method: "POST" })
    .then(() => {
      document.body.innerHTML =
        "<h2 style='text-align:center;margin-top:80px;'>Server stopped. " +
        "You can close this tab.</h2>";
    })
    .catch(() => {
      document.body.innerHTML =
        "<h2 style='text-align:center;margin-top:80px;'>Server stopped. " +
        "You can close this tab.</h2>";
    });
}

// initial empty draws
drawBuffer(5, 0);
drawPhilosophers(5, new Array(5).fill(false));
drawReaderWriter(3, 2, 0, false);