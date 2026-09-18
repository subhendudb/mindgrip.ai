import { NavLink } from "react-router-dom";
import {
  APP_NAME,
  APP_TAGLINE,
  CUSTOM_PAGES,
  LELAB_DOCS_URL,
  LEROBOT_DOCS_URL,
  NAV_ORDER,
} from "../data/nav";

type Props = {
  collapsed: boolean;
  onToggle: () => void;
};

export function Sidebar({ collapsed, onToggle }: Props) {
  return (
    <nav
      className={`sidebar${collapsed ? " is-collapsed" : ""}`}
      aria-hidden={collapsed}
    >
      <div className="sidebar-top">
        <NavLink to="/" className="brand-lockup" end tabIndex={collapsed ? -1 : undefined}>
          <img
            src="/brand/mindgrip-mark.svg"
            alt=""
            className="brand-mark"
            width={40}
            height={40}
          />
          <span className="brand-text">
            <span className="brand-name">{APP_NAME}</span>
            <span className="brand-sub">project docs</span>
          </span>
        </NavLink>
        <button
          type="button"
          className="sidebar-toggle"
          onClick={onToggle}
          title="Collapse menu"
          aria-label="Collapse navigation menu"
          aria-expanded={!collapsed}
          tabIndex={collapsed ? -1 : undefined}
        >
          <CollapseIcon />
        </button>
      </div>

      <div className="sidebar-body">
        <details className="nav-root mindgrip" open>
          <summary>Project pages</summary>
          <p className="brand-tagline">{APP_TAGLINE}</p>
          <ul className="nav-section">
            {NAV_ORDER.map((slug) => (
              <li key={slug}>
                <NavLink
                  to={slug === "mindgrip" ? "/" : `/${slug}`}
                  className={({ isActive }) => (isActive ? "active" : undefined)}
                  end={slug === "mindgrip"}
                  tabIndex={collapsed ? -1 : undefined}
                >
                  {CUSTOM_PAGES[slug]}
                </NavLink>
              </li>
            ))}
          </ul>
        </details>

        <div className="ext-docs">
          <strong>LeRobot docs</strong>
          Official Hugging Face documentation (not mirrored here).
          <br />
          <a
            href={LEROBOT_DOCS_URL}
            target="_blank"
            rel="noopener noreferrer"
            tabIndex={collapsed ? -1 : undefined}
          >
            {LEROBOT_DOCS_URL}
          </a>
          <br />
          <strong>LeLab docs</strong>
          <br />
          <a
            href={LELAB_DOCS_URL}
            target="_blank"
            rel="noopener noreferrer"
            tabIndex={collapsed ? -1 : undefined}
          >
            {LELAB_DOCS_URL}
          </a>
        </div>
      </div>
    </nav>
  );
}

function CollapseIcon() {
  return (
    <svg
      width="15"
      height="15"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.4"
      aria-hidden
    >
      <path d="M15 6 9 12l6 6" />
    </svg>
  );
}
