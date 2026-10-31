"use strict";

const state = {
  latestMemory: null,
  latestMemoryId: null,
};

const API_BASE = "";

const memoryInput = document.querySelector("#memoryInput");
const compressionLevel = document.querySelector("#compressionLevel");
const compressionLabel = document.querySelector("#compressionLabel");
const compressButton = document.querySelector("#compressButton");
const clearInput = document.querySelector("#clearInput");
const loadSample = document.querySelector("#loadSample");

const outputContent = document.querySelector("#outputContent");
const verifyButton = document.querySelector("#verifyButton");
const copyButton = document.querySelector("#copyButton");

const inputTokens = document.querySelector("#inputTokens");
const characterCount = document.querySelector("#characterCount");
const verificationBadge = document.querySelector("#verificationBadge");
const memoryStatusMetric = document.querySelector("#memoryStatusMetric");

const importanceScore = document.querySelector("#importanceScore");
const confidenceScore = document.querySelector("#confidenceScore");

const originalTokensMetric =
  document.querySelector("#originalTokensMetric");

const compressedTokensMetric =
  document.querySelector("#compressedTokensMetric");

const tokensSavedMetric =
  document.querySelector("#tokensSavedMetric");

const savingsMetric =
  document.querySelector("#savingsMetric");

const heroSavings = document.querySelector("#heroSavings");
const heroProgress = document.querySelector("#heroProgress");
const heroTokenCount = document.querySelector("#heroTokenCount");

const queryInput = document.querySelector("#queryInput");
const tokenBudget = document.querySelector("#tokenBudget");
const queryButton = document.querySelector("#queryButton");
const queryResult = document.querySelector("#queryResult");

const demoText = `
I am building MemoSift for the Hyderabad Hacktoberfest Hack Day. It compresses long conversations into searchable memories so AI applications use fewer tokens. The project uses FastAPI and Gemma, supports token-budget retrieval, and verifies memory integrity with hashes. The goal is to preserve important facts while reducing context size.
`.trim();

function exists(element) {
  return element !== null;
}

function updateCompressionLabel() {
  if (!exists(compressionLevel) || !exists(compressionLabel)) {
    return;
  }

  const labels = [
    "Preserve detail",
    "Balanced",
    "Save more tokens",
  ];

  const selectedIndex = Number(compressionLevel.value);

  compressionLabel.textContent =
    labels[selectedIndex] || "Balanced";
}

function estimateTokens(text) {
  if (!text || !text.trim()) {
    return 0;
  }

  return Math.max(1, Math.ceil(text.trim().length / 4));
}

function updateInputStats() {
  if (!exists(memoryInput)) {
    return;
  }

  const text = memoryInput.value;

  if (exists(inputTokens)) {
    inputTokens.textContent = estimateTokens(text);
  }

  if (exists(characterCount)) {
    characterCount.textContent = `${text.length} characters`;
  }
}

