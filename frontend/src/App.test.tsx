import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, expect, it, vi } from "vitest";
import App from "./App";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

function mockApi(fail = false) {
  Element.prototype.scrollIntoView = vi.fn();
  const fetchMock = vi.fn(async (url: string, options?: RequestInit) => {
    if (url === "/api/health")
      return new Response(JSON.stringify({ status: "ok" }));
    if (fail) throw new Error("offline");
    const request = JSON.parse(options?.body as string) as {
      messages: { content: string }[];
    };
    return new Response(
      JSON.stringify({
        mode: "echo",
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

it("envia o histórico completo no segundo turno e limpa a conversa", async () => {
  const fetchMock = mockApi();
  const user = userEvent.setup();
  render(<App />);
  await user.type(screen.getByLabelText("Sua mensagem"), "Estou em Itaquera");
  await user.click(screen.getByRole("button", { name: "Enviar" }));
  await screen.findByText("Você disse: Estou em Itaquera");
  await user.type(screen.getByLabelText("Sua mensagem"), "Busco um CRAS");
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
  await user.click(screen.getByRole("button", { name: "Enviar" }));
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "Sua mensagem foi mantida",
  );
  expect(screen.getByLabelText("Sua mensagem")).toHaveValue("Buscar um CRAS");
  expect(screen.getByRole("button", { name: "Enviar" })).toBeEnabled();
});
