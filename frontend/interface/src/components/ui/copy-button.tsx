import { useState } from "react";
import { Button } from "@/components/ui/button";
import { LuCheck, LuCopy } from "react-icons/lu";
import { cn } from "@/lib/utils";

function CopyButton({ text, className }: { text: string; className?: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);

    setTimeout(() => setCopied(false), 3000);
  };

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={handleCopy}
      className={cn("h-6 w-6 p-0", className)}
    >
      {copied ? (
        <LuCheck className="w-4 h-4 text-green-500" />
      ) : (
        <LuCopy className="w-4 h-4" />
      )}
    </Button>
  );
}

export default CopyButton;
