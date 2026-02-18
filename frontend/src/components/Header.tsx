export function Header() {
  return (
    <header className="flex h-12 shrink-0 border-b border-border overflow-hidden">
      <div className="flex items-center gap-2 px-4 w-[40%]">
        <div className="flex h-6 w-6 items-center justify-center rounded bg-gradient-to-br from-amber-400 to-rose-500">
          <span className="text-white font-bold text-xs">K</span>
        </div>
        <span className="font-semibold text-sm tracking-tight">Kitsune</span>
      </div>
      <div className="flex-1 bg-gradient-to-r from-amber-400/80 via-orange-400/80 to-rose-400/80" />
    </header>
  );
}
