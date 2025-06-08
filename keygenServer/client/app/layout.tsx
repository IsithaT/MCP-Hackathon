import type { Metadata } from "next";
import { Vollkorn } from "next/font/google";
import "./globals.css";

const vollkorn = Vollkorn({
  variable: "--font-vollkorn",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "API Key Generator",
  description: "Generate and manage your API keys",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${vollkorn.variable} antialiased font-vollkorn`}
      >
        {children}
      </body>
    </html>
  );
}
