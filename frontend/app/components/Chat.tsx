"use client";

import { useCallback, useRef, useState } from "react";
import type { Message } from "@/lib/types";
import MessageList from "./MessageList";
import MessageComposer from "./MessageComposer";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const handleSend = useCallback(
    async (content: string) => {
      const userMsg: Message = { role: "user", content };
      const updated = [...messages, userMsg];
      setMessages(updated);
      setIsStreaming(true);

      const assistantMsg: Message = { role: "assistant", content: "" };
      setMessages([...updated, assistantMsg]);

      const controller = new AbortController();
      abortRef.current = controller;

      try {
        const resp = await fetch(`${API_URL}/api/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ messages: updated }),
          signal: controller.signal,
        });

        if (!resp.ok) {
          const err = await resp.text();
          setMessages((prev) => {
            const copy = [...prev];
            copy[copy.length - 1] = {
              role: "assistant",
              content: `Error: ${err}`,
            };
            return copy;
          });
          setIsStreaming(false);
          return;
        }

        const reader = resp.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
          setIsStreaming(false);
          return;
        }

        let buffer = "";
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n\n");
          buffer = lines.pop() ?? "";

          for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed.startsWith("data: ")) continue;
            const payload = trimmed.slice(6);
            if (payload === "[DONE]") break;

            try {
              const { token } = JSON.parse(payload);
              setMessages((prev) => {
                const copy = [...prev];
                const last = copy[copy.length - 1];
                copy[copy.length - 1] = {
                  ...last,
                  content: last.content + token,
                };
                return copy;
              });
            } catch {
              // skip malformed chunks
            }
          }
        }
      } catch (e) {
        if ((e as Error).name !== "AbortError") {
          setMessages((prev) => {
            const copy = [...prev];
            copy[copy.length - 1] = {
              role: "assistant",
              content: `Connection error: ${(e as Error).message}`,
            };
            return copy;
          });
        }
      } finally {
        setIsStreaming(false);
        abortRef.current = null;
      }
    },
    [messages],
  );

  const handleStop = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  return (
    <div className="flex flex-col h-screen max-w-3xl mx-auto">
      <header className="border-b border-gray-800 p-4 text-center">
        <h1 className="text-xl font-semibold">Hack Nation Chat</h1>
      </header>
      <MessageList messages={messages} />
      <MessageComposer
        onSend={handleSend}
        onStop={handleStop}
        isStreaming={isStreaming}
      />
    </div>
  );
}
