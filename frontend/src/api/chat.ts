import type { Zone } from "./services";
export type ChatMessage = { role: "user" | "assistant"; content: string };
export type SupportContact = {
  id: string;
  name: string;
  phone: string;
  purpose: string;
};
export type Urgency = {
  detected: boolean;
  category: string | null;
  contact_ids: string[];
  contacts: SupportContact[];
};
export type ChatReply = { message: ChatMessage; urgency: Urgency };
export const noUrgency: Urgency = {
  detected: false,
  category: null,
  contact_ids: [],
  contacts: [],
};

export async function sendMessage(
  messages: ChatMessage[],
  zone: Zone,
): Promise<ChatReply> {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages, zone }),
    signal: AbortSignal.timeout(20000),
  });
  if (!response.ok) throw new Error("Não foi possível enviar sua mensagem.");
  const data: unknown = await response.json();
  if (
    typeof data !== "object" ||
    data === null ||
    !("message" in data) ||
    typeof data.message !== "object" ||
    data.message === null ||
    !("role" in data.message) ||
    data.message.role !== "assistant" ||
    !("content" in data.message) ||
    typeof data.message.content !== "string"
  )
    throw new Error("A resposta recebida não pôde ser lida.");
  let urgency = noUrgency;
  if ("urgency" in data) {
    const value = data.urgency;
    if (
      typeof value !== "object" ||
      value === null ||
      !("detected" in value) ||
      typeof value.detected !== "boolean" ||
      !("contacts" in value) ||
      !Array.isArray(value.contacts) ||
      !value.contacts.every(
        (item: SupportContact) =>
          item &&
          typeof item.id === "string" &&
          typeof item.name === "string" &&
          typeof item.purpose === "string" &&
          /^\d{3}$/.test(item.phone),
      ) ||
      !("category" in value) ||
      (value.category !== null && typeof value.category !== "string") ||
      !("contact_ids" in value) ||
      !Array.isArray(value.contact_ids) ||
      !value.contact_ids.every((id) => typeof id === "string")
    ) {
      throw new Error("Sinalização de urgência inválida.");
    }
    urgency = {
      detected: value.detected,
      category: value.category,
      contact_ids: value.contact_ids,
      contacts: value.contacts,
    };
  }
  return {
    message: { role: "assistant", content: data.message.content },
    urgency,
  };
}
