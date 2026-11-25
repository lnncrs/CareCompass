import { act, cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, expect, it, vi } from "vitest";
import ServicesPanel from "./ServicesPanel";
import * as api from "./api/services";
import type { Service } from "./api/services";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

it("ignora resposta antiga depois de trocar a zona", async () => {
  let finishOld: (items: Service[]) => void = () => {};
  vi.spyOn(api, "listServices").mockImplementation((zone) =>
    zone === "leste"
      ? new Promise((resolve) => {
          finishOld = resolve;
        })
      : Promise.resolve([]),
  );
  const view = render(
    <ServicesPanel zone="leste" onChange={() => {}} disabled={false} />,
  );
  view.rerender(
    <ServicesPanel zone="norte" onChange={() => {}} disabled={false} />,
  );
  await screen.findByText("0 equipamentos nesta amostra");
  await act(async () => {
    finishOld([
      {
        id: "old",
        zone: "leste",
        name: "Resposta antiga",
        category: "food",
        address: "Endereço antigo",
        description: "",
        provenance: {
          url: "https://prefeitura.sp.gov.br",
          checked_on: "2026-11-24",
        },
      },
    ]);
  });
  expect(screen.queryByText("Resposta antiga")).not.toBeInTheDocument();
});

it("permite tentar novamente após falha da listagem", async () => {
  vi.spyOn(api, "listServices")
    .mockRejectedValueOnce(new Error("offline"))
    .mockResolvedValueOnce([]);
  const user = userEvent.setup();
  render(<ServicesPanel zone="leste" onChange={() => {}} disabled={false} />);
  await screen.findByRole("alert");
  await user.click(screen.getByRole("button", { name: "Tentar novamente" }));
  await screen.findByText("0 equipamentos nesta amostra");
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
});
