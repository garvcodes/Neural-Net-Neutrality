// js/tag-analytics.js
// Tag Analytics Dashboard

document.addEventListener("DOMContentLoaded", async () => {
  const loadingState = document.getElementById("loading-state");
  const errorState = document.getElementById("error-state");
  const errorMessage = document.getElementById("error-message");
  const modelFilter = document.getElementById("model-filter");
  const compareModel1 = document.getElementById("compare-model-1");
  const compareModel2 = document.getElementById("compare-model-2");

  let allModels = [];
  let allTags = {};
  let allDimensions = {};

  // Show loading state
  loadingState.classList.remove("hidden");

  try {
    // Fetch ratings and tags data
    const ratingsResp = await fetch(`${API_CONFIG.BACKEND_URL}/api/ratings`);
    if (!ratingsResp.ok) throw new Error("Failed to fetch ratings");
    const ratingsData = await ratingsResp.json();

    const tagsResp = await fetch(`${API_CONFIG.BACKEND_URL}/api/tags`);
    if (!tagsResp.ok) throw new Error("Failed to fetch tags");
    const tagsData = await tagsResp.json();

    allTags = tagsData.tags;
    allModels = Object.keys(ratingsData.ratings).sort();

    // Initialize filter and comparison selects
    populateSelects(allModels);

    // Generate sample dimension data (in production, this would come from backend)
    generateDimensionData(allModels);

    // Display initial charts
    displayDimensions(allModels);
    displayTagFrequency();

    // Add event listeners
    modelFilter.addEventListener("change", () => {
      const filtered = modelFilter.value ? [modelFilter.value] : allModels;
      displayDimensions(filtered);
    });

    compareModel1.addEventListener("change", updateComparison);
    compareModel2.addEventListener("change", updateComparison);

    loadingState.classList.add("hidden");

  } catch (err) {
    console.error("Error loading analytics:", err);
    errorMessage.textContent = `Error: ${err.message}`;
    errorState.classList.remove("hidden");
    loadingState.classList.add("hidden");
  }

  function populateSelects(models) {
    const options = models.map(m => `<option value="${m}">${m}</option>`).join("");
    modelFilter.innerHTML = '<option value="">All Models</option>' + options;
    compareModel1.innerHTML = '<option value="">Select Model 1</option>' + options;
    compareModel2.innerHTML = '<option value="">Select Model 2</option>' + options;
  }

  function generateDimensionData(models) {
    // Generate sample dimension scores for each model
    // In production, this would be calculated from actual votes with tags
    const dimensions = [
      "empathy",
      "aggressiveness",
      "evidence_use",
      "political_economic",
      "political_social"
    ];

    allDimensions = {};
    dimensions.forEach(dim => {
      allDimensions[dim] = {};
      models.forEach(model => {
        // Generate semi-random but deterministic scores based on model name
        const seed = model.split('').reduce((s, c) => s + c.charCodeAt(0), 0);
        const ranges = {
          empathy: [0.4, 0.8],
          aggressiveness: [0.3, 0.7],
          evidence_use: [0.5, 0.9],
          political_economic: [-0.5, 0.5],
          political_social: [-0.5, 0.5]
        };
        const [min, max] = ranges[dim];
        allDimensions[dim][model] = min + ((seed % 100) / 100) * (max - min);
      });
    });
  }

  function displayDimensions(models) {
    const dimensionIds = [
      "empathy",
      "aggressiveness",
      "evidence_use",
      "political_economic",
      "political_social"
    ];

    dimensionIds.forEach(dimId => {
      const chartEl = document.getElementById(`${dimId}-chart`);
      const leaderboardEl = document.getElementById(`${dimId}-leaderboard`);

      // Sort models by their dimension score
      const sorted = models.slice().sort(
        (a, b) => (allDimensions[dimId][b] || 0) - (allDimensions[dimId][a] || 0)
      );

      // Display chart
      let chartHTML = "";
      sorted.forEach(model => {
        const score = allDimensions[dimId][model] || 0.5;
        const percentage = ((score + 1) / 2) * 100; // Normalize to 0-100
        chartHTML += `
          <div class="chart-bar">
            <div class="bar-fill" style="height: ${percentage}%"></div>
            <div class="bar-label">${model.split('-')[0]}</div>
            <div class="bar-value">${score.toFixed(2)}</div>
          </div>
        `;
      });
      chartEl.innerHTML = chartHTML;

      // Display leaderboard
      let leaderboardHTML = "";
      sorted.slice(0, 5).forEach((model, idx) => {
        const score = allDimensions[dimId][model] || 0.5;
        leaderboardHTML += `
          <div class="leaderboard-row">
            <span class="leaderboard-rank">#${idx + 1}</span>
            <span class="leaderboard-model">${model}</span>
            <span class="leaderboard-score">${score.toFixed(2)}</span>
          </div>
        `;
      });
      leaderboardEl.innerHTML = leaderboardHTML;
    });
  }

  function displayTagFrequency() {
    const tagCategories = {
      tone: document.getElementById("tone-tags"),
      reasoning: document.getElementById("reasoning-tags"),
      structure: document.getElementById("structure-tags"),
      content: document.getElementById("content-tags")
    };

    // Generate sample tag frequencies
    const tagFrequencies = {};
    Object.values(allTags).forEach((categoryTags, idx) => {
      Object.keys(categoryTags).forEach(tag => {
        tagFrequencies[tag] = Math.floor(Math.random() * 100) + 10;
      });
    });

    // Display tags by category
    Object.entries(allTags).forEach(([category, tags]) => {
      const container = tagCategories[category];
      if (!container) return;

      let html = "";
      Object.entries(tags)
        .map(([tagName, desc]) => ({
          name: tagName,
          desc: desc,
          count: tagFrequencies[tagName] || 0
        }))
        .sort((a, b) => b.count - a.count)
        .forEach(tag => {
          html += `
            <div class="tag-item">
              <span class="tag-name">${tag.name.replace(/_/g, ' ')}</span>
              <span class="tag-count">${tag.count}</span>
            </div>
          `;
        });

      container.innerHTML = html;
    });
  }

  function updateComparison() {
    const model1 = compareModel1.value;
    const model2 = compareModel2.value;

    if (!model1 || !model2) {
      document.getElementById("comparison-chart").classList.add("hidden");
      return;
    }

    const comparisonChart = document.getElementById("comparison-chart");
    const dimensionLabels = [
      "empathy",
      "aggressiveness",
      "evidence_use",
      "political_economic",
      "political_social"
    ];

    let html = `
      <div class="comparison-model">
        <div class="comparison-model-title">${model1}</div>
    `;

    dimensionLabels.forEach(dim => {
      const score = allDimensions[dim][model1] || 0.5;
      const percentage = ((score + 1) / 2) * 100;
      html += `
        <div class="comparison-dimension-row">
          <span class="comparison-dimension-label">${dim.replace(/_/g, ' ')}</span>
          <div class="comparison-bar-container">
            <div class="comparison-bar-fill" style="width: ${percentage}%"></div>
          </div>
        </div>
      `;
    });

    html += `
      </div>
      <div class="comparison-model">
        <div class="comparison-model-title">${model2}</div>
    `;

    dimensionLabels.forEach(dim => {
      const score = allDimensions[dim][model2] || 0.5;
      const percentage = ((score + 1) / 2) * 100;
      html += `
        <div class="comparison-dimension-row">
          <span class="comparison-dimension-label">${dim.replace(/_/g, ' ')}</span>
          <div class="comparison-bar-container">
            <div class="comparison-bar-fill" style="width: ${percentage}%"></div>
          </div>
        </div>
      `;
    });

    html += `</div>`;
    comparisonChart.innerHTML = html;
    comparisonChart.classList.remove("hidden");
  }
});
