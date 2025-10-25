document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("battle-form");
  const results = document.getElementById("results");
  const promptInput = document.getElementById("prompt-input");
  const outputA = document.getElementById("modelA-output");
  const outputB = document.getElementById("modelB-output");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const prompt = promptInput.value.trim();
    if (!prompt) return;

    results.classList.remove("hidden");
    outputA.textContent = "Generating response from Model A...";
    outputB.textContent = "Generating response from Model B...";

    // Simulate async API calls
    const [resA, resB] = await Promise.all([
      fakeModelResponse("Model A", prompt),
      fakeModelResponse("Model B", prompt)
    ]);

    outputA.textContent = resA;
    outputB.textContent = resB;
  });

  // Mock: replace with your actual backend/API call
  function fakeModelResponse(model, prompt) {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(`${model} says:\n\nThis is a simulated answer for the prompt:\n"${prompt}"\n\n— end of response —`);
      }, 1000 + Math.random() * 1000);
    });
  }
});
