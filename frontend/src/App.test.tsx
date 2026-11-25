import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, expect, it, vi } from "vitest";
import App from "./App";

it("mostra o aviso de simulação", async () => {
  mockApi();
  render(<App />);
  expect(screen.getByLabelText("Aviso de simulação")).toHaveTextContent(
    "Não realiza ligações nem aciona serviços",
  );
  await screen.findByText("API conectada");
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

function mockApi(fail = false, alert = false) {
  Element.prototype.scrollIntoView = vi.fn();
  const fetchMock = vi.fn(async (url: string, options?: RequestInit) => {
    if (url === "/api/health")
      return new Response(JSON.stringify({ status: "ok" }));
    if (url.startsWith("/api/services")) {
      const zone = new URL(url, "http://localhost").searchParams.get("zone");
      return new Response(
        JSON.stringify({
          zone,
          services: [
            {
              id: `${zone}-01`,
              name: `Equipamento ${zone}`,
              zone,
              address: "Rua de teste, 10",
              description: "Registro simulado para teste",
              category: "food",
              provenance: {
                url: "https://prefeitura.sp.gov.br/",
                checked_on: "2026-11-24",
              },
            },
          ],
        }),
      );
    }
    if (fail) throw new Error("offline");
    const request = JSON.parse(options?.body as string) as {
      messages: { content: string }[];
    };
    return new Response(
      JSON.stringify({
        mode: "echo",
        urgency:
          alert && request.messages.length === 1
            ? {
                detected: true,
                category: "medical",
                contact_ids: ["samu"],
                contacts: [
                  {
                    id: "samu",
                    name: "SAMU",
                    phone: "192",
                    purpose: "Urgência médica.",
                  },
                ],
              }
            : {
                detected: false,
                category: null,
                contact_ids: [],
                contacts: [],
              },
        message: {
          role: "assistant",
          content: `Você disse: ${request.messages.at(-1)?.content}`,
        },
      }),
    );
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

it("envia com Enter e mantém Shift+Enter para quebra de linha", async () => {
  const fetchMock = mockApi();
  const user = userEvent.setup();
  render(<App />);
  const input = screen.getByLabelText(/Sua mensagem/);
  await user.type(input, "Preciso de apoio");
  await user.keyboard("{Shift>}{Enter}{/Shift}na zona leste");
  expect(input).toHaveValue("Preciso de apoio\nna zona leste");
  expect(
    fetchMock.mock.calls.filter(([url]) => url === "/api/chat"),
  ).toHaveLength(0);
  await user.keyboard("{Enter}");
  await screen.findByText(/Você disse: Preciso de apoio/);
  const calls = fetchMock.mock.calls.filter(([url]) => url === "/api/chat");
  expect(calls).toHaveLength(1);
  expect(JSON.parse(calls[0][1]?.body as string).messages[0].content).toBe(
    "Preciso de apoio\nna zona leste",
  );
  expect(input).toHaveValue("");
});

it("envia o histórico completo no segundo turno e limpa a conversa", async () => {
  const fetchMock = mockApi();
  const user = userEvent.setup();
  render(<App />);
  await user.type(screen.getByLabelText(/Sua mensagem/), "Estou em Itaquera");
  await user.click(screen.getByRole("button", { name: "Enviar" }));
  await screen.findByText("Você disse: Estou em Itaquera");
  await user.type(screen.getByLabelText(/Sua mensagem/), "Busco um CRAS");
  await user.click(screen.getByRole("button", { name: "Enviar" }));
  await screen.findByText("Você disse: Busco um CRAS");
  const calls = fetchMock.mock.calls.filter(([url]) => url === "/api/chat");
  expect(JSON.parse(calls[1][1]?.body as string).messages).toEqual([
    { role: "user", content: "Estou em Itaquera" },
    { role: "assistant", content: "Você disse: Estou em Itaquera" },
    { role: "user", content: "Busco um CRAS" },
  ]);
  await user.click(screen.getByRole("button", { name: "Nova conversa" }));
  expect(
    screen.queryByText("Você disse: Busco um CRAS"),
  ).not.toBeInTheDocument();
});

it("mantém rascunho quando a API falha e permite tentar novamente", async () => {
  mockApi(true);
  const user = userEvent.setup();
  render(<App />);
  await user.click(screen.getByRole("button", { name: "Buscar um CRAS" }));
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "Sua mensagem foi mantida",
  );
  expect(screen.getByLabelText(/Sua mensagem/)).toHaveValue("Buscar um CRAS");
  expect(screen.getByRole("button", { name: "Enviar" })).toBeEnabled();
});

it("mantém atalhos após a resposta e envia Estou com frio ao clicar", async () => {
  const fetchMock = mockApi();
  const user = userEvent.setup();
  render(<App />);
  await user.click(
    screen.getByRole("button", { name: "Encontrar alimentação" }),
  );
  await screen.findByText("Você disse: Encontrar alimentação");
  for (const name of [
    "Encontrar alimentação",
    "Buscar um CRAS",
    "Conhecer opções de acolhimento",
    "Estou com frio",
  ]) {
    expect(screen.getByRole("button", { name })).toBeVisible();
  }
  await user.click(screen.getByRole("button", { name: "Estou com frio" }));
  await screen.findByText("Você disse: Estou com frio");
  expect(
    fetchMock.mock.calls.filter(([url]) => url === "/api/chat"),
  ).toHaveLength(2);
});

it("troca a lista e envia a zona atual com o histórico preservado", async () => {
  const fetchMock = mockApi();
  const user = userEvent.setup();
  render(<App />);
  await screen.findByText("Equipamento leste");
  await user.type(screen.getByLabelText(/Sua mensagem/), "Olá");
  await user.click(screen.getByRole("button", { name: "Enviar" }));
  await screen.findByText("Você disse: Olá");
  await user.click(screen.getByRole("button", { name: "Zona Norte" }));
  await screen.findByText("Equipamento norte");
  expect(screen.queryByText("Equipamento leste")).not.toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Zona Norte" })).toHaveAttribute(
    "aria-pressed",
    "true",
  );
  await user.type(screen.getByLabelText(/Sua mensagem/), "Preciso de comida");
  await user.click(screen.getByRole("button", { name: "Enviar" }));
  await screen.findByText("Você disse: Preciso de comida");
  const calls = fetchMock.mock.calls.filter(([url]) => url === "/api/chat");
  const payload = JSON.parse(calls[1][1]?.body as string);
  expect(payload.zone).toBe("norte");
  expect(payload.messages).toHaveLength(3);
});

it("mantém o alerta entre turnos e permite dispensar", async () => {
  mockApi(false, true);
  const user = userEvent.setup();
  render(<App />);
  await user.type(screen.getByLabelText(/Sua mensagem/), "Cenário de teste");
  await user.click(screen.getByRole("button", { name: "Enviar" }));
  await screen.findByText("Possível urgência identificada");
  expect(screen.getByRole("link", { name: "SAMU · 192" })).toHaveAttribute(
    "href",
    "tel:192",
  );
  expect(
    screen.getByRole("heading", { name: /Como .* ajudar/ }).closest("section"),
  ).toHaveClass("urgency-active");
  await user.type(screen.getByLabelText(/Sua mensagem/), "Outro turno");
  await user.click(screen.getByRole("button", { name: "Enviar" }));
  await screen.findByText("Você disse: Outro turno");
  expect(
    screen.getByText("Possível urgência identificada"),
  ).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "Dispensar aviso" }));
  expect(
    screen.queryByText("Possível urgência identificada"),
  ).not.toBeInTheDocument();
});

it("limpa a sinalização ao iniciar nova conversa", async () => {
  mockApi(false, true);
  const user = userEvent.setup();
  render(<App />);
  await user.type(screen.getByLabelText(/Sua mensagem/), "Cenário de teste");
  await user.click(screen.getByRole("button", { name: "Enviar" }));
  await screen.findByText("Possível urgência identificada");
  await user.click(screen.getByRole("button", { name: "Nova conversa" }));
  expect(
    screen.queryByText("Possível urgência identificada"),
  ).not.toBeInTheDocument();
  expect(
    screen.getByRole("heading", { name: /Como .* ajudar/ }).closest("section"),
  ).not.toHaveClass("urgency-active");
});
