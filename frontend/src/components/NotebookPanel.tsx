import { useEffect, useState } from "react";
import { useSession } from "@/hooks/useSession";

interface Notebook {
  name: string;
  path: string;
}

export function NotebookPanel() {
  const sessionId = useSession();
  const [notebooks, setNotebooks] = useState<Notebook[]>([]);
  const [baseUrl, setBaseUrl] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string | null>(null);
  const [hoveredTab, setHoveredTab] = useState<string | null>(null);

  useEffect(() => {
    const es = new EventSource(`/notebooks/watch?session_id=${sessionId}`);
    let initialized = false;

    es.onmessage = (e) => {
      const data: Notebook[] = JSON.parse(e.data);
      setNotebooks(data);
      setActiveTab((prev) => {
        if (!initialized) {
          initialized = true;
          const welcome = data.find((nb) => nb.name === "Welcome");
          return welcome ? "Welcome" : data[0]?.name ?? null;
        }
        const stillExists = data.some((nb) => nb.name === prev);
        return stillExists ? prev : data[0]?.name ?? null;
      });
    };

    return () => es.close();
  }, [sessionId]);

  useEffect(() => {
    fetch(`/notebooks/${sessionId}`)
      .then((r) => r.json())
      .then((data: { url: string }) => setBaseUrl(data.url))
      .catch(() => {});
  }, [sessionId]);

  const iframeSrc =
    baseUrl && activeTab ? `${baseUrl}/?file=${activeTab}.py` : null;

  return (
    <div className="flex flex-col flex-1 min-w-0 bg-carbon/30">
      {/* Notebook tabs */}
      {notebooks.length > 0 && (
        <div className="flex items-end border-b border-jet-light/50 px-2 pt-1 overflow-x-auto shrink-0 gap-0.5">
          {notebooks.map((nb) => {
            const isActive = activeTab === nb.name;
            const isHovered = hoveredTab === nb.name;
            return (
              <button
                key={nb.name}
                onClick={() => setActiveTab(nb.name)}
                onMouseEnter={() => setHoveredTab(nb.name)}
                onMouseLeave={() => setHoveredTab(null)}
                className={`relative px-4 py-2 text-xs font-medium tracking-wide whitespace-nowrap transition-all duration-200 rounded-t-lg ${
                  isActive
                    ? "bg-carbon text-linen"
                    : isHovered
                      ? "text-linen/70 bg-jet-light/30"
                      : "text-linen/35"
                }`}
              >
                {nb.name}
                {/* Active tab indicator */}
                {isActive && (
                  <span className="absolute bottom-0 left-2 right-2 h-[2px] bg-brick rounded-t-full" />
                )}
              </button>
            );
          })}
        </div>
      )}

      {/* Iframe or loading skeleton */}
      <div className="flex-1 relative">
        {iframeSrc ? (
          <iframe
            key={iframeSrc}
            src={iframeSrc}
            className="absolute inset-0 w-full h-full border-0 animate-fade-in"
            title={activeTab ?? "Marimo notebook"}
          />
        ) : (
          <div className="absolute inset-0 p-6 space-y-4 animate-fade-in">
            <div className="h-8 rounded-lg animate-shimmer" />
            <div className="h-36 rounded-lg animate-shimmer" style={{ animationDelay: "0.1s" }} />
            <div className="h-24 rounded-lg animate-shimmer" style={{ animationDelay: "0.2s" }} />
            <div className="h-20 rounded-lg animate-shimmer" style={{ animationDelay: "0.3s" }} />
          </div>
        )}
      </div>
    </div>
  );
}
