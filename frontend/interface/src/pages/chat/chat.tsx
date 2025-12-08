import AdditionDropdown from "@/components/chat/addition-dropdown";
import PipelineGraph from "@/components/chat/pipeline-graph";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { Skeleton } from "@/components/ui/skeleton";
import { Spinner } from "@/components/ui/spinner";
import { Textarea } from "@/components/ui/textarea";
import {
  useSummarizePolicy,
  useTranslatePolicy,
} from "@/features/translation/hooks";
import { useTranslationStore } from "@/features/translation/store";
import GlobalLayout from "@/layouts/global-layout";
import { useState } from "react";
import { LuSend } from "react-icons/lu";
import { toast } from "sonner";
import ReactMarkdown from "react-markdown";
import CopyButton from "@/components/ui/copy-button";

type Message = {
  role: "user" | "assistant";
  content: string;
};

type Representation = {
  policy_id: string;
  resolver_output: any;
  ir: any;
  linting_warnings: Record<string, string[]>;
  safety_warnings: string[];
  batfish_warnings: Record<string, { severity: string; message: string }[]>;
  configs: Record<string, string>;
};

function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [representations, setRepresentations] = useState<Representation[]>([]);
  const message = useTranslationStore((s) => s.message);
  const setMessage = useTranslationStore((s) => s.setMessage);
  const context = useTranslationStore((s) => s.context);

  const { summarizePolicy, loading: summarizing } = useSummarizePolicy();
  const { translatePolicy, loading: translating } = useTranslatePolicy();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const handleSendMessage = async () => {
    if (message.trim() === "") return;

    if (context.description === "" && !context.details) {
      toast.error("Please provide context description or upload a file.");
      setDropdownOpen(true);
      return;
    }

    try {
      setMessages((msgs) => [...msgs, { role: "user", content: message }]);
      setMessage("");

      const summaryResponse = await summarizePolicy({
        message,
        context,
      });

      setMessages((msgs) => [
        ...msgs,
        { role: "assistant", content: summaryResponse.summary },
      ]);

      const translateResponse = await translatePolicy({
        session_id: summaryResponse.session_id,
        confirm: true,
      });

      setRepresentations((r) =>
        r ? [...r, translateResponse] : [translateResponse]
      );

      toast.success("Policy translated successfully.");
    } catch (error) {
      toast.error("Failed to translate policy.");
      setMessages((msgs) => msgs.slice(0, -1));
      return;
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const latest = representations.at(-1);

  return (
    <GlobalLayout>
      <div className="h-full flex">
        <ResizablePanelGroup
          direction="horizontal"
          className="h-full rounded-lg border md:min-w-[450px]"
        >
          <ResizablePanel defaultSize={50}>
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
                        ? "self-end bg-gray-200 dark:bg-gray-800 rounded-xl p-2 md:max-w-64 xl:max-w-xs 2xl:max-w-md"
                        : "self-start"
                    }`}
                  >
                    {msg.role === "user" ? (
                      <span className="w-fit rounded-3xl">{msg.content}</span>
                    ) : (
                      <div className="prose prose-invert max-w-none">
                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                      </div>
                    )}
                  </div>
                ))}
                {summarizing && (
                  <div className="space-y-2">
                    <Skeleton className="h-3 w-[250px]" />
                    <Skeleton className="h-3 w-[200px]" />
                    <Skeleton className="h-3 w-[150px]" />
                  </div>
                )}
                {translating && (
                  <div className="flex items-center gap-1.5">
                    Translating <Spinner />
                  </div>
                )}
                {latest && latest.configs && (
                  <div className="flex flex-col gap-1.5 mt-4">
                    <Label className="font-semibold">
                      Generated configurations:
                    </Label>

                    <div className="flex flex-col gap-1.5 ml-4">
                      {Object.entries(latest.configs).map(
                        ([vendor, config]) => (
                          <div key={vendor} className="flex flex-col gap-1">
                            <Label>{vendor}:</Label>
                            <pre className="relative whitespace-pre-wrap text-sm bg-muted p-2 rounded">
                              <CopyButton
                                text={config}
                                className="absolute top-2 right-2"
                              />
                              {config}
                            </pre>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}
              </div>
              <div className="flex flex-col">
                <div className="relative flex w-full">
                  <Textarea
                    value={summarizing ? "" : message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Ask your policy translation..."
                    className="w-full pb-12"
                    onKeyDown={handleKeyDown}
                  />
                  <div className="flex w-full justify-between absolute bottom-4 pl-1 pr-4">
                    <div className="flex items-center gap-2">
                      <AdditionDropdown
                        open={dropdownOpen}
                        setOpen={setDropdownOpen}
                      />
                      {context.filename && (
                        <span className="text-xs text-muted-foreground">
                          {context.filename}
                        </span>
                      )}
                    </div>
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
          {representations.length > 0 && (
            <ResizablePanel defaultSize={50}>
              <ResizablePanelGroup direction="vertical">
                <ResizablePanel defaultSize={100}>
                  <div className="flex h-full p-6 items-center justify-center">
                    {translating ? (
                      <div className="flex items-center gap-1.5">
                        <Spinner /> Translating policy...
                      </div>
                    ) : representations.length === 0 ? (
                      <Label>No flows generated yet.</Label>
                    ) : (
                      representations.map((rep) => (
                        <PipelineGraph
                          policyId={rep.policy_id}
                          resolverOutput={rep.resolver_output}
                          irOutput={rep.ir}
                          lintingWarnings={rep.linting_warnings}
                          safetyWarnings={rep.safety_warnings}
                          batfishWarnings={rep.batfish_warnings}
                          configs={rep.configs}
                        />
                      ))
                    )}
                  </div>
                </ResizablePanel>
              </ResizablePanelGroup>
            </ResizablePanel>
          )}
        </ResizablePanelGroup>
      </div>
    </GlobalLayout>
  );
}

export default Chat;
