import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { sendMessage } from "./api/chat";
import type { ChatMessage } from "./api/chat";
import "./App.css";

const suggestions = [
  "Encontrar alimentação",
  "Buscar um CRAS",
  "Conhecer opções de acolhimento",
];

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const [health, setHealth] = useState("Verificando conexão");
  const end = useRef<HTMLDivElement>(null);
  const input = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const controller = new AbortController();
    fetch("/api/health", { signal: controller.signal })
      .then(async (response) => {
        if (!response.ok) throw new Error();
        const data = (await response.json()) as { status?: string };
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
    const text = draft.trim();
    if (!text || sending) return;
    // Só confirma o turno no histórico quando o envio completa; falhas preservam o rascunho.
    const next: ChatMessage[] = [...messages, { role: "user", content: text }];
    setSending(true);
    setError("");
    try {
      const reply = await sendMessage(next);
      setMessages([...next, reply]);
      setDraft("");
      setHealth("API conectada");
    } catch {
      setError(
        "Não foi possível enviar. Confira se o backend está iniciado e tente novamente. Sua mensagem foi mantida.",
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
            Care Compass<small>Um caminho para encontrar apoio</small>
          </span>
        </a>
        <span className="academic-label">
          UFABC <span aria-hidden="true">/</span> Projeto de PLN
        </span>
      </header>
      <main id="main" className="workspace">
        <section className="chat-panel" aria-labelledby="chat-title">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">ESCUTA E ORIENTAÇÃO</p>
              <h1 id="chat-title">Como podemos ajudar?</h1>
            </div>
            <span className="connection" role="status">
              {health}
            </span>
          </div>
          <div className="demo-notice">
            <strong>Protótipo · modo de eco</strong>
            <span>
              Nesta versão, o chat apenas repete sua mensagem. A busca por
              serviços ainda não está disponível.
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
                <h2>O primeiro passo é conversar.</h2>
                <p>
                  A proposta do Care Compass é ajudar você a encontrar serviços
                  públicos em São Paulo, começando pela Zona Leste.
                </p>
                <p className="welcome-hint">
                  Escolha um exemplo ou escreva uma mensagem para testar.
                </p>
                <div className="suggestions">
                  {suggestions.map((text) => (
                    <button
                      key={text}
                      type="button"
                      disabled={sending}
                      onClick={() => {
                        setDraft(text);
                        input.current?.focus();
                      }}
                    >
                      {text}
                    </button>
                  ))}
                </div>
              </div>
            )}
            {messages.map((message, index) => (
              <div className={`message ${message.role}`} key={index}>
                <span className="message-author">
                  {message.role === "user" ? "Você" : "Care Compass · eco"}
                </span>
                <p>{message.content}</p>
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
          <form className="composer" onSubmit={submit}>
            <label htmlFor="message">Sua mensagem</label>
            <div className="input-row">
              <textarea
                ref={input}
                id="message"
                placeholder="Escreva aqui o que você precisa…"
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
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
                : "Até 4.000 caracteres. Evite informar dados pessoais neste teste."}
            </p>
          </form>
          <div className="chat-footer">
            <span>A conversa fica apenas nesta sessão.</span>
            <button
              type="button"
              disabled={sending || (!messages.length && !draft)}
              onClick={() => {
                setMessages([]);
                setDraft("");
                setError("");
                input.current?.focus();
              }}
            >
              Nova conversa
            </button>
          </div>
        </section>
        <aside className="services-panel" aria-labelledby="map-title">
          <div>
            <p className="eyebrow">PERTO DE VOCÊ</p>
            <h2 id="map-title">Serviços no mapa</h2>
            <p className="region">São Paulo · piloto na Zona Leste</p>
          </div>
          <div className="map-placeholder">
            <div className="map-grid" aria-hidden="true">
              <span>⌖</span>
            </div>
            <div className="map-copy">
              <span className="tag">Em breve</span>
              <h3>Apoio no seu caminho</h3>
              <p>
                Os serviços encontrados aparecerão aqui, com endereço e fonte
                oficial.
              </p>
            </div>
          </div>
          <div className="next-step">
            <h3>Você escolhe o que compartilhar</h3>
            <p>
              Na próxima etapa, você poderá informar uma região para buscar
              serviços. Sua localização não é solicitada nesta versão.
            </p>
          </div>
          <p className="map-footnote">
            Área reservada para o mapa. Nenhum serviço está sendo exibido.
          </p>
        </aside>
      </main>
      <footer className="site-footer">
        <span>Care Compass · Tecnologia a serviço do cuidado</span>
        <span>Protótipo acadêmico · 2026</span>
      </footer>
    </div>
  );
}
