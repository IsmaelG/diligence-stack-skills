/* onbrand — brand token extractor.
 *
 * Paste into a browser JavaScript tool (claude-in-chrome javascript_tool, or
 * Claude_Browser javascript_tool) with the target's homepage open. Save the
 * returned JSON as tokens.json, then run make_theme.py on it.
 *
 * Returns, in descending order of trustworthiness:
 *   vars   - CSS custom properties declared on :root/html/body. If present these
 *            ARE the brand, named by the company's own designer.
 *   bg     - background colours weighted by painted area (what they actually use)
 *   fg     - text colours weighted by characters rendered
 *   fonts  - font-family + weight weighted by characters rendered
 *   type   - the heading ladder: family, size, weight, case and tracking per level.
 *            This is what makes a rebrand look like the brand rather than merely
 *            share its colours — capture it, don't skip it.
 *   assets - logo / image URLs, for reference only
 *
 * Scroll the page once before running: lazy sections are not painted until seen.
 */
(() => {
  const norm = (c) => {
    if (!c || c === "none" || c === "transparent") return null;
    const m = c.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
    if (!m) return null;
    if (m[4] !== undefined && parseFloat(m[4]) < 0.05) return null;
    return (
      "#" +
      [m[1], m[2], m[3]].map((x) => (+x).toString(16).padStart(2, "0")).join("").toUpperCase()
    );
  };

  const bg = {}, fg = {}, fonts = {};
  document.querySelectorAll("body *").forEach((el) => {
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) return;
    const s = getComputedStyle(el);
    const b = norm(s.backgroundColor);
    if (b) bg[b] = (bg[b] || 0) + Math.round(r.width * r.height);
    const t = (el.textContent || "").trim();
    if (t.length && el.children.length === 0) {
      const f = norm(s.color);
      if (f) fg[f] = (fg[f] || 0) + t.length;
      const k = s.fontFamily + " | " + s.fontWeight;
      fonts[k] = (fonts[k] || 0) + t.length;
    }
  });

  const vars = {};
  for (const sheet of document.styleSheets) {
    try {
      for (const rule of sheet.cssRules) {
        if (rule.style && rule.selectorText && /:root|^html|^body/.test(rule.selectorText)) {
          for (const p of rule.style) {
            if (p.startsWith("--")) vars[p] = rule.style.getPropertyValue(p).trim();
          }
        }
      }
    } catch (e) {
      /* cross-origin stylesheet */
    }
  }

  // The heading ladder. Largest rendered heading wins the "display" role.
  const type = [];
  document.querySelectorAll("h1,h2,h3,h4,h5,h6").forEach((el) => {
    const t = (el.innerText || "").trim();
    if (!t) return;
    const s = getComputedStyle(el);
    const px = parseFloat(s.fontSize) || 0;
    const ls = parseFloat(s.letterSpacing);
    const lh = parseFloat(s.lineHeight);
    type.push({
      tag: el.tagName,
      family: s.fontFamily.split(",")[0].replace(/["']/g, "").trim(),
      px,
      weight: s.fontWeight,
      transform: s.textTransform,
      tracking: isNaN(ls) ? 0 : +(ls / px).toFixed(4),   // em
      leading: isNaN(lh) || !px ? null : +(lh / px).toFixed(2),
      color: norm(s.color),
    });
  });
  type.sort((a, b) => b.px - a.px);

  const top = (o, n) => Object.entries(o).sort((a, b) => b[1] - a[1]).slice(0, n);
  const assets = [...document.querySelectorAll("img")]
    .map((e) => e.currentSrc || e.src)
    .filter((u) => u && /logo|brand|mark/i.test(u))
    .slice(0, 10);

  return JSON.stringify(
    {
      site: location.origin,
      title: document.title,
      vars,
      bg: top(bg, 16),
      fg: top(fg, 12),
      fonts: top(fonts, 8),
      type: type.slice(0, 12),
      assets,
    },
    null,
    1
  );
})();
