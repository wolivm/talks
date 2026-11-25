// Present mode: one slide or film at a time. Arrows, space, swipe; Esc closes. Films play when they come up.
(() => {
  const stage = document.getElementById("stage"), frame = document.getElementById("frame"), count = document.getElementById("count");
  let i = 0, startX = null;
  function show(n) {
    i = Math.max(0, Math.min(ITEMS.length - 1, n));
    const it = ITEMS[i];
    frame.replaceChildren();
    if (it.type === "img") {
      const img = new Image(); img.src = it.src; img.alt = "Slide " + (i + 1); frame.append(img);
    } else {
      const v = document.createElement("video");
      v.src = it.src; v.poster = it.poster; v.controls = true; v.playsInline = true; v.loop = !!it.loop;
      frame.append(v); v.play().catch(() => {});
    }
    count.textContent = (i + 1) + " / " + ITEMS.length;
    // keep the next slide warm
    const nx = ITEMS[i + 1]; if (nx && nx.type === "img") { const p = new Image(); p.src = nx.src; }
  }
  function open(n) {
    document.querySelectorAll(".deck video").forEach(v => v.pause());
    stage.hidden = false; show(n);
    if (stage.requestFullscreen) stage.requestFullscreen().catch(() => {});
  }
  function close() {
    stage.hidden = true; frame.replaceChildren();
    if (document.fullscreenElement) document.exitFullscreen().catch(() => {});
    const el = document.getElementById("s" + (i + 1)); if (el) el.scrollIntoView({ block: "center" });
  }
  document.getElementById("present").addEventListener("click", () => open(0));
  document.querySelectorAll(".deck .slide img").forEach(img => img.addEventListener("click", () => open(+img.closest(".slide").id.slice(1) - 1)));
  document.getElementById("prev").addEventListener("click", () => show(i - 1));
  document.getElementById("next").addEventListener("click", () => show(i + 1));
  document.getElementById("close").addEventListener("click", close);
  document.addEventListener("keydown", e => {
    if (stage.hidden) return;
    if (["ArrowRight", "PageDown", " "].includes(e.key)) { e.preventDefault(); show(i + 1); }
    else if (["ArrowLeft", "PageUp"].includes(e.key)) { e.preventDefault(); show(i - 1); }
    else if (e.key === "Escape") close();
  });
  document.addEventListener("fullscreenchange", () => { if (!document.fullscreenElement && !stage.hidden) close(); });
  frame.addEventListener("touchstart", e => { startX = e.touches[0].clientX; }, { passive: true });
  frame.addEventListener("touchend", e => {
    if (startX === null) return; const dx = e.changedTouches[0].clientX - startX; startX = null;
    if (Math.abs(dx) > 50) show(i + (dx < 0 ? 1 : -1));
  });
})();
