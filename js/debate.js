function updateModelLabel(selectElement, labelElement) {
  const selectedText = selectElement.options[selectElement.selectedIndex].text;
  labelElement.textContent = selectedText;
}

async function typeWriter(element, text, speed = 12) {
  element.textContent = "";
  element.classList.add("typing");

  for (let i = 0; i < text.length; i++) {
    element.textContent += text[i];
    await new Promise((r) => setTimeout(r, speed));
    element.scrollTop = element.scrollHeight; // auto-scroll
  }

  element.classList.remove("typing");
}

document.addEventListener("DOMContentLoaded", () => {
  const proSelect = document.getElementById("model-pro-select");
  const conSelect = document.getElementById("model-con-select");
  const proLabel = document.getElementById("pro-label");
  const conLabel = document.getElementById("con-label");
  const topicInput = document.getElementById("topic-input");
  const startDebateBtn = document.getElementById("start-debate-btn");
  const loadingState = document.getElementById("loading-state");
  const debateResults = document.getElementById("debate-results");
  const errorState = document.getElementById("error-state");
  const errorMessage = document.getElementById("error-message");
  const retryBtn = document.getElementById("retry-btn");
  const newDebateBtn = document.getElementById("new-debate-btn");
  const proArgument = document.getElementById("pro-argument");
  const conArgument = document.getElementById("con-argument");
  const topicDisplay = document.getElementById("topic-display");
  const votePro = document.getElementById("vote-pro");
  const voteCon = document.getElementById("vote-con");

  let currentTopic = "";
  let currentModelPro = "gpt-4o-mini";
  let currentModelCon = "gemini-2.0-flash";

  // Initialize labels
  updateModelLabel(proSelect, proLabel);
  updateModelLabel(conSelect, conLabel);

  // Update labels when selection changes
  proSelect.addEventListener("change", (e) => {
    currentModelPro = e.target.value;
    updateModelLabel(proSelect, proLabel);
  });

  conSelect.addEventListener("change", (e) => {
    currentModelCon = e.target.value;
    updateModelLabel(conSelect, conLabel);
  });

  // Helper function to show error
  function showError(message) {
    errorMessage.textContent = message;
    errorState.classList.remove("hidden");
    loadingState.classList.add("hidden");
    debateResults.classList.add("hidden");
  }

  // Helper function to hide error
  function hideError() {
    errorState.classList.add("hidden");
  }

  // Helper function to reset UI
  function resetUI() {
    topicInput.value = "";
    debateResults.classList.add("hidden");
    loadingState.classList.add("hidden");
    errorState.classList.add("hidden");
    proArgument.textContent = "";
    conArgument.textContent = "";
  }

  // Start Debate Button
  startDebateBtn.addEventListener("click", async () => {
    const topic = topicInput.value.trim();
    if (!topic) {
      showError("Please enter a debate topic.");
      return;
    }

    currentTopic = topic;
    hideError();
    loadingState.classList.remove("hidden");
    debateResults.classList.add("hidden");
    startDebateBtn.disabled = true;
    topicInput.disabled = true;
    proSelect.disabled = true;
    conSelect.disabled = true;

    try {
      const response = await fetch(`${API_CONFIG.BACKEND_URL}/api/debate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic: currentTopic,
          model_pro: currentModelPro,
          model_con: currentModelCon,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to start debate");
      }

      const data = await response.json();
      loadingState.classList.add("hidden");

      // Display the debate
      topicDisplay.textContent = currentTopic;

      // Typewriter reveal for both arguments
      await Promise.all([
        typeWriter(proArgument, data.pro_argument || "No argument provided.", 8),
        typeWriter(conArgument, data.con_argument || "No argument provided.", 8),
      ]);

      debateResults.classList.remove("hidden");
      votePro.disabled = false;
      voteCon.disabled = false;
    } catch (err) {
      showError(`Error: ${err.message || "Failed to start debate"}`);
      console.error(err);
    } finally {
      startDebateBtn.disabled = false;
      topicInput.disabled = false;
      proSelect.disabled = false;
      conSelect.disabled = false;
    }
  });

  // New Debate Button
  newDebateBtn.addEventListener("click", () => {
    resetUI();
    votePro.textContent = "Vote: Pro Wins";
    voteCon.textContent = "Vote: Con Wins";
    votePro.disabled = false;
    voteCon.disabled = false;
  });

  // Retry Button
  retryBtn.addEventListener("click", () => {
    hideError();
    startDebateBtn.click();
  });

  // Vote Handlers
  votePro.addEventListener("click", async () => {
    await submitVote(currentModelPro, currentModelCon, votePro);
  });

  voteCon.addEventListener("click", async () => {
    await submitVote(currentModelCon, currentModelPro, voteCon);
  });

  async function submitVote(winnerModel, loserModel, button) {
    button.disabled = true;
    const originalText = button.textContent;
    button.textContent = "Voting...";

    try {
      const response = await fetch(`${API_CONFIG.BACKEND_URL}/api/vote`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          winner_model: winnerModel,
          loser_model: loserModel,
          prompt: currentTopic,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Vote failed");
      }

      const data = await response.json();
      if (data.success) {
        button.textContent = `✓ Vote recorded!`;
        setTimeout(() => {
          button.textContent = originalText;
          button.disabled = false;
        }, 2000);
      } else {
        throw new Error("Vote was not recorded");
      }
    } catch (err) {
      console.error("Vote error:", err);
      button.textContent = "Error voting";
      button.disabled = false;
    }
  }
});
