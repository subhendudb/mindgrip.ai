import { useEffect } from "react";
import { Navigate, useParams } from "react-router-dom";
import { MarkdownView } from "../components/MarkdownView";
import { CUSTOM_PAGES, HTML_FRAGMENT_PAGES } from "../data/nav";
import acronyms from "../content/acronyms.md?raw";
import directoryStructure from "../content/directory_structure.md?raw";

export const MARKDOWN_MAP: Record<string, string> = {
  directory_structure: directoryStructure,
  acronyms,
};

type Props = {
  slug?: string;
};

export function DocMarkdownPage({ slug: slugProp }: Props) {
  const params = useParams<{ slug: string }>();
  const slug = slugProp ?? params.slug ?? "";
  const content = MARKDOWN_MAP[slug];
  const valid =
    slug in CUSTOM_PAGES && !HTML_FRAGMENT_PAGES.has(slug) && Boolean(content);

  useEffect(() => {
    if (valid) {
      document.title = `${CUSTOM_PAGES[slug]} · MindGrip AI`;
    }
  }, [slug, valid]);

  if (!valid) {
    return <Navigate to="/" replace />;
  }

  return <MarkdownView content={content} />;
}
