function updateModelLabel(selectElement, labelElement) {
  const selectedText = selectElement.options[selectElement.selectedIndex].text;
  labelElement.textContent = selectedText;
}

function parseQuestions(text) {
  return text
    .split(/\r?\n/)
    .map(line => line.trim())
    .filter(line => line.length > 0)
    .map((q, i) => ({ id: i + 1, text: q }));
}

async function typeWriter(element, text) {
  element.textContent = "";
  element.classList.add("typing");
  const delay = 12; // ms per character

  for (let i = 0; i < text.length; i++) {
    element.textContent += text[i];
    await new Promise((r) => setTimeout(r, delay));
    element.scrollTop = element.scrollHeight; // auto-scroll
  }

  element.classList.remove("typing");
}

document.addEventListener("DOMContentLoaded", () => {
  const questionGrid = document.getElementById("question-grid");
  const form = document.getElementById("battle-form");
  const promptInput = document.getElementById("prompt-input");
  const results = document.getElementById("results");
  const outputA = document.getElementById("modelA-output");
  const outputB = document.getElementById("modelB-output");
  const voteA = document.getElementById("vote-a");
  const voteB = document.getElementById("vote-b");
  const modelASelect = document.getElementById("model-a-select");
  const modelBSelect = document.getElementById("model-b-select");
  const modelALabel = document.getElementById("model-a-label");
  const modelBLabel = document.getElementById("model-b-label");

  let currentPrompt = "";
  let currentModelA = "gpt-4o-mini";
  let currentModelB = "gemini-2.0-flash";

  // Map API model IDs to display names (matching your database)
  const modelDisplayNames = {
    "gpt-4o-mini": "OpenAI GPT-4o Mini",
    "gpt-4o": "OpenAI GPT-4o",
    "gpt-3.5-turbo": "OpenAI GPT-3.5 Turbo",
    "claude-3-haiku-20240307": "Claude 3 Haiku",
    "claude-3-sonnet-20240229": "Claude 3 Sonnet",
    "gemini-1.5-pro": "Gemini 1.5 Pro",
    "gemini-2.0-flash": "Gemini 2.0 Flash"
  };

  // Initialize labels immediately
  updateModelLabel(modelASelect, modelALabel);
  updateModelLabel(modelBSelect, modelBLabel);

  // Update model labels when selection changes
  modelASelect.addEventListener("change", (e) => {
    currentModelA = e.target.value;
    updateModelLabel(modelASelect, modelALabel);
  });

  modelBSelect.addEventListener("change", (e) => {
    currentModelB = e.target.value;
    updateModelLabel(modelBSelect, modelBLabel);
  });

  // --- Load and display 3 random questions from TSV ---
  fetch("./questions.tsv")
    .then(res => res.text())
    .then(text => {
      const questions = parseQuestions(text);
      console.log("Loaded", questions.length, "questions");

      const picks = [...questions].sort(() => 0.5 - Math.random()).slice(0, 3);
      picks.forEach(({ text }) => {
        const card = document.createElement("div");
        card.className = "question-card";
        card.textContent = text;
        card.addEventListener("click", () => {
          document.querySelectorAll(".question-card").forEach(c => c.classList.remove("selected"));
          card.classList.add("selected");
          promptInput.value = text; // fill text area
        });
        questionGrid.appendChild(card);
      });
    });

  // --- Handle form submission ---
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const prompt = promptInput.value.trim();
    if (!prompt) return;

    currentPrompt = prompt;
    results.classList.remove("hidden");
    outputA.classList.add("loading-text");
    outputB.classList.add("loading-text");
    outputA.textContent = `Getting response from ${modelALabel.textContent}...`;
    outputB.textContent = `Getting response from ${modelBLabel.textContent}...`;
    voteA.disabled = true;
    voteB.disabled = true;
    voteA.textContent = "Vote: Fairer Response";
    voteB.textContent = "Vote: Fairer Response";

    try {
      const resp = await fetch(`${API_CONFIG.BACKEND_URL}/api/battle`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          prompt,
          model_a: currentModelA,
          model_b: currentModelB,
        }),
      });

      const data = await resp.json();
      outputA.classList.remove("loading-text");
      outputB.classList.remove("loading-text");

      // Typewriter reveal for both outputs
      await Promise.all([
        typeWriter(outputA, data.openai || "No response."),
        typeWriter(outputB, data.gemini || "No response."),
      ]);
      
      // Enable vote buttons after responses are shown
      voteA.disabled = false;
      voteB.disabled = false;
    } catch (err) {
      outputA.textContent = "Error contacting server.";
      outputB.textContent = "Error contacting server.";
      console.error(err);
      voteA.disabled = true;
      voteB.disabled = true;
    }
  });

  // --- Vote handlers ---
  voteA.addEventListener("click", async () => {
    showTagModal(currentModelA, currentModelB, voteA);
  });

  voteB.addEventListener("click", async () => {
    showTagModal(currentModelB, currentModelA, voteB);
  });

  // Tag modal functions
  const voteModal = document.getElementById("vote-modal");
  const tagForm = document.getElementById("tag-form");
  const modalClose = document.getElementById("modal-close");
  const skipTagsBtn = document.getElementById("skip-tags-btn");
  const modalOverlay = voteModal.querySelector(".modal-content");

  let pendingVote = { winner: null, loser: null, button: null };

  function showTagModal(winnerModel, loserModel, button) {
    pendingVote = { winner: winnerModel, loser: loserModel, button };
    voteModal.classList.remove("hidden");
    tagForm.reset();
    document.getElementById("dimension-scores").classList.add("hidden");
  }

  function closeTagModal() {
    voteModal.classList.add("hidden");
    tagForm.reset();
    pendingVote = { winner: null, loser: null, button: null };
    document.getElementById("dimension-scores").classList.add("hidden");
  }

  modalClose.addEventListener("click", closeTagModal);
  skipTagsBtn.addEventListener("click", async () => {
    // Submit vote without tags
    await submitVoteWithTags(pendingVote.winner, pendingVote.loser, [], pendingVote.button);
    closeTagModal();
  });

  voteModal.addEventListener("click", (e) => {
    if (e.target === voteModal) {
      closeTagModal();
    }
  });

  // Tag form submission
  tagForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const selectedTags = Array.from(
      tagForm.querySelectorAll('input[name="tags"]:checked')
    ).map(input => input.value);
    
    await submitVoteWithTags(
      pendingVote.winner,
      pendingVote.loser,
      selectedTags,
      pendingVote.button
    );
    
    closeTagModal();
  });

  async function submitVoteWithTags(winnerModel, loserModel, tags, button) {
    button.disabled = true;
    const originalText = button.textContent;
    button.textContent = "Voting...";

    try {
      const response = await fetch(`${API_CONFIG.BACKEND_URL}/api/vote-with-tags`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          winner_model: winnerModel,
          loser_model: loserModel,
          tags: tags,
          topic: currentPrompt,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Vote failed");
      }

      const data = await response.json();
      if (data.success) {
        button.textContent = `✓ Vote recorded! (${data.tags_recorded} tags)`;
        
        // Show dimension scores if tags were selected
        if (data.tags_recorded > 0) {
          displayDimensionScores(data.dimension_scores);
        }
        
        setTimeout(() => {
          button.textContent = originalText;
          button.disabled = false;
        }, 3000);
      } else {
        throw new Error("Vote was not recorded");
      }
    } catch (err) {
      console.error("Vote error:", err);
      button.textContent = "Error voting";
      button.disabled = false;
    }
  }

  function displayDimensionScores(scores) {
    const dimensionScores = document.getElementById("dimension-scores");
    const dimensionBars = document.getElementById("dimension-bars");
    
    let html = "";
    const dimensions = [
      { key: "empathy", label: "Empathy", range: [0, 1] },
      { key: "aggressiveness", label: "Aggressiveness", range: [0, 1] },
      { key: "evidence_use", label: "Evidence Use", range: [0, 1] },
      { key: "political_economic", label: "Political (Economic)", range: [-1, 1] },
      { key: "political_social", label: "Political (Social)", range: [-1, 1] }
    ];
    
    for (const dim of dimensions) {
      const score = scores[dim.key] || 0.5;
      const [min, max] = dim.range;
      
      // Normalize score to 0-100% for display
      const percentage = ((score - min) / (max - min)) * 100;
      
      html += `
        <div class="dimension-bar">
          <label>${dim.label}</label>
          <div class="bar">
            <div class="fill" style="width: ${percentage}%"></div>
          </div>
          <span class="value">${score.toFixed(2)}</span>
        </div>
      `;
    }
    
    dimensionBars.innerHTML = html;
    dimensionScores.classList.remove("hidden");
  }

  async function submitVote(winnerModelId, loserModelId, button, displayName) {
    // Disable both buttons to prevent double voting
    voteA.disabled = true;
    voteB.disabled = true;
    
    const originalText = button.textContent;
    button.textContent = "Submitting vote...";

    try {
      // Use display names for database (matching your init_database models)
      const winnerName = modelDisplayNames[winnerModelId];
      const loserName = modelDisplayNames[loserModelId];

      console.log("Voting:", { winner: winnerName, loser: loserName });

      const resp = await fetch(`http://127.0.0.1:8000/api/vote`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          winner_model: winnerName,
          loser_model: loserName,
          prompt: currentPrompt,
        }),
      });

      const data = await resp.json();
      console.log("Vote response:", data);

      if (data.success) {
        // Show new ratings if available
        const ratingInfo = data.new_ratings 
          ? ` (${data.new_ratings.winner.toFixed(0)} → ${data.new_ratings.loser.toFixed(0)})`
          : '';
        
        button.textContent = `✓ Vote recorded!${ratingInfo}`;
        
        // Keep buttons disabled after vote
        setTimeout(() => {
          button.textContent = "✓ Already voted";
        }, 2000);
      } else {
        button.textContent = "Vote failed: " + (data.error || "Unknown error");
        // Re-enable buttons on failure
        setTimeout(() => {
          voteA.disabled = false;
          voteB.disabled = false;
          button.textContent = originalText;
        }, 3000);
      }
    } catch (err) {
      console.error("Vote error:", err);
      button.textContent = "Network error";
      // Re-enable buttons on error
      setTimeout(() => {
        voteA.disabled = false;
        voteB.disabled = false;
        button.textContent = originalText;
      }, 3000);
    }
  }

});