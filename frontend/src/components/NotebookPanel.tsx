import { useNotebooks } from "@/hooks/useNotebooks";

export function NotebookPanel() {
  const { activeTab, baseUrl } = useNotebooks();

  const iframeSrc =
    baseUrl && activeTab ? `${baseUrl}/?file=${activeTab}.py` : null;

  return (
    <div className="flex flex-col flex-1 min-w-0 bg-carbon/30">
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
