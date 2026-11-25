import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { noUrgency, sendMessage } from "./api/chat";
import type { ChatMessage, Urgency } from "./api/chat";
import ServicesPanel from "./ServicesPanel";
import AssistantMessage from "./AssistantMessage";
import type { Zone } from "./api/services";
import "./App.css";

const suggestions = [
  "Encontrar alimentação",
  "Buscar um CRAS",
  "Conhecer opções de acolhimento",
  "Estou com frio",
];

export default function App() {
  const [zone, setZone] = useState<Zone>("leste");
  const [urgency, setUrgency] = useState<Urgency>(noUrgency);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const [mode, setMode] = useState<"echo" | "langgraph">("echo");
  const [health, setHealth] = useState("Verificando conexão");
  const end = useRef<HTMLDivElement>(null);
  const input = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const controller = new AbortController();
    fetch("/api/health", { signal: controller.signal })
      .then(async (response) => {
        if (!response.ok) throw new Error();
        const data = (await response.json()) as {
          status?: string;
          mode?: string;
        };
        setMode(data.mode === "langgraph" ? "langgraph" : "echo");
        setHealth(data.status === "ok" ? "API conectada" : "API indisponível");
      })
      .catch(() => {
        if (!controller.signal.aborted) setHealth("API indisponível");
      });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    end.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [messages, sending]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    await send(draft);
  }

  async function send(value: string) {
    const text = value.trim();
    if (!text || sending || messages.length >= 98) return;
    setDraft(text);
    // Só confirma o turno no histórico quando o envio completa; falhas preservam o rascunho.
    const next: ChatMessage[] = [...messages, { role: "user", content: text }];
    setSending(true);
    setError("");
    try {
      const reply = await sendMessage(next, zone);
      setMessages([...next, reply.message]);
      if (reply.urgency.detected) {
        setUrgency((previous) => ({
          ...reply.urgency,
          contacts: [
            ...new Map(
              [...previous.contacts, ...reply.urgency.contacts].map((item) => [
                item.id,
                item,
              ]),
            ).values(),
          ],
        }));
      }
      setDraft("");
      setHealth("API conectada");
    } catch {
      setError(
        "Não foi possível obter a resposta. Confira a conexão e tente novamente. Sua mensagem foi mantida.",
      );
    } finally {
      setSending(false);
      input.current?.focus();
    }
  }

  return (
    <div className="app-shell">
      <header className="top-bar">
        <a className="brand" href="#main">
          <span className="brand-mark" aria-hidden="true">
            ✳
          </span>
          <span>
            Encontre Apoio<small>Alimentação, acolhimento e cuidado</small>
          </span>
        </a>
        <span className="academic-label">
          UFABC <span aria-hidden="true">/</span> 2026
        </span>
      </header>
      <main id="main" className="workspace">
        <aside className="simulation-banner" aria-label="Aviso de simulação">
          <strong>Simulação</strong>
          <span>
            Não realiza ligações nem aciona serviços. Use apenas situações e
            dados fictícios.
          </span>
        </aside>
        <section
          className={`chat-panel${urgency.detected ? " urgency-active" : ""}`}
          aria-labelledby="chat-title"
        >
          <div className="panel-heading">
            <div>
              <p className="eyebrow">ORIENTAÇÃO</p>
              <h1 id="chat-title">Como posso ajudar?</h1>
            </div>
            <span className="connection" role="status">
              {health}
            </span>
          </div>
          {urgency.detected && (
            <div className="urgency-notice" role="alert">
              <strong>Possível urgência identificada</strong>
              <p>
                Sinalização do protótipo, sujeita a erro. Nenhum serviço foi
                acionado.
              </p>
              <ul>
                {urgency.contacts.map((contact) => (
                  <li key={contact.id}>
                    <a href={`tel:${contact.phone}`}>
                      {contact.name} · {contact.phone}
                    </a>
                    <span>{contact.purpose}</span>
                  </li>
                ))}
              </ul>
              <button type="button" onClick={() => setUrgency(noUrgency)}>
                Dispensar aviso
              </button>
            </div>
          )}
          <div className="demo-notice">
            <strong>
              {mode === "echo"
                ? "Protótipo · modo eco"
                : "Protótipo · modo assistente"}
            </strong>
            <span>
              {mode === "echo"
                ? "O modo eco repete sua mensagem. A lista lateral consulta o catálogo de equipamentos publicos."
                : "O modo assistente consulta a amostra de equipamentos na zona selecionada. Demonstração acadêmica, sem disponibilidade em tempo real."}
            </span>
          </div>
          <div
            className="conversation"
            role="log"
            aria-label="Conversa"
            aria-live="polite"
            aria-busy={sending}
          >
            {messages.length === 0 && (
              <div className="welcome">
                <span className="welcome-icon" aria-hidden="true">
                  ✳
                </span>
                <h2>Encontre o apoio que você precisa.</h2>
                <p>
                  Encontre opções de alimentação, acolhimento e cuidado em São
                  Paulo. Selecione sua região e conte o que você precisa.
                </p>
                <p className="welcome-hint">
                  Escolha um exemplo ou escreva uma mensagem para testar.
                </p>
              </div>
            )}
            {messages.map((message, index) => (
              <div className={`message ${message.role}`} key={index}>
                <span className="message-author">
                  {message.role === "user"
                    ? "Você"
                    : mode === "echo"
                      ? "Encontre Apoio · eco"
                      : "Encontre Apoio"}
                </span>
                {message.role === "assistant" ? (
                  <AssistantMessage content={message.content} />
                ) : (
                  <p>{message.content}</p>
                )}
              </div>
            ))}
            {sending && (
              <p className="sending" role="status">
                Enviando sua mensagem…
              </p>
            )}
            <div ref={end} />
          </div>
          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}
          <div
            className="suggestions persistent-suggestions"
            role="group"
            aria-label="Atalhos de mensagem"
          >
            {suggestions.map((text) => (
              <button
                key={text}
                type="button"
                disabled={sending || messages.length >= 98}
                onClick={() => void send(text)}
              >
                {text}
              </button>
            ))}
          </div>
          <form className="composer" onSubmit={submit}>
            <label htmlFor="message">Sua mensagem</label>
            <div className="input-row">
              <textarea
                ref={input}
                id="message"
                placeholder="Escreva aqui o que você precisa…"
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                onKeyDown={(event) => {
                  if (
                    event.key === "Enter" &&
                    !event.shiftKey &&
                    !event.nativeEvent.isComposing &&
                    event.nativeEvent.keyCode !== 229
                  ) {
                    event.preventDefault();
                    if (!event.repeat) void send(draft);
                  }
                }}
                maxLength={4000}
                rows={2}
                readOnly={sending}
                aria-describedby="message-help"
              />
              <button
                className="send"
                type="submit"
                disabled={sending || !draft.trim() || messages.length >= 98}
              >
                {sending ? "Enviando…" : "Enviar"}
              </button>
            </div>
            <p id="message-help">
              {messages.length >= 98
                ? "Limite desta demonstração atingido. Use “Nova conversa” para continuar."
                : "Enter envia · Shift+Enter quebra a linha. Até 4.000 caracteres. Use dados fictícios."}
            </p>
          </form>
          <div className="chat-footer">
            <span>A conversa fica apenas nesta sessão.</span>
            <button
              type="button"
              disabled={sending || (!messages.length && !draft)}
              onClick={() => {
                setMessages([]);
                setUrgency(noUrgency);
                setDraft("");
                setError("");
                input.current?.focus();
              }}
            >
              Nova conversa
            </button>
          </div>
        </section>
        <ServicesPanel zone={zone} onChange={setZone} disabled={sending} />
      </main>
      <footer className="site-footer">
        <span>Encontre Apoio</span>
        <span>Protótipo acadêmico / CMCC @ UFABC 2026 / MCZA017-13SA</span>
      </footer>
    </div>
  );
}
