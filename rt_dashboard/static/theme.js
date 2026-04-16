// ─── theme.js ─────────────────────────────────────────────────────────────────
//  Material You / TailwindCSS CSS-variable bridge
//  Generates --tw-* custom properties for light, dark, and mid themes.
//  Usage: import { injectStyles, setTheme, getTheme, onThemeChange } from './theme.js'
// ─────────────────────────────────────────────────────────────────────────────

// ══════════════════════════════════════════════════════════════════════════════
//  LIGHT THEME
// ══════════════════════════════════════════════════════════════════════════════

const lightThemeArgs = {
    // Background & Surface
    "background":                  "#ece3df",
    "surface":                     "#ece3df",
    "surface-dim":                 "#ded8d7",
    "surface-bright":              "#ffffff",
    "surface-variant":             "#f4f1f8",
    "surface-container-lowest":    "#ffffff",
    "surface-container-low":       "#fdf7ff",
    "surface-container":           "#f3eeed",
    "surface-container-high":      "#f7f2f1",
    "surface-container-highest":   "#e6e1e5",
    "surface-tint":                "#4e5f80",
    "inverse-surface":             "#1b162e",
    "inverse-on-surface":          "#eae1ff",

    // On-Surface & Outlines
    "on-background":               "#433f4e",
    "on-surface":                  "#433f4e",
    "on-surface-variant":          "#6b6562",
    "outline":                     "#796f9a",
    "outline-variant":             "#c9c5d0",

    // Primary
    "primary":                     "#4e5f80",
    "primary-dim":                 "#4e5f80",
    "primary-fixed":               "#d7e2ff",
    "primary-fixed-dim":           "#c3d5fb",
    "primary-container":           "#d7e2ff",
    "on-primary":                  "#ffffff",
    "on-primary-container":        "#001a41",
    "on-primary-fixed":            "#2e3f5f",
    "on-primary-fixed-variant":    "#4b5c7c",
    "inverse-primary":             "#b5c7ed",

    // Secondary
    "secondary":                   "#575a6f",
    "secondary-dim":               "#575a6f",
    "secondary-fixed":             "#dfe1fa",
    "secondary-fixed-dim":         "#d1d3ec",
    "secondary-container":         "#e0e2ec",
    "on-secondary":                "#ffffff",
    "on-secondary-container":      "#1c1f31",
    "on-secondary-fixed":          "#3b3e52",
    "on-secondary-fixed-variant":  "#575a6f",

    // Tertiary
    "tertiary":                    "#645e5b",
    "tertiary-dim":                "#f2e9e5",
    "tertiary-fixed":              "#fbf2ee",
    "tertiary-fixed-dim":          "#ede3df",
    "tertiary-container":          "#f2e9e5",
    "on-tertiary":                 "#ffffff",
    "on-tertiary-container":       "#5b5653",
    "on-tertiary-fixed":           "#4e4946",
    "on-tertiary-fixed-variant":   "#6b6562",

    // Error
    "error":                       "#b3261e",
    "error-dim":                   "#bb5551",
    "error-container":             "#f9dedc",
    "on-error":                    "#ffffff",
    "on-error-container":          "#410002",
};


// ══════════════════════════════════════════════════════════════════════════════
//  DARK THEME
// ══════════════════════════════════════════════════════════════════════════════

const darkThemeArgs = {
    // Background & Surface
    "background":                  "#0f0c19",
    "surface":                     "#0f0c19",
    "surface-dim":                 "#0f0c19",
    "surface-bright":              "#2f2551",
    "surface-variant":             "#282045",
    "surface-container-lowest":    "#000000",
    "surface-container-low":       "#151123",
    "surface-container":           "#1b162e",
    "surface-container-high":      "#221b39",
    "surface-container-highest":   "#282045",
    "surface-tint":                "#b5c7ed",
    "inverse-surface":             "#fdf7ff",
    "inverse-on-surface":          "#575362",

    // On-Surface & Outlines
    "on-background":               "#eae1ff",
    "on-surface":                  "#eae1ff",
    "on-surface-variant":          "#b0a5d2",
    "outline":                     "#796f9a",
    "outline-variant":             "#4b426a",

    // Primary
    "primary":                     "#b5c7ed",
    "primary-dim":                 "#a8b9de",
    "primary-fixed":               "#d7e2ff",
    "primary-fixed-dim":           "#c3d5fb",
    "primary-container":           "#364766",
    "on-primary":                  "#2f405f",
    "on-primary-container":        "#bfd0f7",
    "on-primary-fixed":            "#2e3f5f",
    "on-primary-fixed-variant":    "#4b5c7c",
    "inverse-primary":             "#4e5f80",

    // Secondary
    "secondary":                   "#9a9cb4",
    "secondary-dim":               "#9a9cb4",
    "secondary-fixed":             "#dfe1fa",
    "secondary-fixed-dim":         "#d1d3ec",
    "secondary-container":         "#373a4e",
    "on-secondary":                "#1c1f31",
    "on-secondary-container":      "#bbbed6",
    "on-secondary-fixed":          "#3b3e52",
    "on-secondary-fixed-variant":  "#575a6f",

    // Tertiary
    "tertiary":                    "#fff8f5",
    "tertiary-dim":                "#f2e9e5",
    "tertiary-fixed":              "#fbf2ee",
    "tertiary-fixed-dim":          "#ede3df",
    "tertiary-container":          "#f2e9e5",
    "on-tertiary":                 "#645e5b",
    "on-tertiary-container":       "#5b5653",
    "on-tertiary-fixed":           "#4e4946",
    "on-tertiary-fixed-variant":   "#6b6562",

    // Error
    "error":                       "#ee7d77",
    "error-dim":                   "#bb5551",
    "error-container":             "#7f2927",
    "on-error":                    "#490106",
    "on-error-container":          "#ff9993",
};


