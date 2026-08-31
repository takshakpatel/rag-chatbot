import type { Metadata } from "next";
import "./globals.css";
import ContractComment from "./ContractComment";

export const metadata: Metadata = {
  title: "Lumen — Ask your documents",
  description:
    "Lumen: a glass-frosted RAG studio. Upload documents and read grounded, source-cited answers.",
};

const themeInit = `
  (function () {
    try {
      var t = localStorage.getItem('rag-deepdive-theme');
      if (t === 'light') document.documentElement.classList.add('theme-light');
    } catch (e) {}
  })();
`;

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInit }} />
      </head>
      <body style={{ background: "var(--abyss-0)", color: "var(--ink)" }}>
        <ContractComment />
        {children}
      </body>
    </html>
  );
}
