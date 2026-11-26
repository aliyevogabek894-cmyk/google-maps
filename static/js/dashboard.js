(function () {
  "use strict";

  const dataNode = document.getElementById("dashboardChartData");
  const canvas = document.getElementById("trafficChart");
  if (!dataNode || !canvas) return;

  let payload;
  try {
    payload = JSON.parse(dataNode.textContent);
  } catch (e) {
    return;
  }

  const labels = payload.labels || [];
  const pageViews = payload.page_views || [];
  const googleClicks = payload.google_clicks || [];
  const yandexClicks = payload.yandex_clicks || [];

  if (typeof window.Chart !== "undefined") {
    new window.Chart(canvas.getContext("2d"), {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Sahifa ko‘rishlari",
            data: pageViews,
            borderColor: "#0B1F3A",
            backgroundColor: "rgba(11, 31, 58, 0.1)",
            tension: 0.28,
            fill: true
          },
          {
            label: "Google tugmasi (saytdan)",
            data: googleClicks,
            borderColor: "#C9973B",
            backgroundColor: "rgba(201, 151, 59, 0.12)",
            tension: 0.25
          },
          {
            label: "Yandex tugmasi (saytdan)",
            data: yandexClicks,
            borderColor: "#D94E34",
            backgroundColor: "rgba(217, 78, 52, 0.1)",
            tension: 0.25
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "bottom" }
        },
        scales: {
          y: { beginAtZero: true, ticks: { precision: 0 } }
        }
      }
    });
    return;
  }

  // Oflayn muhit uchun sodda Canvas zaxira grafigi
  const ctx = canvas.getContext("2d");
  const w = (canvas.width = canvas.parentElement.clientWidth || 640);
  const h = (canvas.height = 280);
  ctx.clearRect(0, 0, w, h);
  ctx.font = "12px sans-serif";

  if (!labels.length) {
    ctx.fillStyle = "#4B5D73";
    ctx.fillText("Tanlangan sana oralig‘ida ma’lumot topilmadi.", 20, 40);
    return;
  }

  const maxVal = Math.max(1, ...pageViews, ...googleClicks, ...yandexClicks);
  const padL = 42, padR = 16, padT = 20, padB = 34;
  const chartW = w - padL - padR;
  const chartH = h - padT - padB;

  ctx.strokeStyle = "#DCE3ED";
  ctx.beginPath();
  ctx.moveTo(padL, padT);
  ctx.lineTo(padL, padT + chartH);
  ctx.lineTo(padL + chartW, padT + chartH);
  ctx.stroke();

  function drawSeries(arr, color) {
    if (!arr.length) return;
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.2;
    ctx.beginPath();
    arr.forEach(function (val, idx) {
      const x = padL + (arr.length === 1 ? chartW / 2 : (idx / (arr.length - 1)) * chartW);
      const y = padT + chartH - (val / maxVal) * chartH;
      if (idx === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
  }

  drawSeries(pageViews, "#0B1F3A");
  drawSeries(googleClicks, "#C9973B");
  drawSeries(yandexClicks, "#D94E34");

  ctx.fillStyle = "#4B5D73";
  ctx.fillText("0", 12, padT + chartH);
  ctx.fillText(String(maxVal), 12, padT + 10);
  ctx.fillText(labels[0], padL, h - 10);
  if (labels.length > 1) {
    ctx.fillText(labels[labels.length - 1], w - 70, h - 10);
  }
})();
