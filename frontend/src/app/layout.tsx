import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "FinWise",
  description: "Personal finance goals and AI-guided spending",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
