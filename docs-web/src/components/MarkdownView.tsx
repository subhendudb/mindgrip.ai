import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Link } from "react-router-dom";
import type { Components } from "react-markdown";

function normalizeInternalHref(href: string): string | null {
  // ./foo, ./foo.md, foo.mdx, /foo → /foo
  if (/^https?:\/\//i.test(href) || href.startsWith("mailto:")) return null;
  if (href.startsWith("#")) return null;

  let path = href;
  if (path.startsWith("./")) path = path.slice(1);
  if (!path.startsWith("/")) path = `/${path}`;

  const hashIdx = path.indexOf("#");
  const hash = hashIdx >= 0 ? path.slice(hashIdx) : "";
  let base = hashIdx >= 0 ? path.slice(0, hashIdx) : path;

  base = base.replace(/\.(mdx?|html)$/i, "");
  if (base === "/mindgrip") base = "/";

  return `${base}${hash}`;
}

const components: Components = {
  a({ href, children, ...rest }) {
    if (!href) {
      return <a {...rest}>{children}</a>;
    }
    const internal = normalizeInternalHref(href);
    if (internal) {
      return (
        <Link to={internal} {...rest}>
          {children}
        </Link>
      );
    }
    const external = /^https?:\/\//i.test(href);
    return (
      <a
        href={href}
        {...(external
          ? { target: "_blank", rel: "noopener noreferrer" }
          : {})}
        {...rest}
      >
        {children}
      </a>
    );
  },
  img({ src, alt, ...rest }) {
    let resolved = src ?? "";
    // Rewrite ../images/... or images/... to /images/...
    if (resolved.includes("images/")) {
      const m = resolved.match(/(?:^|\/)(images\/.+)$/);
      if (m) resolved = `/${m[1]}`;
    }
    return <img src={resolved} alt={alt ?? ""} {...rest} />;
  },
};

type Props = {
  content: string;
};

export function MarkdownView({ content }: Props) {
  return (
    <div className="doc-measure">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {content}
      </ReactMarkdown>
    </div>
  );
}
