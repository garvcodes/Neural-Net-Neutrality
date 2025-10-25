document.addEventListener("DOMContentLoaded", () => {
  const tableBody = document.querySelector("#ratings-table tbody");

  // Example data — replace with fetch from your backend
  const models = [
    { name: "GPT-5", v1: 1810, v2: 1795, v5: 1820, elo: 1808 },
    { name: "Claude 3.5", v1: 1780, v2: 1770, v5: 1800, elo: 1783 },
    { name: "Gemini 2.0", v1: 1760, v2: 1755, v5: 1775, elo: 1763 },
    { name: "Mistral 8x7B", v1: 1720, v2: 1705, v5: 1730, elo: 1718 },
    { name: "LLaMA 3.1", v1: 1695, v2: 1675, v5: 1700, elo: 1690 }
  ];

  // Sort descending by Elo
  models.sort((a, b) => b.elo - a.elo);

  // Populate table
  models.forEach(model => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${model.name}</td>
      <td>${model.v1}</td>
      <td>${model.v2}</td>
      <td>${model.v5}</td>
      <td>${model.elo}</td>
    `;
    tableBody.appendChild(row);
  });
});
