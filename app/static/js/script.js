const menuIcon = document.getElementById("menuIcon");
const navLinks = document.getElementById("navLinks");

if (menuIcon && navLinks) {
    menuIcon.addEventListener("click", () => {
        navLinks.classList.toggle("active");
    });
}

const themeToggle = document.getElementById("themeToggle");
const themeIcon = themeToggle ? themeToggle.querySelector("i") : null;

function updateThemeToggle(theme) {
    if (!themeToggle || !themeIcon) return;

    const isDark = theme === "dark";
    themeToggle.setAttribute("aria-label", isDark ? "Switch to light mode" : "Switch to dark mode");
    themeIcon.className = isDark ? "fa-solid fa-sun" : "fa-solid fa-moon";
}

const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
updateThemeToggle(currentTheme);

if (themeToggle) {
    themeToggle.addEventListener("click", () => {
        const nextTheme = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";

        if (nextTheme === "dark") {
            document.documentElement.setAttribute("data-theme", "dark");
        } else {
            document.documentElement.removeAttribute("data-theme");
        }

        localStorage.setItem("theme", nextTheme);
        updateThemeToggle(nextTheme);
    });
}
