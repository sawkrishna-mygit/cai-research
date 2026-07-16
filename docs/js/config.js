/**
 * CAI deployment URLs — auto-detect local vs production.
 */
const CAI_CONFIG = (() => {
  const isLocal =
    location.hostname === "localhost" || location.hostname === "127.0.0.1";

  const PRODUCTION = {
    portfolioUrl: "https://sawkrishna-mygit.github.io/cai-research/",
    playgroundUrl: "https://cai-research-playground.streamlit.app",
    githubUrl: "https://github.com/sawkrishna-mygit/cai-research",
  };

  const LOCAL = {
    portfolioUrl: "http://localhost:8080/",
    playgroundUrl: "http://localhost:8501",
    githubUrl: PRODUCTION.githubUrl,
  };

  return isLocal ? LOCAL : PRODUCTION;
})();

function wirePlaygroundLinks() {
  document.querySelectorAll("[data-playground-link]").forEach((el) => {
    el.href = CAI_CONFIG.playgroundUrl;
  });
}

function wireGithubLinks() {
  document.querySelectorAll("[data-github-link]").forEach((el) => {
    el.href = CAI_CONFIG.githubUrl;
  });
}

document.addEventListener("DOMContentLoaded", () => {
  wirePlaygroundLinks();
  wireGithubLinks();
});
