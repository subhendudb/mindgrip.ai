import { Navigate, Route, Routes, useParams } from "react-router-dom";
import { Layout } from "./components/Layout";
import { CUSTOM_PAGES, HTML_FRAGMENT_PAGES } from "./data/nav";
import { DocHtmlPage } from "./pages/DocHtmlPage";
import { DocMarkdownPage } from "./pages/DocMarkdownPage";
import { HomePage } from "./pages/HomePage";

function DocBySlug() {
  const { slug = "" } = useParams<{ slug: string }>();
  if (!(slug in CUSTOM_PAGES)) {
    return <Navigate to="/" replace />;
  }
  if (HTML_FRAGMENT_PAGES.has(slug)) {
    return <DocHtmlPage />;
  }
  return <DocMarkdownPage />;
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path=":slug" element={<DocBySlug />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
