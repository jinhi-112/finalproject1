import type { ReactNode } from "react";

export function Body({ children }: { children: ReactNode }) {
  return (
    <main className="w-full mx-auto py-8 px-4 min-h-[calc(100vh-64px)] flex flex-col container mt-16">
      {children}
    </main>
  );
}
