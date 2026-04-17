"use client";

import { useState } from "react";
import type { Settings } from "@/lib/types";

const PROVIDER_DEFAULTS: Record<string, string> = {
  gemini: "gemini-2.0-flash",
  openai: "gpt-4o-mini",
};

interface Props {
  settings: Settings;
  onSave: (s: Settings) => void;
}

export default function SettingsPanel({ settings, onSave }: Props) {
  const [draft, setDraft] = useState<Settings>(settings);
  const [showKey, setShowKey] = useState(false);

  return (
    <div className="border-b border-gray-800 bg-gray-900 px-4 py-3 flex flex-wrap gap-3 items-end">
      <div className="flex flex-col gap-1">
        <label className="text-xs text-gray-400">Provider</label>
        <select
          className="bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-sm"
          value={draft.provider}
          onChange={(e) =>
            setDraft({ ...draft, provider: e.target.value as Settings["provider"] })
          }
        >
          <option value="gemini">Gemini</option>
          <option value="openai">OpenAI</option>
        </select>
      </div>

      <div className="flex flex-col gap-1 flex-1 min-w-48">
        <label className="text-xs text-gray-400">API Key</label>
        <div className="flex">
          <input
            type={showKey ? "text" : "password"}
            className="flex-1 bg-gray-800 border border-gray-700 rounded-l px-2 py-1.5 text-sm"
            placeholder="Paste your API key…"
            value={draft.apiKey}
            onChange={(e) => setDraft({ ...draft, apiKey: e.target.value })}
          />
          <button
            className="bg-gray-700 border border-l-0 border-gray-700 rounded-r px-2 text-xs text-gray-400 hover:text-gray-200"
            onClick={() => setShowKey(!showKey)}
          >
            {showKey ? "Hide" : "Show"}
          </button>
        </div>
      </div>

      <div className="flex flex-col gap-1 w-44">
        <label className="text-xs text-gray-400">Model (optional)</label>
        <input
          type="text"
          className="bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-sm"
          placeholder={PROVIDER_DEFAULTS[draft.provider]}
          value={draft.model}
          onChange={(e) => setDraft({ ...draft, model: e.target.value })}
        />
      </div>

      <button
        className="bg-blue-600 hover:bg-blue-500 text-white rounded px-3 py-1.5 text-sm"
        onClick={() => onSave(draft)}
      >
        Save
      </button>
    </div>
  );
}
