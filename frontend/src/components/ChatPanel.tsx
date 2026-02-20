import { useState, useEffect, useRef } from "react";
import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport } from "ai";
import { Send, Sparkles } from "lucide-react";
import { useSession } from "@/hooks/useSession";

export function ChatPanel() {
  const sessionId = useSession();
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const [inputFocused, setInputFocused] = useState(false);

  const { messages, status, sendMessage } = useChat({
    transport: new DefaultChatTransport({
      api: "/chat",
      headers: { "x-session-id": sessionId },
    }),
  });

  const isLoading = status === "submitted" || status === "streaming";

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    sendMessage({ text: input });
    setInput("");
  }

  return (
    <div className="flex flex-col w-[40%] border-r border-jet-light/50 min-w-0 bg-jet">
      {/* Message list */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center gap-4 animate-fade-in">
            <img
              src="/kitsune-logo.png"
              alt=""
              className="w-16 h-16 object-contain opacity-20"
            />
            <div className="space-y-2">
              <p className="text-sm font-medium text-linen/60">
                Start a conversation with Kitsune
              </p>
              <p className="text-xs text-linen/30">
                Ask me to create or modify a notebook
              </p>
            </div>
          </div>
        )}
        {messages.map((m, idx) => (
          <div
            key={m.id}
            className={`flex ${m.role === "user" ? "justify-end" : "justify-start"} ${
              m.role === "user" ? "animate-slide-right" : "animate-slide-left"
            }`}
            style={{ animationDelay: `${Math.min(idx * 0.05, 0.3)}s` }}
          >
            <div
              className={`max-w-[85%] rounded-xl px-4 py-2.5 text-sm leading-relaxed ${
                m.role === "user"
                  ? "bg-brick text-linen rounded-br-sm"
                  : "bg-carbon text-linen/90 rounded-bl-sm border border-jet-light/40"
              }`}
            >
              {m.parts
                .filter((p) => p.type === "text")
                .map((p, i) => (
                  <p key={i} className="whitespace-pre-wrap">
                    {"text" in p ? p.text : ""}
                  </p>
                ))}
            </div>
          </div>
        ))}
        {isLoading && messages[messages.length - 1]?.role !== "assistant" && (
          <div className="flex justify-start animate-slide-left">
            <div className="bg-carbon rounded-xl rounded-bl-sm border border-jet-light/40 px-4 py-3">
              <div className="flex gap-1.5">
                {[0, 1, 2].map((i) => (
                  <span
                    key={i}
                    className="w-1.5 h-1.5 bg-brick rounded-full"
                    style={{
                      animation: `typing-dot 1.2s ease-in-out ${i * 0.2}s infinite`,
                    }}
                  />
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input bar */}
      <div className="px-4 pb-4 pt-2">
        <form
          onSubmit={handleSubmit}
          className={`flex items-center gap-2 rounded-xl border bg-carbon/80 px-3 py-2 transition-all duration-300 ${
            inputFocused
              ? "border-brick/50 shadow-[0_0_20px_rgba(189,47,37,0.1)]"
              : "border-jet-light/50"
          }`}
        >
          <Sparkles className="h-4 w-4 text-brick/40 shrink-0" />
          <input
            className="flex-1 bg-transparent text-sm text-linen placeholder:text-linen/25 focus:outline-none"
            placeholder="Message Kitsune..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onFocus={() => setInputFocused(true)}
            onBlur={() => setInputFocused(false)}
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="flex items-center justify-center rounded-lg h-8 w-8 bg-brick text-linen transition-all duration-200 hover:bg-brick-glow disabled:opacity-30 disabled:hover:bg-brick shrink-0"
          >
            <Send className="h-3.5 w-3.5" />
          </button>
        </form>
      </div>
    </div>
  );
}
