import { useEffect, useState } from "react";
import { Link, Outlet, useLocation } from "react-router-dom";
import { APP_NAME, APP_TAGLINE } from "../data/nav";
import { Sidebar } from "./Sidebar";
import { SiteFooter } from "./SiteFooter";
import { ThemeToggle } from "./ThemeToggle";

const STORAGE_KEY = "docs-sidebar";

function readCollapsed(): boolean {
  try {
    return localStorage.getItem(STORAGE_KEY) === "collapsed";
  } catch {
    return false;
  }
}

export function Layout() {
  const { pathname } = useLocation();
  const isHome = pathname === "/" || pathname === "/mindgrip";
  const [collapsed, setCollapsed] = useState(readCollapsed);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, collapsed ? "collapsed" : "open");
    } catch {
      /* ignore */
    }
  }, [collapsed]);

  const toggle = () => setCollapsed((c) => !c);

  return (
    <div className={`layout${collapsed ? " sidebar-collapsed" : ""}`}>
      <Sidebar collapsed={collapsed} onToggle={toggle} />
      {collapsed && (
        <button
          type="button"
          className="sidebar-reopen"
          onClick={toggle}
          title="Open menu"
          aria-label="Open navigation menu"
        >
          <MenuIcon />
        </button>
      )}
      <main className="content">
        {!isHome && (
          <div className="app-brand">
            <Link to="/" className="app-brand-link">
              <img
                src="/brand/mindgrip-mark.svg"
                alt=""
                className="brand-mark"
                width={28}
                height={28}
              />
              <strong>{APP_NAME}</strong>
            </Link>
            <span className="tagline">{APP_TAGLINE}</span>
          </div>
        )}
        <Outlet />
        <SiteFooter />
      </main>
      <ThemeToggle />
    </div>
  );
}

function MenuIcon() {
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
      <path d="M4 7h16M4 12h16M4 17h16" />
    </svg>
  );
}
