import { useEffect, useState } from "react";
import { useSession } from "@/hooks/useSession";

interface Notebook {
  name: string;
  path: string;
}

export function NotebookPanel() {
  const sessionId = useSession();
  const [notebooks, setNotebooks] = useState<Notebook[]>([]);
  const [notebookUrl, setNotebookUrl] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string | null>(null);

  useEffect(() => {
    fetch("/notebooks", { headers: { "x-session-id": sessionId } })
      .then((r) => r.json())
      .then((data: Notebook[]) => {
        setNotebooks(data);
        if (data.length > 0) setActiveTab(data[0].name);
      })
      .catch(() => {});

    fetch(`/notebooks/${sessionId}`)
      .then((r) => r.json())
      .then((data: { url: string }) => setNotebookUrl(data.url))
      .catch(() => {});
  }, [sessionId]);

  return (
    <div className="flex flex-col flex-1 min-w-0">
      {/* Notebook tabs */}
      {notebooks.length > 0 && (
        <div className="flex border-b border-border overflow-x-auto shrink-0">
          {notebooks.map((nb) => (
            <button
              key={nb.name}
              onClick={() => setActiveTab(nb.name)}
              className={`px-4 py-2 text-sm whitespace-nowrap border-b-2 transition-colors ${
                activeTab === nb.name
                  ? "border-primary text-primary font-medium"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              {nb.name}
            </button>
          ))}
        </div>
      )}

      {/* Iframe or skeleton */}
      <div className="flex-1 relative">
        {notebookUrl ? (
          <iframe
            src={notebookUrl}
            className="absolute inset-0 w-full h-full border-0"
            title="Marimo notebook"
          />
        ) : (
          <div className="absolute inset-0 p-4 space-y-3">
            <div className="h-8 rounded-md bg-muted animate-pulse" />
            <div className="h-32 rounded-md bg-muted animate-pulse" />
            <div className="h-24 rounded-md bg-muted animate-pulse" />
            <div className="h-16 rounded-md bg-muted animate-pulse" />
          </div>
        )}
      </div>
    </div>
  );
}
