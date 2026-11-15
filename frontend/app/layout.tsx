import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Aivanta OS | Aivanta Labs",
  description: "Intelligence. Innovation. Automation.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="id"><body>{children}</body></html>;
}