function setLoading(button, loadingText, normalText) {
  if (!exists(button)) {
    return () => {};
  }

  button.disabled = true;
  button.textContent = loadingText;

  return () => {
    button.disabled = false;
    button.textContent = normalText;
  };
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function showError(message) {
  if (!exists(outputContent)) {
    return;
  }

  outputContent.innerHTML = `
    <div class="empty-state">
      <div class="empty-icon">!</div>
      <h3>Something went wrong</h3>
      <p>${escapeHtml(message)}</p>
    </div>
  `;
}

function resetVerificationState() {
  if (exists(verificationBadge)) {
    verificationBadge.textContent = "Not verified";
    verificationBadge.classList.add("pending");
  }

  if (exists(memoryStatusMetric)) {
    memoryStatusMetric.textContent = "Waiting";
  }
}

function resetOutputState() {
  if (exists(outputContent)) {
    outputContent.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">M</div>
        <h3>Your compressed memory will appear here</h3>
        <p>
          Add some context on the left to extract useful facts
          and reduce token usage.
        </p>
      </div>
    `;
  }

  if (exists(verifyButton)) {
    verifyButton.disabled = true;
  }

  if (exists(copyButton)) {
    copyButton.disabled = true;
  }

  if (exists(importanceScore)) {
    importanceScore.textContent = "0%";
  }

  if (exists(confidenceScore)) {
    confidenceScore.textContent = "0%";
  }

  resetVerificationState();
}

function renderMemory(memory) {
  if (!exists(outputContent)) {
    return;
  }

  const facts = Array.isArray(memory?.facts)
    ? memory.facts
    : [];

  if (exists(importanceScore)) {
    importanceScore.textContent =
      `${memory?.importance_score ?? 0}%`;
  }

  if (exists(confidenceScore)) {
    confidenceScore.textContent =
      `${memory?.confidence ?? 0}%`;
  }

  const factsMarkup = facts.length > 0
    ? `
      <div class="memory-facts">
        ${facts
          .map(
            (fact) => `
              <div class="memory-fact">
                ${escapeHtml(fact)}
              </div>
            `,
          )
          .join("")}
      </div>
    `
    : "";

  outputContent.innerHTML = `
    <div class="memory-result">
      ${escapeHtml(memory?.compressed_text || "")}
    </div>
    ${factsMarkup}
  `;

  if (exists(verifyButton)) {
    verifyButton.disabled = false;
  }

  if (exists(copyButton)) {
    copyButton.disabled = false;
  }

  if (exists(verificationBadge)) {
    verificationBadge.textContent = "Ready to verify";
    verificationBadge.classList.add("pending");
  }

  if (exists(memoryStatusMetric)) {
    memoryStatusMetric.textContent = "Unverified";
  }
}

function updateMetrics(stats = {}) {
  const originalTokens = Number(stats.original_tokens || 0);
  const compressedTokens = Number(stats.compressed_tokens || 0);
  const tokensSaved = Number(stats.tokens_saved || 0);
  const savingsPercent = Number(stats.savings_percent || 0);

  if (exists(originalTokensMetric)) {
    originalTokensMetric.textContent = originalTokens;
  }

  if (exists(compressedTokensMetric)) {
    compressedTokensMetric.textContent = compressedTokens;
  }

  if (exists(tokensSavedMetric)) {
    tokensSavedMetric.textContent = tokensSaved;
  }

  if (exists(savingsMetric)) {
    savingsMetric.textContent =
      `${savingsPercent}% reduction`;
  }

  if (exists(heroSavings)) {
    heroSavings.textContent =
      `${savingsPercent}%`;
  }

  if (exists(heroProgress)) {
    heroProgress.style.width =
      `${Math.min(Math.max(savingsPercent, 0), 100)}%`;
  }

  if (exists(heroTokenCount)) {
    heroTokenCount.textContent = tokensSaved;
  }
}

async function parseResponse(response) {
  const contentType =
    response.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    return response.json();
  }

  const text = await response.text();

  return {
    detail: text || "The server returned an unexpected response.",
  };
}

async function compressMemory() {
  if (!exists(memoryInput)) {
    return;
  }

  const text = memoryInput.value.trim();

  if (!text) {
    showError("Please enter a memory or conversation first.");
    return;
  }

  const restoreButton = setLoading(
    compressButton,
    "Compressing...",
    "Compress memory",
  );

  try {
    const levelMap = [
      "preserve",
      "balanced",
      "aggressive",
    ];

    const selectedLevel = Number(
      compressionLevel?.value ?? 1,
    );

    const response = await fetch(
      `${API_BASE}/api/memories`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text,
          compression_level:
            levelMap[selectedLevel] || "balanced",
        }),
      },
    );

    const data = await parseResponse(response);

    if (!response.ok) {
      throw new Error(
        data.detail || "Compression failed.",
      );
    }

    if (!data.memory) {
      throw new Error(
        "The server did not return a memory object.",
      );
    }

    state.latestMemory = data.memory;
    state.latestMemoryId = data.memory.id || null;

    renderMemory(data.memory);
    updateMetrics(data.stats || {});
  } catch (error) {
    showError(
      error.message || "Unable to compress memory.",
    );
  } finally {
    restoreButton();
  }
}

async function verifyMemory() {
  if (!state.latestMemoryId) {
    return;
  }

  if (!exists(verifyButton)) {
    return;
  }

  const originalText = verifyButton.textContent;

  verifyButton.disabled = true;
  verifyButton.textContent = "Verifying...";

  try {
    const response = await fetch(
      `${API_BASE}/api/verify/${encodeURIComponent(
        state.latestMemoryId,
      )}`,
      {
        method: "POST",
      },
    );

    const data = await parseResponse(response);

    if (!response.ok) {
      throw new Error(
        data.detail || "Verification failed.",
      );
    }

    if (data.verified) {
      if (exists(verificationBadge)) {
        verificationBadge.textContent = "Verified";
        verificationBadge.classList.remove("pending");
      }

      if (exists(memoryStatusMetric)) {
        memoryStatusMetric.textContent = "Verified";
      }
    } else {
      if (exists(verificationBadge)) {
        verificationBadge.textContent = "Modified";
        verificationBadge.classList.add("pending");
      }

      if (exists(memoryStatusMetric)) {
        memoryStatusMetric.textContent = "Modified";
      }
    }
  } catch (error) {
    if (exists(verificationBadge)) {
      verificationBadge.textContent =
        "Verification error";
      verificationBadge.classList.add("pending");
    }

    if (exists(memoryStatusMetric)) {
      memoryStatusMetric.textContent = "Error";
    }

    console.error("Verification error:", error);
  } finally {
    verifyButton.disabled = false;
    verifyButton.textContent = originalText;
  }
}

async function copyMemory() {
  if (!state.latestMemory) {
    return;
  }

  const text =
    state.latestMemory.compressed_text || "";

  try {
    await navigator.clipboard.writeText(text);

    if (!exists(copyButton)) {
      return;
    }

    const originalText = copyButton.textContent;
    copyButton.textContent = "Copied";

    setTimeout(() => {
      copyButton.textContent = originalText;
    }, 1400);
  } catch (error) {
    console.error("Copy failed:", error);

    if (exists(copyButton)) {
      copyButton.textContent = "Copy failed";

      setTimeout(() => {
        copyButton.textContent = "Copy result";
      }, 1400);
    }
  }
}

async function searchMemory() {
  if (!exists(queryInput) || !exists(queryResult)) {
    return;
  }

  const query = queryInput.value.trim();

  if (!query) {
    queryResult.textContent =
      "Enter a question to search your memory.";
    return;
  }

  const originalText = queryButton?.textContent;

  if (exists(queryButton)) {
    queryButton.disabled = true;
    queryButton.textContent = "Searching...";
  }

  queryResult.innerHTML = `
    <div class="query-loading">
      Searching relevant memories...
    </div>
  `;

  try {
    const requestedBudget = Number(
      tokenBudget?.value || 500,
    );

    const response = await fetch(
      `${API_BASE}/api/query`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query,
          token_budget:
            Number.isFinite(requestedBudget) &&
            requestedBudget > 0
              ? requestedBudget
              : 500,
        }),
      },
    );

    const data = await parseResponse(response);

    if (!response.ok) {
      throw new Error(
        data.detail || "Search failed.",
      );
    }

    const memories = Array.isArray(data.memories)
      ? data.memories
      : [];

    if (!memories.length) {
      queryResult.textContent =
        "No relevant memories found.";
      return;
    }

    const resultMarkup = memories
      .map((memory, index) => {
        const summary =
          memory.summary ||
          memory.compressed_text ||
          "No summary available.";

        const topics = Array.isArray(memory.topics)
          ? memory.topics
          : [];

        const importance =
          memory.importance_score ?? 0;

        return `
          <article class="query-memory-card">
            <div class="query-memory-header">
              <span class="query-memory-index">
                Memory ${index + 1}
              </span>

              <span class="query-memory-score">
                Importance ${escapeHtml(importance)}%
              </span>
            </div>

            <p class="query-memory-summary">
              ${escapeHtml(summary)}
            </p>

            ${
              topics.length
                ? `
                  <div class="query-memory-topics">
                    ${topics
                      .map(
                        (topic) => `
                          <span>
                            ${escapeHtml(topic)}
                          </span>
                        `,
                      )
                      .join("")}
                  </div>
                `
                : ""
            }
          </article>
        `;
      })
      .join("");

    queryResult.innerHTML = `
      <div class="query-result-header">
        <strong>
          ${memories.length} relevant memory item(s)
        </strong>

        <span>
          ${data.tokens_used || 0} tokens used
          of ${data.token_budget || requestedBudget}
        </span>
      </div>

      <div class="query-memory-list">
        ${resultMarkup}
      </div>
    `;
  } catch (error) {
    queryResult.textContent =
      error.message || "Search failed.";
  } finally {
    if (exists(queryButton)) {
      queryButton.disabled = false;
      queryButton.textContent =
        originalText || "Search memory";
    }
  }
}


function clearMemoryInput() {
  if (!exists(memoryInput)) {
    return;
  }

  memoryInput.value = "";
  updateInputStats();
  resetOutputState();
}

function registerEventListeners() {
  if (exists(memoryInput)) {
    memoryInput.addEventListener(
      "input",
      updateInputStats,
    );
  }

  if (exists(compressionLevel)) {
    compressionLevel.addEventListener(
      "input",
      updateCompressionLabel,
    );
  }

  if (exists(compressButton)) {
    compressButton.addEventListener(
      "click",
      compressMemory,
    );
  }

  if (exists(verifyButton)) {
    verifyButton.addEventListener(
      "click",
      verifyMemory,
    );
  }

  if (exists(copyButton)) {
    copyButton.addEventListener(
      "click",
      copyMemory,
    );
  }

  if (exists(queryButton)) {
    queryButton.addEventListener(
      "click",
      searchMemory,
    );
  }

  if (exists(clearInput)) {
    clearInput.addEventListener(
      "click",
      clearMemoryInput,
    );
  }

  if (exists(loadSample)) {
    loadSample.addEventListener(
      "click",
      loadDemoText,
    );
  }

  if (exists(queryInput)) {
    queryInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        searchMemory();
      }
    });
  }
}

function initializeApp() {
  registerEventListeners();
  updateCompressionLabel();
  updateInputStats();
  resetOutputState();
}

initializeApp();
