const portfolioAbout = {
  name: "Vaibhavi Saw",
  role: "Senior · Dublin High School · Dublin, California",
  intro:
    "Hi! I'm Vaibhavi Saw — a senior aspiring to study Architecture. I combine creative design with technical problem-solving to turn ideas into spaces where people live, learn, and grow.",
  goal:
    "I am applying to architecture programs to deepen my foundation in design, technology, and collaborative problem-solving — and to become an architect who shapes environments that are functional, beautiful, and inclusive.",
  highlights: [
    { "value": "Honor Roll", "label": "All years of high school" },
    { "value": "Head of Science", "label": "Girls in STEM leadership" },
    { "value": "3 languages", "label": "English · French · Hindi" },
  ],
  sections: [
    {
      title: "Why architecture",
      accent: "coral",
      items: [
        "Design and building are how I understand the world — shaped by my mom's creativity and my dad's engineering mindset.",
        "In fourth grade, built a working model house with a windmill, solar panels, and functioning lights — the moment architecture became my path.",
        "Believe art and technology work best together when spaces must be both beautiful and buildable.",
      ],
    },
    {
      title: "Design & technical skills",
      accent: "cobalt",
      items: [
        "Model and design in Autodesk Fusion 360, Revit, and Houzz Pro.",
        "Completed a compact ~440 ft² residential floor plan with blueprint, top-view plan, and interior rendering.",
        "When Houzz roof tools disrupted the model, solved it by building separate rooms and assembling step-by-step instead of restarting.",
      ],
    },
    {
      title: "Leadership & community impact",
      accent: "sage",
      items: [
        "Head of Science, Girls in STEM — lead initiatives supporting girls in science and technology.",
        "Coordinated two fundraisers for school supplies in lower-income communities.",
        "Volunteered with Tutoring Chicago (English tutoring) and Khan Academy Schoolhouse (led an art course).",
      ],
    },
    {
      title: "Academic & personal strengths",
      accent: "gold",
      items: [
        "Honor Roll throughout high school.",
        "Chess awards, 2nd place art contest, basketball trophies — focus, strategy, and resilience under pressure.",
        "Basketball and volleyball team experience — collaboration, adaptability, and supporting others.",
      ],
    },
  ],
  tags: [
    "Autodesk Fusion 360",
    "Autodesk Revit",
    "Houzz Pro",
    "Spatial design",
    "Girls in STEM",
    "Community leadership",
  ],
  contact: {
    email: "saw.naraclan2134@gmail.com",
    linkedin: "https://www.linkedin.com/in/vaibhavi-saw-469905397/",
  },
};

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function renderAbout(container) {
  const highlights = (portfolioAbout.highlights || [])
    .map(
      (item) =>
        "<div class=\"portfolio-stat\"><strong>" +
        escapeHtml(item.value) +
        "</strong><span>" +
        escapeHtml(item.label) +
        "</span></div>"
    )
    .join("");

  const sections = (portfolioAbout.sections || [])
    .map((section) => {
      const items = (section.items || [])
        .map((item) => "<li>" + escapeHtml(item) + "</li>")
        .join("");
      return (
        "<div class=\"about-me-block about-accent-" +
        escapeHtml(section.accent || "cobalt") +
        "\">" +
        "<h4>" +
        escapeHtml(section.title) +
        "</h4>" +
        "<ul>" +
        items +
        "</ul></div>"
      );
    })
    .join("");

  const tags = (portfolioAbout.tags || [])
    .map((tag) => "<span class=\"portfolio-tag\">" + escapeHtml(tag) + "</span>")
    .join("");

  container.innerHTML =
    "<div class=\"portfolio-stats sketch-box\">" +
    highlights +
    "</div>" +
    "<div class=\"about-me-grid sketch-box\">" +
    "<div class=\"about-me-photo\" aria-hidden=\"true\">VS</div>" +
    "<div class=\"about-me-copy\">" +
    "<p class=\"about-me-intro\">" +
    escapeHtml(portfolioAbout.intro) +
    "</p>" +
    "<p class=\"about-me-role\">" +
    escapeHtml(portfolioAbout.role) +
    "</p>" +
    sections +
    "<p class=\"about-me-goal\">" +
    escapeHtml(portfolioAbout.goal) +
    "</p>" +
    "<div class=\"portfolio-tags\">" +
    tags +
    "</div>" +
    "<div class=\"about-links\">" +
    "<a href=\"mailto:" +
    escapeHtml(portfolioAbout.contact.email) +
    "\">Email</a>" +
    "<a href=\"" +
    escapeHtml(portfolioAbout.contact.linkedin) +
    "\" target=\"_blank\" rel=\"noreferrer\">LinkedIn</a>" +
    "</div>" +
    "</div></div>";
}

function renderProjectImage(image, sizeClass) {
  return (
    "<figure class=\"project-image " +
    escapeHtml(sizeClass || "") +
    "\">" +
    "<p class=\"project-image-label\">" +
    escapeHtml(image.label || "") +
    "</p>" +
    "<div class=\"project-image-media\">" +
    "<img src=\"" +
    escapeHtml(image.src) +
    "\" alt=\"" +
    escapeHtml(image.alt) +
    "\" loading=\"lazy\">" +
    "</div>" +
    "<figcaption>" +
    escapeHtml(image.caption) +
    "</figcaption></figure>"
  );
}

function findProjectImage(project, labelMatch) {
  const images = project.images || [];
  const match = labelMatch.toLowerCase();
  return images.find((image) => (image.label || "").toLowerCase().includes(match));
}

