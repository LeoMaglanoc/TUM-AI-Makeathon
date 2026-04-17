export type Role = "user" | "assistant";

export interface Message {
  role: Role;
  content: string;
}

export interface Settings {
  provider: "gemini" | "openai";
  apiKey: string;
  model: string;
}

export const DEFAULT_SETTINGS: Settings = {
  provider: "gemini",
  apiKey: "",
  model: "",
};
