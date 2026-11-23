export type ChatMessage = { role: "user" | "assistant"; content: string };

export async function sendMessage(
  messages: ChatMessage[],
): Promise<ChatMessage> {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
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
  return { role: "assistant", content: data.message.content };
}
