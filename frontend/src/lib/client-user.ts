const STORAGE_KEY = "matematex-client-user-id";

/** Stable per-browser identity for job isolation when using a shared API key. */
export function getClientUserId(): string {
  if (typeof window === "undefined") return "";
  try {
    let id = localStorage.getItem(STORAGE_KEY);
    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem(STORAGE_KEY, id);
    }
    return id;
  } catch {
    return "";
  }
}

export function clientUserHeaders(): Record<string, string> {
  const id = getClientUserId();
  return id ? { "X-Client-User-Id": id } : {};
}
