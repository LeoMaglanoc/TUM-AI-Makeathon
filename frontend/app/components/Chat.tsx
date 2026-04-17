"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { Message, Settings } from "@/lib/types";
import { DEFAULT_SETTINGS } from "@/lib/types";
import MessageList from "./MessageList";
import MessageComposer from "./MessageComposer";
import SettingsPanel from "./SettingsPanel";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const SETTINGS_KEY = "tumai-settings";

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useState<Settings>(DEFAULT_SETTINGS);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    try {
      const stored = localStorage.getItem(SETTINGS_KEY);
      if (stored) setSettings(JSON.parse(stored));
    } catch {
      // ignore parse errors
    }
  }, []);

  const handleSaveSettings = useCallback((s: Settings) => {
    setSettings(s);
    try {
      localStorage.setItem(SETTINGS_KEY, JSON.stringify(s));
    } catch {
      // ignore storage errors
    }
    setShowSettings(false);
  }, []);

  const handleSend = useCallback(
    async (content: string) => {
      if (!settings.apiKey) return;

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
          body: JSON.stringify({
            messages: updated,
            api_key: settings.apiKey,
            provider: settings.provider,
            model: settings.model || null,
          }),
          signal: controller.signal,
        });

        if (!resp.ok) {
          const err = await resp.text();
          setMessages((prev) => {
            const copy = [...prev];
            copy[copy.length - 1] = { role: "assistant", content: `Error: ${err}` };
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
              const parsed = JSON.parse(payload);
              if (parsed.error) {
                setMessages((prev) => {
                  const copy = [...prev];
                  copy[copy.length - 1] = {
                    role: "assistant",
                    content: `Error: ${parsed.error}`,
                  };
                  return copy;
                });
                break;
              }
              if (parsed.token) {
                setMessages((prev) => {
                  const copy = [...prev];
                  const last = copy[copy.length - 1];
                  copy[copy.length - 1] = { ...last, content: last.content + parsed.token };
                  return copy;
                });
              }
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
    [messages, settings],
  );

  const handleStop = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  return (
    <div className="flex flex-col h-screen max-w-3xl mx-auto">
      <header className="border-b border-gray-800 p-4 flex items-center justify-between">
        <h1 className="text-xl font-semibold">TUM.AI Makeathon</h1>
        <button
          onClick={() => setShowSettings(!showSettings)}
          className="text-gray-400 hover:text-gray-200 p-1 rounded"
          aria-label="Settings"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
            />
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
            />
          </svg>
        </button>
      </header>

      {showSettings && <SettingsPanel settings={settings} onSave={handleSaveSettings} />}

      {!settings.apiKey && !showSettings && (
        <div className="bg-yellow-900/40 border-b border-yellow-800 px-4 py-2 text-sm text-yellow-300">
          Enter your API key in ⚙ Settings to start chatting.
        </div>
      )}

      <MessageList messages={messages} />
      <MessageComposer
        onSend={handleSend}
        onStop={handleStop}
        isStreaming={isStreaming}
        disabled={!settings.apiKey}
      />
    </div>
  );
}