function renderProjectShowcase(project) {
  const blueprint = findProjectImage(project, "blueprint");
  const topView = findProjectImage(project, "top");
  const rendering = findProjectImage(project, "render");

  const stack = [topView, rendering].filter(Boolean)
    .map((image) => renderProjectImage(image, "project-image-compact"))
    .join("");

  const primary = blueprint ? renderProjectImage(blueprint, "project-image-primary") : "";

  return (
    "<div class=\"project-showcase\">" +
    "<div class=\"project-showcase-primary\">" +
    primary +
    "</div>" +
    "<div class=\"project-showcase-stack\">" +
    stack +
    "</div></div>"
  );
}

function renderVideo(project) {
  const video = project.video || {};
  if (video.src) {
    return (
      "<figure class=\"project-video sketch-box\">" +
      "<video controls playsinline preload=\"metadata\" poster=\"" +
      escapeHtml(video.poster || "") +
      "\">" +
      "<source src=\"" +
      escapeHtml(video.src) +
      "\" type=\"video/mp4\">" +
      "Your browser does not support embedded video." +
      "</video>" +
      "<figcaption>" +
      escapeHtml(video.caption || "") +
      "</figcaption></figure>"
    );
  }

  return (
    "<figure class=\"project-video project-video-placeholder sketch-box\">" +
    "<div class=\"video-placeholder-inner\" aria-label=\"Video placeholder\">" +
    "<span class=\"video-placeholder-icon\" aria-hidden=\"true\">▶</span>" +
    "<p><strong>Video walkthrough</strong></p>" +
    "<p>" +
    escapeHtml(video.caption || "Video will be added here when ready.") +
    "</p>" +
    "</div></figure>"
  );
}

function renderProject(project) {
  const tools = (project.tools || [])
    .map((tool) => "<li>" + escapeHtml(tool) + "</li>")
    .join("");
  const highlights = (project.highlights || [])
    .map((item) => "<li>" + escapeHtml(item) + "</li>")
    .join("");
  const metrics = (project.metrics || [])
    .map(
      (metric) =>
        "<div class=\"project-metric\"><strong>" +
        escapeHtml(metric.value) +
        "</strong><span>" +
        escapeHtml(metric.label) +
        "</span></div>"
    )
    .join("");

  const videoBlock =
    project.video && project.video.src ? renderVideo(project) : "";

  return (
    "<article class=\"project-card sketch-box\" id=\"project-" +
    escapeHtml(project.id) +
    "\">" +
    "<header class=\"project-header\">" +
    "<p class=\"project-number\">Project " +
    escapeHtml(project.number || "") +
    "</p>" +
    "<div class=\"project-title-row\">" +
    "<h3>" +
    escapeHtml(project.title) +
    "</h3>" +
    "<span class=\"project-status\">" +
    escapeHtml(project.status || "") +
    "</span>" +
    "</div>" +
    "<p class=\"project-subtitle\">" +
    escapeHtml(project.subtitle || "") +
    " · " +
    escapeHtml(project.year || "") +
    "</p>" +
    "</header>" +
    "<div class=\"project-body\">" +
    "<div class=\"project-copy\">" +
    "<p class=\"project-summary\">" +
    escapeHtml(project.summary || "") +
    "</p>" +
    "<div class=\"project-metrics\">" +
    metrics +
    "</div>" +
    "<h4>Key contributions</h4>" +
    "<ul>" +
    highlights +
    "</ul>" +
    "<h4>Tools</h4>" +
    "<ul class=\"project-tools\">" +
    tools +
    "</ul>" +
    "</div>" +
    renderProjectShowcase(project) +
    videoBlock +
    "</div>" +
    "</article>"
  );
}

function renderProjects(container, projects) {
  const cards = projects.map(renderProject).join("");
  container.innerHTML = cards;
}

async function initPortfolio() {
  const aboutRoot = document.getElementById("portfolioAbout");
  const projectsRoot = document.getElementById("portfolioProjects");
  if (!aboutRoot || !projectsRoot) return;

  renderAbout(aboutRoot);

  try {
    const response = await fetch("assets/data/portfolio-projects.json");
    const data = await response.json();
    renderProjects(projectsRoot, data.projects || []);
  } catch (error) {
    projectsRoot.innerHTML =
      "<p class=\"source-note\">Could not load portfolio projects.</p>";
  }
}

function initPortalTabs() {
  const tabs = document.querySelectorAll(".portal-tab");
  const views = document.querySelectorAll(".portal-view");
  const navResearch = document.querySelector(".navlinks-research");
  const navPortfolio = document.querySelector(".navlinks-portfolio");

  function setView(name) {
    tabs.forEach((tab) => {
      tab.classList.toggle("active", tab.dataset.tab === name);
      tab.setAttribute("aria-selected", tab.dataset.tab === name ? "true" : "false");
    });
    views.forEach((view) => {
      view.classList.toggle("active", view.dataset.view === name);
      view.hidden = view.dataset.view !== name;
    });
    if (navResearch) navResearch.hidden = name !== "research";
    if (navPortfolio) navPortfolio.hidden = name !== "portfolio";
    document.body.dataset.activePortal = name;
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => setView(tab.dataset.tab));
  });

  const hash = window.location.hash;
  if (hash.startsWith("#portfolio")) {
    setView("portfolio");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initPortalTabs();
  initPortfolio();
});
