export function Header() {
  return (
    <header className="flex items-center h-12 shrink-0 border-b border-jet-light/50 bg-carbon/40">
      {/* Brand section aligned with chat panel */}
      <div className="flex items-center gap-3 px-5 w-[40%]">
        <span className="font-display text-sm tracking-wider text-linen/90 uppercase">
          Kitsune
        </span>
        <span className="text-[10px] font-body font-light tracking-widest text-rose/50 uppercase ml-1">
          agent
        </span>
      </div>

      {/* Accent line — brick red gradient fading out */}
      <div className="flex-1 flex items-center h-full">
        <div className="h-px w-full bg-gradient-to-r from-brick/60 via-brick/20 to-transparent" />
      </div>
    </header>
  );
}
