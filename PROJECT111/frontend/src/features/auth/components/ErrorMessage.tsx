export function ErrorMessage({ children }: { children: React.ReactNode }) {
  return <div className="text-red-500 text-sm">{children}</div>;
}