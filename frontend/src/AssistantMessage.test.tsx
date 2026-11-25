import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, expect, it } from "vitest";
import AssistantMessage from "./AssistantMessage";

afterEach(cleanup);

it("renderiza negrito, quebra de linha, lista e link", () => {
  const { container } = render(
    <AssistantMessage
      content={
        "Opção: **CRAS Itaquera**.  \nRua Fontoura Xavier, 695.\n\n- Orientação\n- [Fonte](https://prefeitura.sp.gov.br)"
      }
    />,
  );
  expect(screen.getByText("CRAS Itaquera").tagName).toBe("STRONG");
  expect(container.querySelector("br")).toBeInTheDocument();
  expect(screen.getAllByRole("listitem")).toHaveLength(2);
  expect(screen.getByRole("link", { name: "Fonte" })).toHaveAttribute(
    "rel",
    "noopener noreferrer",
  );
});

it("não permite HTML, imagens remotas ou links javascript", () => {
  const { container } = render(
    <AssistantMessage
      content={
        '<script>alert(1)</script>\n\n<img src="https://example.com/tracker">\n\n![imagem](https://example.com/tracker)\n\n[Perigoso](javascript:alert%281%29)'
      }
    />,
  );
  expect(container.querySelector("script")).toBeNull();
  expect(container.querySelector("img")).toBeNull();
  expect(screen.queryByRole("link")).not.toBeInTheDocument();
});
