import AdditionDropdown from "@/components/chat/addition-dropdown";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { Textarea } from "@/components/ui/textarea";
import { confirmPolicy } from "@/features/translation/api";
import GlobalLayout from "@/layouts/global-layout";
import { useState } from "react";
import { LuPlus, LuSend } from "react-icons/lu";
import { toast } from "sonner";

type Message = {
  role: "user" | "assistant";
  content: string;
};

function Chat() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [response, setResponse] = useState("");

  const handleSendMessage = async () => {
    if (message.trim() === "") return;

    setMessages((msgs) => [...msgs, { role: "user", content: message }]);

    try {
      const response = await confirmPolicy({
        message: message,
        context: "Please translate the following policy.",
      });

      setMessage("");
      setMessages((msgs) => [
        ...msgs,
        { role: "assistant", content: response.summary },
      ]);
    } catch (error) {
      toast.error("Failed to translate policy.");
      setMessages((msgs) => msgs.slice(0, -1));
      return;
    }
  };

  return (
    <GlobalLayout>
      <div className="h-full flex">
        <div className="p-4 min-w-48">
          <Label> Policy History </Label>
        </div>
        <ResizablePanelGroup
          direction="horizontal"
          className="h-full rounded-lg border md:min-w-[450px]"
        >
          <ResizablePanel defaultSize={80}>
            <div
              className={`flex flex-col h-full p-4 md:p-10 xl:px-20 xl:py-10 2xl:px-40 2xl:py-20 ${
                messages.length === 0 ? "justify-center" : "justify-between"
              }`}
            >
              <div className="flex flex-col gap-2.5">
                {messages.map((msg, index) => (
                  <div
                    key={index}
                    className={`${
                      msg.role === "user"
                        ? "self-end bg-gray-800 rounded-xl p-2"
                        : "self-start"
                    }`}
                  >
                    <span
                      className={
                        msg.role === "user"
                          ? "w-fit bg- rounded-3xl"
                          : "font-normal"
                      }
                    >
                      {msg.content}
                    </span>
                  </div>
                ))}
              </div>
              <div className={`flex`}>
                <div className="relative flex w-full">
                  <Textarea
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Ask your policy translation..."
                    className="w-full pb-12"
                  />
                  <div className="flex w-full justify-between absolute bottom-4 pl-1 pr-4">
                    <AdditionDropdown />
                    <Button
                      onClick={handleSendMessage}
                      variant="ghost"
                      size="icon"
                      className="self-end"
                    >
                      <LuSend
                        className={`transition-all duration-300 ${
                          message ? "size-5" : "size-0"
                        }`}
                      />
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </ResizablePanel>
          <ResizableHandle />
          <ResizablePanel defaultSize={20}>
            <ResizablePanelGroup direction="vertical">
              <ResizablePanel defaultSize={100}>
                <div className="flex h-full items-center justify-center p-6">
                  <Label>No flow created yet.</Label>
                </div>
              </ResizablePanel>
            </ResizablePanelGroup>
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>
    </GlobalLayout>
  );
}

export default Chat;
