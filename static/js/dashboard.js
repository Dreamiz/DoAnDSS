// static/js/dashboard.js

  let showingTop = true; // Mặc định hiển thị Top
  const toggleBtn = document.getElementById("toggleRankBtn"); // Nút chuyển đổi


  async function fetchChartData() {
  const res = await fetch("/api/chart-data");
  const data = await res.json();

  // Tổng hợp thống kê
  const totalViews = data.reduce((sum, ch) => sum + ch.views, 0);
  const totalSubs = data.reduce((sum, ch) => sum + ch.subscribers, 0);
  const totalChannels = data.length; 

  // Gán vào HTML
  document.getElementById("totalViews").innerText = totalViews.toLocaleString();
  document.getElementById("totalSubs").innerText = totalSubs.toLocaleString();
  document.getElementById("totalChannels").innerText = totalChannels.toLocaleString();

  // Tạo biểu đồ theo chế độ hiện tại
  updateCharts(data);
}

// Hàm sắp xếp và cắt top/bottom
function getRanked(names, values, N, top = true) {
  const combined = names.map((name, i) => ({ name, value: values[i] }));
  combined.sort((a, b) => b.value - a.value);
  const result = top ? combined.slice(0, N) : combined.slice(-N);
  return {
    names: result.map(item => item.name),
    values: result.map(item => item.value)
  };
}

function updateCharts(data) {
  const names = data.map(ch => ch.name);
  const views = data.map(ch => ch.views);
  const subs = data.map(ch => ch.subscribers);

  // Chọn top hoặc bottom 5
  const rankViews = getRanked(names, views, 5, showingTop);
  const rankSubs = getRanked(names, subs, 5, showingTop);

  // Xóa biểu đồ cũ (tránh chồng lớp)
  Chart.getChart("viewsChart")?.destroy();
  Chart.getChart("subsChart")?.destroy();


  // Biểu đồ lượt xem
  new Chart(document.getElementById("viewsChart"), {
    type: "bar",
    data: {
      labels: rankViews.names,
      datasets: [{
        label: "Lượt xem",
        data: rankViews.values,
        backgroundColor: "rgba(75, 192, 75, 0.5)", // xanh lá
        borderColor: "rgba(75, 192, 75, 1)",
        borderWidth: 1
      }]
    },
    options: {
      plugins: {
        legend: { labels: { color: "green" } },
        title: {
          display: true,
          text: showingTop ? "Top 5 kênh có lượt xem cao nhất" : "Top 5 kênh có lượt xem thấp nhất",
          color: "#333"
        }
      },
      scales: {
        x: { ticks: { color: "#333" } },
        y: { ticks: { color: "#333" } }
      }
    }
  });

  // Biểu đồ người đăng ký
  new Chart(document.getElementById("subsChart"), {
    type: "bar",
    data: {
      labels: rankSubs.names,
      datasets: [{
        label: "Người đăng ký",
        data: rankSubs.values,
        backgroundColor: "rgba(255, 99, 99, 0.5)", // đỏ
        borderColor: "rgba(255, 99, 99, 1)",
        borderWidth: 1
      }]
    },
    options: {
      plugins: {
        legend: { labels: { color: "red" } },
        title: {
          display: true,
          text: showingTop ? "Top 5 kênh có người đăng ký cao nhất" : "Top 5 kênh có người đăng ký thấp nhất",
          color: "#333"
        }
      },
      scales: {
        x: { ticks: { color: "#333" } },
        y: { ticks: { color: "#333" } }
      }
    }
  });


// Cập nhật nút chuyển
  if (toggleBtn)
    toggleBtn.textContent = showingTop ? "Xem kênh thấp nhất" : "Xem kênh cao nhất";
}

// Sự kiện nhấn nút chuyển đổi
if (toggleBtn) {
  toggleBtn.addEventListener("click", async () => {
    showingTop = !showingTop;
    const res = await fetch("/api/chart-data");
    const data = await res.json();
    updateCharts(data);
  });


}

fetchChartData();
