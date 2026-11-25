import { useEffect, useState } from "react";
import { listServices, zones, zoneLabel } from "./api/services";
import type { Service, Zone } from "./api/services";

const categories = {
  social_assistance: "Assistência social",
  food: "Alimentação",
  shelter: "Acolhimento",
  mental_health: "Saúde mental",
};

function ServicesList({ zone }: { zone: Zone }) {
  const [state, setState] = useState<{
    items: Service[];
    status: "loading" | "ready" | "error";
  }>({ items: [], status: "loading" });
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000);
    let active = true;
    listServices(zone, controller.signal)
      .then((items) => {
        if (active) setState({ items, status: "ready" });
      })
      .catch(() => {
        if (active) setState({ items: [], status: "error" });
      });
    return () => {
      active = false;
      clearTimeout(timeout);
      controller.abort();
    };
  }, [zone, attempt]);
  return (
    <section
      className="catalog"
      aria-label={`Equipamentos — ${zoneLabel(zone)}`}
      aria-busy={state.status === "loading"}
    >
      <h3>Equipamentos</h3>
      {state.status === "loading" && (
        <p role="status">Carregando equipamentos…</p>
      )}
      {state.status === "error" && (
        <div role="alert">
          <p>Não foi possível carregar o catálogo.</p>
          <button
            type="button"
            onClick={() => {
              setState({ items: [], status: "loading" });
              setAttempt(attempt + 1);
            }}
          >
            Tentar novamente
          </button>
        </div>
      )}
      {state.status === "ready" && (
        <>
          <p role="status">{state.items.length} equipamentos nesta amostra</p>
          <ul className="service-list">
            {state.items.map((item) => (
              <li key={item.id}>
                <span className="tag">{categories[item.category]}</span>
                <h4>{item.name}</h4>
                <p>{item.address}</p>
                <details>
                  <summary>Descrição e fonte</summary>
                  <p>{item.description}</p>
                  <a
                    href={item.provenance.url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    Fonte oficial
                  </a>
                  <p>Conferência: {item.provenance.checked_on}</p>
                  {item.provenance.source_note && (
                    <p>{item.provenance.source_note}</p>
                  )}
                </details>
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  );
}

export default function ServicesPanel({
  zone,
  onChange,
  disabled,
}: {
  zone: Zone;
  onChange: (zone: Zone) => void;
  disabled: boolean;
}) {
  return (
    <aside className="services-panel" aria-labelledby="map-title">
      <p className="eyebrow">DEMONSTRAÇÃO</p>
      <h2 id="map-title">Localização simulada</h2>
      <p className="region">
        Selecione uma região para simular o GPS. Este desenho não representa
        limites geográficos.
      </p>
      <div className="zone-map" role="group" aria-label="Selecionar zona">
        {zones.map((item) => (
          <button
            className={`zone-button zone-${item.id}`}
            key={item.id}
            type="button"
            aria-pressed={zone === item.id}
            disabled={disabled}
            onClick={() => onChange(item.id)}
          >
            {item.label}
          </button>
        ))}
      </div>
      <p className="active-zone">
        Zona ativa: <strong>{zoneLabel(zone)}</strong>
      </p>
      <ServicesList key={zone} zone={zone} />
      <p className="map-footnote">
        Amostra acadêmica. Esta lista é carregada sem IA e permite conferir as
        respostas do chat. Nenhum GPS real é acessado.
      </p>
    </aside>
  );
}
