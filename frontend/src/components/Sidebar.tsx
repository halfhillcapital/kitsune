import { MessageSquare, BookOpen, Settings } from "lucide-react";

export function Sidebar() {
  return (
    <aside className="flex flex-col items-center gap-2 w-14 border-r border-border bg-muted/30 py-3 shrink-0">
      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-amber-400 to-rose-500 mb-2">
        <span className="text-white font-bold text-sm">K</span>
      </div>
      <nav className="flex flex-col items-center gap-1 flex-1">
        <button className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors">
          <MessageSquare className="h-4 w-4" />
        </button>
        <button className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors">
          <BookOpen className="h-4 w-4" />
        </button>
      </nav>
      <button className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors">
        <Settings className="h-4 w-4" />
      </button>
    </aside>
  );
}
