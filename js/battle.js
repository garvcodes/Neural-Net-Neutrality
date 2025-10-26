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
    await submitVote(currentModelA, currentModelB, voteA, modelALabel.textContent);
  });

  voteB.addEventListener("click", async () => {
    await submitVote(currentModelB, currentModelA, voteB, modelBLabel.textContent);
  });

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