document.addEventListener("DOMContentLoaded", () => {
  const tableBody = document.querySelector("#ratings-table tbody");
  const statusEl = document.querySelector(".ratings-subtitle") || null;

  // Fetch live ratings from backend
  async function loadRatings() {
    try {
      const resp = await fetch(`${API_CONFIG.BACKEND_URL}/api/ratings`);
      const data = await resp.json();
      
      const ratings = data.ratings || {};
      
      // Convert ratings object to sortable array
      const models = Object.entries(ratings).map(([model, stats]) => ({
        name: model,
        elo: stats.rating || 1600,
        wins: stats.wins || 0,
        losses: stats.losses || 0,
        total: (stats.wins || 0) + (stats.losses || 0),
      }));
      
      // Sort by Elo descending
      models.sort((a, b) => b.elo - a.elo);
      
      // Clear existing rows
      tableBody.innerHTML = "";
      
      // Populate table
      models.forEach((model, index) => {
        const row = document.createElement("tr");
        const winRate = model.total > 0 ? ((model.wins / model.total) * 100).toFixed(1) : "—";
        row.innerHTML = `
          <td><strong>${index + 1}. ${model.name}</strong></td>
          <td>${model.elo.toFixed(0)}</td>
          <td>${model.wins}</td>
          <td>${model.losses}</td>
          <td>${winRate}${winRate !== "—" ? "%" : ""}</td>
        `;
        tableBody.appendChild(row);
      });
    } catch (err) {
      console.error("Failed to load ratings:", err);
      tableBody.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 2rem;">Failed to load ratings. ${err.message}</td></tr>`;
    }
  }

  // Load ratings on page load
  loadRatings();
  
  // Refresh ratings every 10 seconds
  setInterval(loadRatings, 10000);
});

