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

    // Fetch real dimension scores from backend
    await loadDimensionData();

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

  async function loadDimensionData() {
    // Fetch aggregated dimension scores from backend
    const resp = await fetch(`${API_CONFIG.BACKEND_URL}/api/dimension-scores`);
    if (!resp.ok) throw new Error("Failed to fetch dimension scores");
    const data = await resp.json();
    
    const dimensionScores = data.dimension_scores || {};
    
    // Transform backend data to allDimensions structure
    allDimensions = {
      empathy: {},
      aggressiveness: {},
      evidence_use: {},
      political_economic: {},
      political_social: {}
    };
    
    // Populate with data from backend
    Object.entries(dimensionScores).forEach(([model, scores]) => {
      Object.keys(allDimensions).forEach(dim => {
        if (scores[dim] !== undefined) {
          allDimensions[dim][model] = scores[dim];
        }
      });
    });
    
    // If no data yet, show placeholder (0.5 for 0-1 scales, 0.0 for -1 to 1 scales)
    allModels.forEach(model => {
      if (!allDimensions.empathy[model]) {
        allDimensions.empathy[model] = 0.5;
      }
      if (!allDimensions.aggressiveness[model]) {
        allDimensions.aggressiveness[model] = 0.5;
      }
      if (!allDimensions.evidence_use[model]) {
        allDimensions.evidence_use[model] = 0.5;
      }
      if (!allDimensions.political_economic[model]) {
        allDimensions.political_economic[model] = 0.0;
      }
      if (!allDimensions.political_social[model]) {
        allDimensions.political_social[model] = 0.0;
      }
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

    // Generate sample tag frequencies (in production, query backend)
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
