// static/js/dashboard.js

  const menuBtn = document.getElementById("menuBtn");
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("overlay");

    menuBtn.addEventListener("click", () => {
      sidebar.classList.toggle("open");
      overlay.classList.toggle("show");
    });

    overlay.addEventListener("click", () => {
      sidebar.classList.remove("open");
      overlay.classList.remove("show");
    });

  function toggleUserMenu() {
    const menu = document.getElementById("userMenu");
    menu.classList.toggle("show");
  }

  // Đóng menu user nếu click ra ngoài
  document.addEventListener("click", (e) => {
    const menu = document.getElementById("userMenu");
    const btn = document.querySelector(".user-btn");
    if (!btn.contains(e.target) && !menu.contains(e.target)) {
      menu.classList.remove("show");
    }
  });

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
function getRanked(names, values, categories, N, top = true) {
  // Gom name, value, category thành một mảng đối tượng
  const combined = names.map((name, i) => ({
    name,
    value: values[i],
    category: categories[i]
  }));

  // Sắp xếp giảm dần theo value
  combined.sort((a, b) => b.value - a.value);

  // Lấy top N hoặc bottom N
  const result = top ? combined.slice(0, N) : combined.slice(-N);

  // Trả kết quả gồm 3 mảng
  return {
    names: result.map(item => item.name),
    values: result.map(item => item.value),
    categories: result.map(item => item.category)
  };
}


function updateCharts(data) {
  const N = parseInt(numInput?.value) || 5; // Lấy số N từ input, mặc định 5
  const names = data.map(ch => ch.name);
  const views = data.map(ch => ch.views);
  const subs = data.map(ch => ch.subscribers);
  const categories = data.map(ch => ch.category);


  const rankViews = getRanked(names, views, categories, parseInt(document.getElementById("numInput").value), showingTop);
  const rankSubs = getRanked(names, subs, categories, parseInt(document.getElementById("numInput").value), showingTop);


  // Xóa biểu đồ cũ để tránh chồng lớp
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
        backgroundColor: "rgba(75, 192, 75, 0.5)",
        borderColor: "rgba(75, 192, 75, 1)",
        borderWidth: 1
      }]
    },
    options: {
      plugins: {
        legend: { labels: { color: "green" } },
        title: {
          display: true,
          text: showingTop
            ? `Top ${N} kênh có lượt xem cao nhất`
            : `Top ${N} kênh có lượt xem thấp nhất`,
          color: "#333"
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              const cat = rankViews.categories[context.dataIndex];
              return `${context.dataset.label}: ${context.formattedValue} (${cat})`;
            }
          }
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
        backgroundColor: "rgba(255, 99, 99, 0.5)",
        borderColor: "rgba(255, 99, 99, 1)",
        borderWidth: 1
      }]
    },
    options: {
      plugins: {
        legend: { labels: { color: "red" } },
        title: {
          display: true,
          text: showingTop
            ? `Top ${N} kênh có người đăng ký cao nhất`
            : `Top ${N} kênh có người đăng ký thấp nhất`,
          color: "#333"
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              const cat = rankSubs.categories[context.dataIndex];
              return `${context.dataset.label}: ${context.formattedValue} (${cat})`;
            }
          }
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

// Khi nhập số và nhấn Enter hoặc mất focus → cập nhật biểu đồ
if (numInput) {
  numInput.addEventListener("change", async () => {
    const res = await fetch("/api/chart-data");
    const data = await res.json();
    updateCharts(data);
  });
}

// Sự kiện nhấn nút "?" để hiện message box
document.addEventListener("DOMContentLoaded", () => {
  const helpBtn = document.getElementById("help-btn");

  if (helpBtn) {
    helpBtn.addEventListener("click", () => {
      alert(
        "📊 Giải thích nhãn:\n\n" +
        "🟢 Viral: Kênh có lượt xem và đăng ký tăng đột biến, xu hướng lan truyền mạnh.\n" +
        "🔵 Trend: Kênh có chỉ số vượt xa trung bình nhóm, hiệu suất rất cao.\n" +
        "🟡 Developing: Đăng ký cao nhưng lượt xem tăng chậm.\n" +
        "🔴 NotViral: Lượt xem thấp hơn mức trung bình."
      );
    });
  }
});

document.addEventListener("DOMContentLoaded", () => {
  const buttons = document.querySelectorAll(".filter-btn");
  const rows = document.querySelectorAll("table tbody tr");

  // 🔹 Gán màu highlight riêng theo nhãn
  const labelColors = {
    "Viral": "rgba(6, 157, 19, 0.2)",       // Xanh lá
    "Trend": "rgba(40, 114, 217, 0.2)",     // Xanh dương
    "Developing": "rgba(238, 202, 21, 0.25)", // Vàng
    "NotViral": "rgba(230, 50, 14, 0.2)"     // Đỏ
  };

  // Khi nhấn nút filter
  buttons.forEach(btn => {
    btn.addEventListener("click", () => {
      btn.classList.toggle("active");
      applyFilter();
    });
  });

  function applyFilter() {
    const activeLabels = Array.from(buttons)
      .filter(b => b.classList.contains("active"))
      .map(b => b.dataset.label);

    rows.forEach(row => {
      const labelCell = row.querySelector("td:last-child");
      const labelText = labelCell ? labelCell.textContent.trim() : "";

      // Nếu không chọn nút nào => reset lại
      if (activeLabels.length === 0) {
        row.style.backgroundColor = "";
        row.classList.remove("dim-row");
        return;
      }

      // Nếu nhãn trùng với filter đang bật
      if (activeLabels.includes(labelText)) {
        row.style.backgroundColor = labelColors[labelText] || "rgba(0, 168, 255, 0.15)";
        row.classList.remove("dim-row");
      } else {
        row.style.backgroundColor = "";
        row.classList.add("dim-row");
      }
    });
  }
});
fetchChartData();
