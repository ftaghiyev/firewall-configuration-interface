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

function AskContextDialog() {
  return (
    <Dialog>
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
            />
            <div className="flex items-center justify-center space-x-2">
              <div className="h-[0.5px] bg-gray-500 w-full"></div>
              <span className="text-gray-400 mx-4">or</span>
              <div className="h-[0.5px] bg-gray-500 w-full"></div>
            </div>
            <div>
              <Label>Upload File</Label>
              <Input type="file" className="mt-2 w-full" />
            </div>
          </div>
        </DialogHeader>
      </DialogContent>
    </Dialog>
  );
}

export default AskContextDialog;
