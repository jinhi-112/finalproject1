export function useAuth(): boolean {
  // TODO
  return !!localStorage.getItem("token");
}
