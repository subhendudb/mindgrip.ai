import { AUTHOR_NAME, AUTHOR_URL } from "../data/nav";

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <p>
        © 2026{" "}
        <a href={AUTHOR_URL} target="_blank" rel="noopener noreferrer">
          {AUTHOR_NAME}
        </a>
        . All rights reserved.
      </p>
    </footer>
  );
}
