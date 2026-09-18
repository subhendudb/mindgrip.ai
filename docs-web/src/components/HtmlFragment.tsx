import { useEffect, useRef, useState } from "react";
import { CUSTOM_PAGES } from "../data/nav";

type Props = {
  id: string;
};

declare global {
  interface Window {
    renderMathInElement?: (
      el: HTMLElement,
      options?: {
        delimiters?: { left: string; right: string; display: boolean }[];
        throwOnError?: boolean;
      },
    ) => void;
  }
}

const KATEX_DELIMITERS = [
  { left: "\\[", right: "\\]", display: true },
  { left: "\\(", right: "\\)", display: false },
];

function renderFragmentMath(root: HTMLElement) {
  if (typeof window.renderMathInElement !== "function") return;
  const target =
    (root.querySelector(".kin") as HTMLElement | null) ??
    (root.querySelector("main") as HTMLElement | null) ??
    root;
  window.renderMathInElement(target, {
    delimiters: KATEX_DELIMITERS,
    throwOnError: false,
  });
}

/** Load/execute fragment <script> tags in order (innerHTML does not run them). */
async function runFragmentScripts(el: HTMLElement) {
  const scripts = Array.from(el.querySelectorAll("script"));
  for (const old of scripts) {
    await new Promise<void>((resolve, reject) => {
      const s = document.createElement("script");
      for (const attr of Array.from(old.attributes)) {
        // Sequential insert after navigation — defer would race inline init
        if (attr.name === "defer" || attr.name === "async") continue;
        s.setAttribute(attr.name, attr.value);
      }
      if (old.src) {
        s.onload = () => resolve();
        s.onerror = () => reject(new Error(`Failed to load ${old.src}`));
        old.replaceWith(s);
      } else {
        if (old.textContent) s.textContent = old.textContent;
        old.replaceWith(s);
        resolve();
      }
    });
  }
}

/**
 * Fetch a pre-extracted HTML fragment and inject it.
 * Re-runs scripts in the fragment so checklist / kinematics interactivity works.
 */
export function HtmlFragment({ id }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const title = CUSTOM_PAGES[id] ?? id;
    document.title = `${title} · MindGrip AI`;

    setLoading(true);
    setError(null);

    fetch(`/fragments/${id}.html`)
      .then(async (res) => {
        if (!res.ok) throw new Error(`Failed to load fragment (${res.status})`);
        return res.text();
      })
      .then(async (html) => {
        if (cancelled || !containerRef.current) return;
        const el = containerRef.current;
        el.innerHTML = html;

        try {
          await runFragmentScripts(el);
        } catch (err) {
          if (!cancelled) {
            console.warn("Fragment script load issue:", err);
          }
        }
        if (cancelled) return;

        // Ensure KaTeX runs even if fragment init skipped math (SPA timing)
        renderFragmentMath(el);
        setLoading(false);
      })
      .catch((err: Error) => {
        if (!cancelled) {
          setError(err.message);
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
      if (containerRef.current) containerRef.current.innerHTML = "";
    };
  }, [id]);

  return (
    <>
      {loading && <p className="fragment-status">Loading…</p>}
      {error && <p className="fragment-status">Error: {error}</p>}
      <div ref={containerRef} className="html-fragment" />
    </>
  );
}
