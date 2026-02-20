import { useEffect, useState } from "react";
import { useSession } from "@/hooks/useSession";

export interface Notebook {
  name: string;
  path: string;
}

let sharedNotebooks: Notebook[] = [];
let sharedActiveTab: string | null = null;
let sharedBaseUrl: string | null = null;
const listeners = new Set<() => void>();

function notify() {
  listeners.forEach((l) => l());
}

export function useNotebooks() {
  const sessionId = useSession();
  const [, rerender] = useState(0);

  useEffect(() => {
    const listener = () => rerender((n) => n + 1);
    listeners.add(listener);
    return () => { listeners.delete(listener); };
  }, []);

  useEffect(() => {
    const es = new EventSource(`/notebooks/watch?session_id=${sessionId}`);
    let initialized = false;

    es.onmessage = (e) => {
      const data: Notebook[] = JSON.parse(e.data);
      sharedNotebooks = data;

      if (!initialized) {
        initialized = true;
        const welcome = data.find((nb) => nb.name === "Welcome");
        sharedActiveTab = welcome ? "Welcome" : data[0]?.name ?? null;
      } else {
        const stillExists = data.some((nb) => nb.name === sharedActiveTab);
        if (!stillExists) sharedActiveTab = data[0]?.name ?? null;
      }
      notify();
    };

    return () => es.close();
  }, [sessionId]);

  useEffect(() => {
    fetch(`/notebooks/${sessionId}`)
      .then((r) => r.json())
      .then((data: { url: string }) => {
        sharedBaseUrl = data.url;
        notify();
      })
      .catch(() => {});
  }, [sessionId]);

  return {
    notebooks: sharedNotebooks,
    activeTab: sharedActiveTab,
    baseUrl: sharedBaseUrl,
    setActiveTab(name: string) {
      sharedActiveTab = name;
      notify();
    },
  };
}
