document.addEventListener("DOMContentLoaded", () => {
  const questionGrid = document.getElementById("question-grid");
  const form = document.getElementById("battle-form");
  const promptInput = document.getElementById("prompt-input");
  const results = document.getElementById("results");
  const outputA = document.getElementById("modelA-output");
  const outputB = document.getElementById("modelB-output");
  let selectedQuestion = null;

  // Load and display 3 random questions from CSV
fetch("../questions.tsv")
  .then(res => res.text())
  .then(text => {
    const questions = parseQuestions(text);
    console.log("Loaded", questions.length, "questions");

    // Choose 3 random ones
    const picks = [...questions].sort(() => 0.5 - Math.random()).slice(0, 3);

    // Display them
    const grid = document.querySelector(".question-grid");
    const input = document.querySelector("#prompt-box");

    picks.forEach(({ text }) => {
      const card = document.createElement("div");
      card.className = "question-card";
      card.textContent = text;
      card.addEventListener("click", () => {
        document.querySelectorAll(".question-card").forEach(c => c.classList.remove("selected"));
        card.classList.add("selected");
        input.value = text; // fill prompt box
      });
      grid.appendChild(card); 
    });
  });


  // Handle form submission
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const prompt = promptInput.value.trim();
    if (!prompt) return;

    results.classList.remove("hidden");
    outputA.textContent = "Generating response from Model A...";
    outputB.textContent = "Generating response from Model B...";

    const [resA, resB] = await Promise.all([
      fakeModelResponse("Model A", prompt),
      fakeModelResponse("Model B", prompt)
    ]);

    outputA.textContent = resA;
    outputB.textContent = resB;
  });

  // --- Helpers ---
function parseQuestions(text) {
  // Split by any kind of newline, trim extra whitespace, and remove blank lines
  return text
    .split(/\r?\n/)
    .map(line => line.trim())
    .filter(line => line.length > 0)
    .map((q, i) => ({ id: i + 1, text: q }));
}



  function getRandomSubset(arr, n) {
    const shuffled = arr.sort(() => 0.5 - Math.random());
    return shuffled.slice(0, n);
  }

  function fakeModelResponse(model, prompt) {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(`${model} says:\n\n"${prompt}"\n\n(Example simulated output for demo purposes.)`);
      }, 1000 + Math.random() * 800);
    });
  }
});
