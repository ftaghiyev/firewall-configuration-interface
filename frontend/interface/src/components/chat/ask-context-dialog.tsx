import { LuSettings2 } from "react-icons/lu";
import { Button } from "../ui/button";
import {
  Dialog,
  DialogDescription,
  DialogHeader,
  DialogTrigger,
  DialogContent,
  DialogTitle,
} from "../ui/dialog";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Textarea } from "../ui/textarea";
import { useTranslationStore } from "@/features/translation/store";
import { useState } from "react";
import { toast } from "sonner";

function AskContextDialog() {
  const context = useTranslationStore((s) => s.context);
  const setContextDescription = useTranslationStore(
    (s) => s.setContextDescription
  );
  const setContextDetails = useTranslationStore((s) => s.setContextDetails);
  const setContextFilename = useTranslationStore((s) => s.setContextFilename);

  console.log("Current context in AskContextDialog:", context);

  const [open, setOpen] = useState(false);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];

    if (!file) return;

    try {
      setContextDetails(undefined); // Reset previous details
      setContextFilename(undefined);
      const text = await file.text();
      const json = JSON.parse(text);
      setContextDetails(json);
      setContextFilename(file.name);
    } catch (err) {
      toast.error("Invalid JSON file.");
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" className="w-full justify-start">
          <LuSettings2 /> Add context
        </Button>
      </DialogTrigger>

      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Context</DialogTitle>
          <DialogDescription>
            Provide additional context to improve the translation accuracy.
          </DialogDescription>

          <div className="flex flex-col gap-4">
            <Textarea
              placeholder="Enter additional context here..."
              className="mt-4 w-full"
              value={
                typeof context.description === "string"
                  ? context.description
                  : ""
              }
              onChange={(e) => setContextDescription(e.target.value)}
            />
            <div className="flex items-center justify-center space-x-2">
              <div className="h-[0.5px] bg-gray-500 w-full"></div>
              <span className="text-gray-400 mx-4">or</span>
              <div className="h-[0.5px] bg-gray-500 w-full"></div>
            </div>
            <div className="flex flex-col gap-1.5">
              <Label>Upload File</Label>
              <Input
                type="file"
                className="mt-2 w-full"
                onChange={handleFileChange}
              />
              <p
                className={`${
                  context.details ? "text-green-500" : "text-gray-400"
                }`}
              >
                {context.details && context.filename
                  ? `File uploaded: ${context.filename}`
                  : context.details
                  ? "File uploaded."
                  : "No file selected."}
              </p>
              <div>
                {context.details && (
                  <pre className="max-h-40 w-full overflow-auto rounded-md bg-gray-800 p-2 text-xs whitespace-pre-wrap break-all">
                    {JSON.stringify(context.details, null, 2)}
                  </pre>
                )}
              </div>
            </div>
            <div className="flex justify-end">
              <Button onClick={() => setOpen(false)}>Confirm</Button>
            </div>
          </div>
        </DialogHeader>
      </DialogContent>
    </Dialog>
  );
}

export default AskContextDialog;

