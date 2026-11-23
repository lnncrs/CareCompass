# Care Compass

**Um caminho para encontrar apoio em serviços oficiais da cidade de São Paulo.**

![UFABC Logo](assets/logotipo-ufabc-extenso.png)

Universidade Federal do ABC - Bacharelado em Ciência e Tecnologia<br />
Processamento de Linguagem Natural<br />

Lenin Cristi - RA 21030114

## Resumo

O Care Compass propõe um chat para ajudar pessoas em vulnerabilidade a encontrar
alimentação, acolhimento, CRAS, CREAS, Centro POP e saúde mental, começando pela
Zona Leste de São Paulo. A proposta prioriza linguagem simples, respostas curtas,
contexto da conversa e localização, com serviços apresentados em um mapa.

**Estado atual: fase estrutural, com chat de eco.** O sistema repete a mensagem
enviada para validar frontend e backend. Ainda não consulta serviços, não solicita
localização e não utiliza IA. O mapa é um espaço reservado no desktop.

## Início rápido

Pré-requisitos: Python 3.13+, uv e Node.js 24 LTS com npm.
Execute os comandos a partir desta pasta, em dois terminais.

### Backend

```powershell
cd backend
uv sync --locked
Copy-Item .env.example .env
uv run uvicorn app.main:app --reload --host 127.0.0.1
```

Copie o `.env` apenas no primeiro uso. A configuração padrão funciona sem ele.
API em <http://127.0.0.1:8000/api/health> e documentação em
<http://127.0.0.1:8000/docs>. Nenhuma credencial é necessária nesta fase.

### Frontend

```powershell
cd frontend
npm ci
npm run dev
```

Abra o endereço local exibido pelo Vite, normalmente <http://127.0.0.1:5173>.
Envie uma mensagem para receber “Você disse: …”. A conversa fica em memória
nesta aba e é apagada ao recarregar ou selecionar “Nova conversa”.
O proxy do Vite encaminha `/api` ao backend na porta 8000.

## Estrutura do projeto

```text
├── backend/                  # FastAPI, configuração, contrato de chat e testes
│   ├── src/app/
│   ├── tests/
│   ├── pyproject.toml
│   └── uv.lock
├── frontend/                 # React, TypeScript, Vite e testes de interface
│   ├── src/
│   └── package.json
├── docs/                     # Produto, arquitetura e plano de execução
├── third-party/              # Avisos de licença de arquivos reaproveitados
├── AGENTS.md                 # Orientações para trabalhar no repositório
└── LICENSE
```

## Verificação

Em `backend/`:

```powershell
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
```

Em `frontend/`:

```powershell
npm run format:check
npm run lint
npm run typecheck
npm run test
npm run build
```

O build gera arquivos estáticos; `vite preview` não fornece o proxy de API
de desenvolvimento. Para testar o chat local, use `npm run dev` com o backend ativo.

## Metodologia e próximos passos

A base usa FastAPI + React/TypeScript, inspirada no SampleCodex. A próxima etapa
prioriza LangGraph com integrações LangChain e modelo no Microsoft Foundry,
catálogo revisado e recuperação de orientações oficiais. Voz e Microsoft Agent
Framework são adicionais. Busca será independente do motor de execução.

Veja a [especificação](docs/product-spec.md), a [arquitetura](docs/architecture.md)
e o [plano de execução](docs/implementation-plan.md). A avaliação de PLN e seus
resultados serão registrados nas próximas fases; ainda não há métricas de IA.

O trabalho é somente local. Configurações e dependências foram reaproveitadas
seletivamente do SampleCodex; sua licença está preservada em
[third-party/SampleCodex-LICENSE](third-party/SampleCodex-LICENSE).

## Licença

O código deste projeto é disponibilizado sob a [PolyForm Noncommercial License 1.0.0](LICENSE), que permite os usos não comerciais e os demais usos expressamente previstos em seus termos.

A base de backend e frontend foi adaptada do projeto [SampleCodex](https://github.com/lnncrs/SampleCodex) que tem licença [MIT](https://opensource.org/licenses/MIT).

Componentes de terceiros permanecem sujeitos às respectivas licenças.

___

CMCC - Universidade Federal do ABC (UFABC) - Santo André - SP - Brasil
