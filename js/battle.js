document.addEventListener("DOMContentLoaded", () => {
  const questionGrid = document.getElementById("question-grid");
  const form = document.getElementById("battle-form");
  const promptInput = document.getElementById("prompt-input");
  const results = document.getElementById("results");
  const outputA = document.getElementById("modelA-output");
  const outputB = document.getElementById("modelB-output");

  // --- Load and display 3 random questions from TSV ---
  fetch("../questions.tsv")
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

    results.classList.remove("hidden");
    outputA.classList.add("loading-text");
    outputB.classList.add("loading-text");
    outputA.textContent = "Getting response from OpenAI...";
    outputB.textContent = "Getting response from Gemini...";

    try {
      const resp = await fetch(`${API_CONFIG.BACKEND_URL}/api/battle`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });

      const data = await resp.json();
      outputA.classList.remove("loading-text");
      outputB.classList.remove("loading-text");

      // Typewriter reveal for both outputs
      await Promise.all([
        typeWriter(outputA, data.openai || "No response from OpenAI."),
        typeWriter(outputB, data.gemini || "No response from Gemini."),
      ]);
    } catch (err) {
      outputA.textContent = "Error contacting server.";
      outputB.textContent = "Error contacting server.";
      console.error(err);
    }
  });

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