// ══════════════════════════════════════════════════════════════════════════════
//  MID THEME  — Deep violet dusk; halfway between light and dark
// ══════════════════════════════════════════════════════════════════════════════

const midThemeArgs = {
    // Background & Surface
    "background":                  "#1e1a2e",
    "surface":                     "#1e1a2e",
    "surface-dim":                 "#16132a",
    "surface-bright":              "#2e2850",
    "surface-variant":             "#2a2440",
    "surface-container-lowest":    "#0a0814",
    "surface-container-low":       "#1b1830",
    "surface-container":           "#22203a",
    "surface-container-high":      "#282444",
    "surface-container-highest":   "#302c52",
    "surface-tint":                "#b5c7ed",
    "inverse-surface":             "#eae1ff",
    "inverse-on-surface":          "#433f4e",

    // On-Surface & Outlines
    "on-background":               "#d4ccf5",
    "on-surface":                  "#d4ccf5",
    "on-surface-variant":          "#9990bb",
    "outline":                     "#796f9a",
    "outline-variant":             "#4b426a",

    // Primary
    "primary":                     "#c3d5fb",
    "primary-dim":                 "#a8b9de",
    "primary-fixed":               "#d7e2ff",
    "primary-fixed-dim":           "#c3d5fb",
    "primary-container":           "#2e3f5f",
    "on-primary":                  "#1a2a48",
    "on-primary-container":        "#c3d5fb",
    "on-primary-fixed":            "#2e3f5f",
    "on-primary-fixed-variant":    "#4b5c7c",
    "inverse-primary":             "#4e5f80",

    // Secondary
    "secondary":                   "#b0b2cc",
    "secondary-dim":               "#9a9cb4",
    "secondary-fixed":             "#dfe1fa",
    "secondary-fixed-dim":         "#d1d3ec",
    "secondary-container":         "#2c2e44",
    "on-secondary":                "#1c1f31",
    "on-secondary-container":      "#c8cadf",
    "on-secondary-fixed":          "#3b3e52",
    "on-secondary-fixed-variant":  "#575a6f",

    // Tertiary
    "tertiary":                    "#e8ddd9",
    "tertiary-dim":                "#c8bfbb",
    "tertiary-fixed":              "#fbf2ee",
    "tertiary-fixed-dim":          "#ede3df",
    "tertiary-container":          "#3a3330",
    "on-tertiary":                 "#2a2420",
    "on-tertiary-container":       "#c8bfbb",
    "on-tertiary-fixed":           "#4e4946",
    "on-tertiary-fixed-variant":   "#6b6562",

    // Error
    "error":                       "#ee7d77",
    "error-dim":                   "#bb5551",
    "error-container":             "#5c1f1d",
    "on-error":                    "#360004",
    "on-error-container":          "#ff9993",
};


// ══════════════════════════════════════════════════════════════════════════════
//  THEME REGISTRY
// ══════════════════════════════════════════════════════════════════════════════

const THEMES = {
    light: lightThemeArgs,
    dark:  darkThemeArgs,
    mid:   midThemeArgs,
};

const THEME_CLASSES = {
    light: [],           // :root defaults to light
    dark:  ["dark"],
    mid:   ["mid"],
};

/** @type {'light' | 'dark' | 'mid'} */
let _activeTheme = "dark";

/** @type {Array<(theme: string) => void>} */
const _listeners = [];

let _styleEl = null;


// ══════════════════════════════════════════════════════════════════════════════
//  HELPERS
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Serialize a token map into CSS custom property declarations.
 * @param {Record<string, string>} tokens
 * @param {string} [prefix="tw"]
 * @returns {string}
 */
