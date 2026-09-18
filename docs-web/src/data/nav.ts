export const APP_NAME = "MindGrip AI";
export const APP_TAGLINE =
  "Lab overlay for imitation-learning robot arms — SO-101 and beyond.";
export const LEROBOT_DOCS_URL = "https://huggingface.co/docs/lerobot";
export const LELAB_DOCS_URL = "https://huggingface.co/docs/lerobot/lelab";
export const AUTHOR_NAME = "Subhendu Datta Bhowmik";
export const AUTHOR_URL = "https://subhdb.co.in";

/** Custom project pages — order = sidebar order. */
export const CUSTOM_PAGES: Record<string, string> = {
  mindgrip: "MindGrip AI Home",
  project_page: "Pick & Place Sorting",
  roadmap: "Roadmap · Support · Reference",
  lelab: "LeLab (Recommended Path)",
  cli_menu: "CLI Command Menu",
  so101_kinematics: "Forward & Inverse Kinematics",
  policy_cheatsheet: "Policy Cheatsheet",
  optional_tooling: "Optional Tooling · MuJoCo",
  directory_structure: "Directory Structure",
  acronyms: "Acronyms Glossary",
};

/** Pages served as pre-extracted HTML fragments (interactive / custom layout). */
export const HTML_FRAGMENT_PAGES = new Set([
  "mindgrip",
  "project_page",
  "lelab",
  "cli_menu",
  "roadmap",
  "optional_tooling",
  "so101_kinematics",
  "policy_cheatsheet",
]);

export const NAV_ORDER = Object.keys(CUSTOM_PAGES);
