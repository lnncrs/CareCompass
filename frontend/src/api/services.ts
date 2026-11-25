export const zones = [
  { id: "norte", label: "Zona Norte" },
  { id: "oeste", label: "Zona Oeste" },
  { id: "centro", label: "Centro" },
  { id: "leste", label: "Zona Leste" },
  { id: "sul", label: "Zona Sul" },
] as const;
export type Zone = (typeof zones)[number]["id"];
export const zoneLabel = (zone: Zone) =>
  zones.find((item) => item.id === zone)!.label;

export type Service = {
  id: string;
  name: string;
  zone: Zone;
  address: string;
  description: string;
  category: "food" | "shelter" | "mental_health" | "social_assistance";
  provenance: { url: string; checked_on: string; source_note?: string | null };
};

export async function listServices(
  zone: Zone,
  signal: AbortSignal,
): Promise<Service[]> {
  const response = await fetch(`/api/services?zone=${zone}`, { signal });
  if (!response.ok) throw new Error("Catálogo indisponível");
  const data = (await response.json()) as { zone: unknown; services: unknown };
  if (
    data.zone !== zone ||
    !Array.isArray(data.services) ||
    !data.services.every(
      (item: Service) =>
        item &&
        item.zone === zone &&
        typeof item.id === "string" &&
        typeof item.name === "string" &&
        typeof item.address === "string" &&
        typeof item.description === "string" &&
        typeof item.provenance?.url === "string" &&
        ["food", "shelter", "mental_health", "social_assistance"].includes(
          item.category,
        ),
    )
  )
    throw new Error("Catálogo inválido");
  return data.services;
}
