import { MessageSquare, BookOpen, Settings } from "lucide-react";
import { useState } from "react";

const navItems = [
  { icon: MessageSquare, label: "Chat", id: "chat" },
  { icon: BookOpen, label: "Notebooks", id: "notebooks" },
];

export function Sidebar() {
  const [active, setActive] = useState("chat");
  const [hovered, setHovered] = useState<string | null>(null);

  return (
    <aside className="relative z-10 flex flex-col items-center w-[60px] bg-carbon py-4 shrink-0 border-r border-jet-light/50">
      {/* Logo */}
      <div className="mb-6 group cursor-pointer">
        <img
          src="/kitsune-logo.png"
          alt="Kitsune"
          className="w-9 h-9 object-contain animate-pulse-glow transition-transform duration-300 group-hover:scale-110"
        />
      </div>

      {/* Divider */}
      <div className="w-6 h-px bg-jet-lighter mb-4" />

      {/* Navigation */}
      <nav className="flex flex-col items-center gap-1 flex-1">
        {navItems.map((item) => {
          const isActive = active === item.id;
          const isHovered = hovered === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActive(item.id)}
              onMouseEnter={() => setHovered(item.id)}
              onMouseLeave={() => setHovered(null)}
              className="relative flex h-10 w-10 items-center justify-center rounded-lg transition-all duration-200"
              title={item.label}
            >
              {/* Active indicator bar */}
              {isActive && (
                <span className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-[14px] w-[3px] h-5 bg-brick rounded-r-full transition-all" />
              )}
              {/* Background glow */}
              <span
                className={`absolute inset-0 rounded-lg transition-all duration-200 ${
                  isActive
                    ? "bg-brick/15"
                    : isHovered
                      ? "bg-jet-light/60"
                      : "bg-transparent"
                }`}
              />
              <item.icon
                className={`relative h-[18px] w-[18px] transition-colors duration-200 ${
                  isActive
                    ? "text-brick-glow"
                    : isHovered
                      ? "text-linen"
                      : "text-linen/40"
                }`}
              />
            </button>
          );
        })}
      </nav>

      {/* Settings */}
      <button
        onMouseEnter={() => setHovered("settings")}
        onMouseLeave={() => setHovered(null)}
        className="relative flex h-10 w-10 items-center justify-center rounded-lg transition-all duration-200"
        title="Settings"
      >
        <span
          className={`absolute inset-0 rounded-lg transition-all duration-200 ${
            hovered === "settings" ? "bg-jet-light/60" : "bg-transparent"
          }`}
        />
        <Settings
          className={`relative h-[18px] w-[18px] transition-colors duration-200 ${
            hovered === "settings" ? "text-linen" : "text-linen/40"
          }`}
        />
      </button>
    </aside>
  );
}
