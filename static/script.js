const form = document.getElementById("search-form");
const queryInput = document.getElementById("query");
const sourceSelect = document.getElementById("source");
const grid = document.getElementById("grid");
const status = document.getElementById("status");
const toast = document.getElementById("toast");

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 1600);
}

function copyToClipboard(text) {
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(text).then(() => showToast("Image URL copied"));
  } else {
    const tmp = document.createElement("textarea");
    tmp.value = text;
    document.body.appendChild(tmp);
    tmp.select();
    document.execCommand("copy");
    document.body.removeChild(tmp);
    showToast("Image URL copied");
  }
}

function renderResults(results) {
  grid.innerHTML = "";
  results.forEach((item) => {
    if (!item.url) return;
    const card = document.createElement("div");
    card.className = "img-card";

    const img = document.createElement("img");
    img.src = item.thumbnail || item.url;
    img.loading = "lazy";
    img.alt = item.title || "";

    const overlay = document.createElement("div");
    overlay.className = "overlay";
    overlay.textContent = "Click to copy URL";

    const tag = document.createElement("span");
    tag.className = "tag";
    tag.textContent = item.source;

    card.appendChild(img);
    card.appendChild(overlay);
    card.appendChild(tag);

    card.addEventListener("click", () => copyToClipboard(item.url));

    grid.appendChild(card);
  });
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const query = queryInput.value.trim();
  const source = sourceSelect.value;
  if (!query) return;

  status.textContent = "Searching...";
  grid.innerHTML = "";

  try {
    const res = await fetch("/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, source }),
    });
    const data = await res.json();

    if (!res.ok) {
      status.textContent = data.error || "Something went wrong";
      return;
    }

    status.textContent = `${data.count} results for "${data.query}"`;
    renderResults(data.results);
  } catch (err) {
    status.textContent = "Search failed. Check the server console.";
  }
});
