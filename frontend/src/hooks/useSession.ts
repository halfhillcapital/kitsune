import { useMemo } from "react";

export function useSession(): string {
  return useMemo(() => {
    let id = localStorage.getItem("kitsune-session-id");
    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem("kitsune-session-id", id);
    }
    return id;
  }, []);
}
