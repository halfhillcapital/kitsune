import { useState } from "react";
import { useNotebooks } from "@/hooks/useNotebooks";

export function Header() {
  const { notebooks, activeTab, setActiveTab } = useNotebooks();
  const [hoveredTab, setHoveredTab] = useState<string | null>(null);

  return (
    <header className="flex items-stretch h-12 shrink-0 border-b border-jet-light/50 bg-carbon/40">
      {/* Brand section aligned with chat panel */}
      <div className="flex items-center gap-3 px-5 w-[40%] shrink-0 border-r border-jet-light/50">
        <span className="font-display text-sm tracking-wider text-linen/90 uppercase">
          Kitsune
        </span>
        <span className="text-[10px] font-body font-light tracking-widest text-rose/50 uppercase ml-1">
          agent
        </span>
      </div>

      {/* Notebook tabs */}
      <div className="flex items-end flex-1 overflow-x-auto px-2 gap-0.5">
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
              {isActive && (
                <span className="absolute bottom-0 left-2 right-2 h-[2px] bg-brick rounded-t-full" />
              )}
            </button>
          );
        })}
      </div>
    </header>
  );
}