function serializeVars(tokens, prefix = "tw") {
    return Object.entries(tokens)
        .map(([k, v]) => `  --${prefix}-${k}: ${v};`)
        .join("\n");
}

/**
 * Build the full <style> content from all registered themes.
 * @returns {string}
 */
function buildStylesheet() {
    const light = serializeVars(lightThemeArgs);
    const dark   = serializeVars(darkThemeArgs);
    const mid    = serializeVars(midThemeArgs);

    return `
:root {
${light}
}

.dark {
${dark}
}

.mid {
${mid}
}

/* Smooth palette crossfade on theme switch */
*, *::before, *::after {
  transition:
    background-color 160ms ease,
    border-color     160ms ease,
    color            120ms ease;
}
    `.trim();
}


// ══════════════════════════════════════════════════════════════════════════════
//  PUBLIC API
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Inject (or re-inject) the theme stylesheet into <head>.
 * Safe to call multiple times — replaces the existing <style> element.
 */
function injectStyles() {
    if (!_styleEl) {
        _styleEl = document.createElement("style");
        _styleEl.id = "tw-theme-vars";
        document.head.appendChild(_styleEl);
    }
    _styleEl.textContent = buildStylesheet();
}

/**
 * Switch the active theme.
 * @param {'light' | 'dark' | 'mid'} theme
 */
function setTheme(theme) {
    if (!(theme in THEMES)) {
        console.warn(`[theme] Unknown theme "${theme}". Valid options: ${Object.keys(THEMES).join(", ")}.`);
        return;
    }

    const root = document.documentElement;

    // Remove all known theme classes, then apply the new one
    Object.values(THEME_CLASSES).flat().forEach(cls => root.classList.remove(cls));
    THEME_CLASSES[theme].forEach(cls => root.classList.add(cls));

    _activeTheme = theme;

    // Persist preference
    try { localStorage.setItem("theme", theme); } catch (_) {}

    _listeners.forEach(fn => fn(theme));
}

/** @returns {'light' | 'dark' | 'mid'} */
function getTheme() {
    return _activeTheme;
}

/**
 * Register a callback that fires whenever the theme changes.
 * @param {(theme: string) => void} fn
 * @returns {() => void}  Unsubscribe function
 */
function onThemeChange(fn) {
    _listeners.push(fn);
    return () => {
        const i = _listeners.indexOf(fn);
        if (i !== -1) _listeners.splice(i, 1);
    };
}

/**
 * Toggle between light ↔ dark (ignores mid).
 * Useful for a simple toggle button.
 */
function toggleTheme() {
    setTheme(_activeTheme === "dark" ? "light" : "dark");
}

/**
 * Read a single resolved CSS variable from the current theme.
 * @param {string} token  e.g. "primary" or "on-surface"
 * @returns {string}
 */
function getToken(token) {
    return getComputedStyle(document.documentElement)
        .getPropertyValue(`--tw-${token}`)
        .trim();
}

/**
 * Auto-detect preference from:
 *   1. localStorage  (user's last explicit choice)
 *   2. prefers-color-scheme media query
 *   3. Falls back to "dark"
 */
function detectAndApplyTheme() {
    let saved;
    try { saved = localStorage.getItem("theme"); } catch (_) {}

    if (saved && saved in THEMES) {
        setTheme(saved);
        return;
    }

    const prefersDark = window.matchMedia?.("(prefers-color-scheme: dark)").matches;
    setTheme(prefersDark ? "dark" : "light");
}

/**
 * Watch the OS color scheme and switch automatically
 * (only when the user hasn't made an explicit choice).
 */
function watchSystemTheme() {
    const mq = window.matchMedia?.("(prefers-color-scheme: dark)");
    if (!mq) return;

    mq.addEventListener("change", e => {
        let saved;
        try { saved = localStorage.getItem("theme"); } catch (_) {}
        if (!saved) setTheme(e.matches ? "dark" : "light");
    });
}


// ══════════════════════════════════════════════════════════════════════════════
//  AUTO-INIT
// ══════════════════════════════════════════════════════════════════════════════

injectStyles();
detectAndApplyTheme();
watchSystemTheme();


// ══════════════════════════════════════════════════════════════════════════════
//  EXPORTS  (ES module — remove if using as a plain script tag)
// ══════════════════════════════════════════════════════════════════════════════

export {
    THEMES,
    lightThemeArgs,
    darkThemeArgs,
    midThemeArgs,
    injectStyles,
    setTheme,
    getTheme,
    toggleTheme,
    onThemeChange,
    getToken,
    detectAndApplyTheme,
    watchSystemTheme,
};
