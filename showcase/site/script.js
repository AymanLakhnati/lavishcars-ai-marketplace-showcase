const video = document.querySelector("#demo");
const buttons = [...document.querySelectorAll("[data-time]")];
const status = document.querySelector("#play-status");
let preparedVideo;
async function prepareChapterPlayback() {
  if (!/^https?:$/.test(location.protocol)) return;
  if (!preparedVideo)
    preparedVideo = (async () => {
      status.textContent = "Preparing the video for chapter navigation…";
      const response = await fetch("assets/LavishCars-Demo.mp4");
      if (!response.ok) throw new Error("Video download unavailable");
      const blob = await response.blob();
      if (!blob.size) throw new Error("Empty video response");
      const source = URL.createObjectURL(blob);
      await new Promise((resolve, reject) => {
        video.addEventListener("loadedmetadata", resolve, { once: true });
        video.addEventListener("error", reject, { once: true });
        video.src = source;
        video.load();
      });
      status.textContent = "Video ready. Chapter selected.";
    })();
  await preparedVideo;
}
for (const button of buttons) {
  button.addEventListener("click", async () => {
    try {
      await prepareChapterPlayback();
    } catch {
      status.textContent =
        "Chapter download unavailable. Use Play or the GitHub video fallback.";
    }

    if (video.readyState < 1) {
      video.load();
      await new Promise((resolve, reject) => {
        video.addEventListener("loadedmetadata", resolve, { once: true });
        video.addEventListener("error", reject, { once: true });
      }).catch(() => null);
    }
    if (video.readyState >= 1) {
      video.currentTime = Number(button.dataset.time);
      await video.play().catch(() => {
        status.textContent =
          "Chapter selected. Press Play in the video controls.";
      });
      video.scrollIntoView({
        behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches
          ? "auto"
          : "smooth",
        block: "center",
      });
    } else {
      status.textContent =
        "The video could not load. Use the download or transcript link.";
    }
  });
}
video.addEventListener("timeupdate", () => {
  let current = buttons[0];
  for (const button of buttons)
    if (Number(button.dataset.time) <= video.currentTime) current = button;
  for (const button of buttons) {
    button.classList.toggle("active", button === current);
    if (button === current) button.setAttribute("aria-current", "true");
    else button.removeAttribute("aria-current");
  }
});

const views = {
  marketplace: [
    "Discovery with a sense of occasion.",
    "Destination and category discovery, detailed filters, rental-period prices, vehicle details, photos and structured supplier inquiries.",
  ],
  supplier: [
    "Your fleet. One workspace.",
    "Listing overview and lifecycle, specifications, pricing, photo ordering, supplier profile, team roles, service areas, inquiry management and scoped insights.",
  ],
  admin: [
    "A higher standard, built in.",
    "Supplier approval and suspension, listing moderation, rejection reasons, visibility controls, catalog taxonomy, hierarchical locations and audit history.",
  ],
  concierge: [
    "Describe the trip. Discover the drive.",
    "Supported trip language becomes catalog constraints. Up to three eligible offers carry stored prices and explanations; missing destination details can be clarified.",
  ],
};
const tabs = [...document.querySelectorAll("[data-view]")];
function selectView(button) {
  const name = button.dataset.view;
  for (const tab of tabs) {
    tab.setAttribute("aria-selected", String(tab === button));
    tab.tabIndex = tab === button ? 0 : -1;
  }
  document
    .querySelector("#product-panel")
    .setAttribute("aria-labelledby", button.id);
  document.querySelector("#product-image").src = `assets/${name}.png`;
  document.querySelector("#product-image").alt =
    `Verified ${name} prototype capture`;
  document.querySelector("#product-full").href = `assets/${name}.png`;
  document.querySelector("#product-title").textContent = views[name][0];
  document.querySelector("#product-copy").textContent = views[name][1];
  document.querySelector(".capture-window").scrollTop = 0;
}
for (const tab of tabs) {
  tab.addEventListener("click", () => selectView(tab));
  tab.addEventListener("keydown", (event) => {
    let target;
    const index = tabs.indexOf(tab);
    if (event.key === "ArrowRight") target = tabs[(index + 1) % tabs.length];
    if (event.key === "ArrowLeft")
      target = tabs[(index + tabs.length - 1) % tabs.length];
    if (event.key === "Home") target = tabs[0];
    if (event.key === "End") target = tabs.at(-1);
    if (target) {
      event.preventDefault();
      selectView(target);
      target.focus();
    }
  });
}
