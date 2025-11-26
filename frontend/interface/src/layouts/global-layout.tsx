import { ModeToggle } from "@/components/ui/mode-togle";

type GlobalLayoutProps = {
  children: React.ReactNode;
};
function GlobalLayout({ children }: GlobalLayoutProps) {
  return (
    <div className="flex flex-col h-screen">
      <div className="flex justify-end">
        <ModeToggle />
      </div>
      <main className="h-full">{children}</main>
    </div>
  );
}

export default GlobalLayout;
