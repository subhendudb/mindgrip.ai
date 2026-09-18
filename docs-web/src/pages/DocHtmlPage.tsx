import { Navigate, useParams } from "react-router-dom";
import { HtmlFragment } from "../components/HtmlFragment";
import { CUSTOM_PAGES, HTML_FRAGMENT_PAGES } from "../data/nav";

export function DocHtmlPage() {
  const { slug = "" } = useParams<{ slug: string }>();

  if (!HTML_FRAGMENT_PAGES.has(slug) || !(slug in CUSTOM_PAGES)) {
    return <Navigate to="/" replace />;
  }

  return <HtmlFragment id={slug} />;
}
