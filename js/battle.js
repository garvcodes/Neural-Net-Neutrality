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

  // Update model labels when selection changes
  modelASelect.addEventListener("change", (e) => {
    currentModelA = e.target.value;
    updateModelLabel(modelASelect, modelALabel);
  });

  modelBSelect.addEventListener("change", (e) => {
    currentModelB = e.target.value;
    updateModelLabel(modelBSelect, modelBLabel);
  });

  function updateModelLabel(selectElement, labelElement) {
    const selectedText = selectElement.options[selectElement.selectedIndex].text;
    labelElement.textContent = selectedText;
  }

  // Initialize labels
  updateModelLabel(modelASelect, modelALabel);
  updateModelLabel(modelBSelect, modelBLabel);

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
    await submitVote(currentModelA, currentModelB, voteA);
  });

  voteB.addEventListener("click", async () => {
    await submitVote(currentModelB, currentModelA, voteB);
  });

  async function submitVote(winnerModel, loserModel, button) {
    button.disabled = true;
    const originalText = button.textContent;
    button.textContent = "Voting...";

    try {
      const resp = await fetch(`${API_CONFIG.BACKEND_URL}/api/vote`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          winner_model: winnerModel,
          loser_model: loserModel,
          prompt: currentPrompt,
        }),
      });

      const data = await resp.json();
      if (data.success) {
        button.textContent = `✓ ${winnerModel.split('-')[0].toUpperCase()} now leads!`;
        setTimeout(() => {
          button.textContent = originalText;
          button.disabled = false;
        }, 2000);
      } else {
        button.textContent = "Vote failed";
        button.disabled = false;
      }
    } catch (err) {
      console.error("Vote error:", err);
      button.textContent = "Error voting";
      button.disabled = false;
    }
  }

  // --- Helpers ---
  function parseQuestions(text) {
    return text
      .split(/\r?\n/)
      .map(line => line.trim())
      .filter(line => line.length > 0)
      .map((q, i) => ({ id: i + 1, text: q }));
  }
    // --- Typewriter animation ---
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
  
});

