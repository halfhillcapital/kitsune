import { Sidebar } from "@/components/Sidebar";
import { Header } from "@/components/Header";
import { ChatPanel } from "@/components/ChatPanel";
import { NotebookPanel } from "@/components/NotebookPanel";

export default function App() {
  return (
    <div className="flex h-screen overflow-hidden bg-jet noise-overlay">
      <Sidebar />
      <div className="relative z-10 flex flex-col flex-1 min-w-0">
        <Header />
        <main className="flex flex-1 min-h-0">
          <ChatPanel />
          <NotebookPanel />
        </main>
      </div>
    </div>
  );
}
