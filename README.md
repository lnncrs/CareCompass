# Care Compass

**Solução adaptativa para encontrar apoio em serviços oficiais da cidade de São Paulo.**

![UFABC Logo](assets/logotipo-ufabc-extenso.png)

Universidade Federal do ABC - Bacharelado em Ciência e Tecnologia<br />
Processamento de Linguagem Natural<br />
Entrega prevista: 25/11/2026<br />

Lenin Cristi - RA 21030114

## Intenção do projeto

O Care Compass é um projeto acadêmico de Processamento de Linguagem Natural
para demonstrar a viabilidade de um chat que ajude pessoas em vulnerabilidade a
entender quais serviços oficiais podem atender suas necessidades em São Paulo.
A comunicação proposta é **adaptativa, breve e orientada à ação**: palavras
simples, respostas curtas, uma pergunta por vez e explicações ajustadas à conversa,
sem presumir escolaridade a partir de erros de escrita.

O protótipo prioriza **alimentação, acolhimento e saúde mental**. A amostra tem
40 locais: oito para cada região — Centro, Leste, Norte, Sul e Oeste — combinando
dois locais de alimentação, dois de acolhimento e três CAPS (Adulto, Álcool e
Drogas e Infantojuvenil) e um CRAS. CREAS e Centro POP fazem parte da proposta mais
ampla, mas não integram a amostra atual. Os CRAS vêm de uma lista municipal
consolidada publicada em 2019; essa limitação aparece na procedência dos registros.

Trata-se de uma **demonstração acadêmica**, não de atendimento público em operação.
O objetivo de PLN é avaliar compreensão da necessidade, uso do contexto,
adaptação da linguagem e fidelidade às informações oficiais recuperadas.

Na interface, o nome exibido é **Encontre Apoio**. Care Compass permanece como
nome acadêmico do projeto e dos componentes internos.

## O que está implementado

- Chat com histórico somente na memória da aba; backend sem persistência de conversas.
- Envio por **Enter**, quebra de linha com **Shift+Enter** e atalhos sempre visíveis
  para alimentação, CRAS, acolhimento e “Estou com frio”, enviados ao clicar.
- Respostas do assistente renderizadas em Markdown (negrito, listas, links e quebras),
  com HTML e imagens desabilitados. Mensagens do usuário permanecem texto simples.
- Painel lateral com botões de zona para **simular o GPS durante a apresentação**.
  Abaixo dele aparecem os oito locais da região, com endereço e fonte. No celular,
  o painel aparece acima do chat. Não há mapa geográfico, coordenadas ou GPS real.
- API não generativa para listar o catálogo, independente do chat.
- Dois modos: `echo` (padrão, sem credenciais) e `langgraph` (modelo no Foundry).
- Agente LangGraph com tools de consulta ao catálogo e aos contatos públicos de apoio.
  A consulta ao catálogo rejeita zonas diferentes da seleção atual.
- Prompt Markdown versionado, carregado uma vez na inicialização do backend.
- Flag estruturada de possível urgência: borda vermelha discreta com brilho difuso,
  aviso textual e contato destacado. Permanece até dispensa ou “Nova conversa”.
  O efeito depende da sinalização do agente; não existe classificação no modo eco.
- Barra de **Simulação** acima dos dois painéis: não há ligações ou acionamento
  de serviços. Os avisos ficam na interface, sem repetição nas respostas do chat.
- Cenário demonstrativo de socorro disfarçado de pedido de pizza: conversa sobre
  sabor e local fictício, com sinalização por tool para os observadores. A confirmação
  de pedido a caminho pertence à encenação; não representa entrega ou envio de ajuda.

O projeto chegou ao recorte de **protótipo para apresentação acadêmica**. O grafo
real possui testes com modelo simulado; durante o desenvolvimento também foram
observadas respostas na interface em testes manuais com Foundry. Esses testes
exploratórios não substituem avaliação sistemática de qualidade, urgência e latência.
Houve ajustes visuais a partir das capturas da demonstração; a revisão completa
de acessibilidade e de telas pequenas permanece pendente.

## Stack e tecnologias

| Camada | Tecnologias e finalidade |
| --- | --- |
| Backend | Python 3.13+, FastAPI, Uvicorn e Pydantic para API e contratos |
| Configuração | Pydantic Settings e `.env` local; credenciais como `SecretStr` |
| Agente | LangGraph, mensagens e tools LangChain (`langchain-core`), integração `langchain-openai` |
| Modelo | Microsoft Foundry/Azure OpenAI, inferência direta via Chat Completions compatível com OpenAI v1 e autenticação por chave |
| Frontend | React 19, TypeScript, Vite, HTML e CSS; Fetch API para HTTP e react-markdown para respostas |
| Dados | JSON local para catálogo e contatos; HTMLs oficiais preservados, manifesto e hashes SHA-256 |
| Dependências | uv com `uv.lock`; npm com `package-lock.json`; monorepo com projetos separados |
| Testes backend | pytest e TestClient do FastAPI/Starlette; HTTPX disponível no ambiente de testes |
| Testes frontend | Vitest, React Testing Library, user-event, jest-dom e jsdom |
| Qualidade | Ruff e Pyright no backend; ESLint, TypeScript e Prettier no frontend |
| Coleta e transformação | Scripts Python com biblioteca padrão e testes unittest |

As versões efetivamente resolvidas estão nos lockfiles. Não usamos banco de dados,
busca vetorial, Azure AI Search ou biblioteca de mapas nesta demonstração.
Voz com Azure Speech e Microsoft Agent Framework são possibilidades futuras,
ainda não implementadas.

## Início rápido

Pré-requisitos: **Python 3.13+**, **uv** e **Node.js 24 LTS com npm**.
Os exemplos usam PowerShell. Abra dois terminais a partir da raiz do repositório.

### 1. Backend — modo de eco, sem secrets

```powershell
cd backend
uv sync --locked
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
uv run uvicorn app.main:app --reload
```

O arquivo de exemplo usa `CARECOMPASS_CHAT_ENGINE=echo`. A configuração padrão
funciona sem `.env`; o comando acima preserva um `.env` que já exista.
Se já houver configuração local de IA, defina `CARECOMPASS_CHAT_ENGINE=echo`
nesse arquivo para executar esta etapa sem chamar o modelo.
Mantenha as pastas `data/`, `backend/prompts/` e `backend/config/` do checkout.

- Saúde da API: <http://127.0.0.1:8000/api/health>.
- Documentação interativa: <http://127.0.0.1:8000/docs>.
- Catálogo da Leste: <http://127.0.0.1:8000/api/services?zone=leste>.

### 2. Frontend

```powershell
cd frontend
npm ci
npm run dev
```

Abra o endereço exibido pelo Vite, normalmente <http://localhost:5173>.
O proxy de desenvolvimento encaminha `/api` ao backend na porta 8000.
Selecione uma zona, confira os oito locais e envie uma mensagem. No modo de eco,
a resposta será “Você disse: …”; o agente e a sinalização de urgência não são acionados.

Trocar de zona preserva a conversa e atualiza o contexto do próximo turno.
“Nova conversa” apaga mensagens, rascunho e alerta, preservando a zona selecionada.
Recarregar a página apaga o estado da aba e restaura a zona inicial Leste.

### 3. Ativar LangGraph e Foundry — demonstração com IA

Edite **somente `backend/.env`**, usando valores reais localmente:

```dotenv
CARECOMPASS_CHAT_ENGINE=langgraph
CARECOMPASS_FOUNDRY_BASE_URL=https://SEU-RECURSO.openai.azure.com/openai/v1/
CARECOMPASS_FOUNDRY_DEPLOYMENT=sua-implantacao
CARECOMPASS_FOUNDRY_API_KEY=sua-chave-local
```

Requer uma implantação com **tool calling** e endpoint direto de inferência
OpenAI v1 Chat Completions. A base inclui `/openai/v1/`, sem `/chat/completions`
ou `/responses` no final. Use a base de inferência fornecida pelo Foundry.
Não use o endpoint de projeto `/api/projects/`. Nesta implementação, a API v1
não requer `api-version`; autenticação por identidade Microsoft e APIs legadas
não foram implementadas. Reinicie o backend para aplicar a configuração.

Nunca versionar `.env` ou colocar secrets em variáveis `VITE_*`. As conversas
no modo LangGraph são enviadas ao endpoint configurado no Foundry; no modo eco,
não há chamada ao modelo. Use cenários fictícios na demonstração.

## Notebook didático

O [notebooks/sample-agent.ipynb](notebooks/sample-agent.ipynb) apresenta um agente
menor, construído nas próprias células, sem importar `app.agent` ou iniciar Uvicorn.
Reutiliza o prompt oficial, o catálogo e `backend/.env`. A pergunta fixa busca
alimentação barata e o resultado identifica a zona selecionada.

Prepare as dependências opcionais a partir da raiz:

```powershell
cd backend
uv sync --locked --group notebook
```

Abra o notebook no VS Code com suporte Jupyter e selecione o interpretador
`backend/.venv/Scripts/python.exe` como kernel. Execute as células na ordem.
Configure as variáveis Foundry no mesmo `.env`; o notebook usa diretamente o
modelo mesmo que `CARECOMPASS_CHAT_ENGINE=echo`. A célula final chama o serviço
real e pode consumir créditos. Não exiba configurações ou secrets nas saídas.

Para trocar a zona, altere `ZONE` e reexecute as células 2 a 5. Para reler o
`.env`, reexecute desde a primeira. O exemplo é restrito a alimentação, sem
interface ou sinalização de urgência. As cinco células foram verificadas com
cliente simulado em um kernel Jupyter real; teste com Foundry permanece pendente.
Antes de versionar, limpe todas as saídas e contagens de execução.

## Prompt, contatos e configuração

O prompt executável é [backend/prompts/assistant.md](backend/prompts/assistant.md).
Ele orienta adaptação da linguagem, concisão, consulta às tools e tratamento de
possível urgência. As diretrizes de revisão estão em
[docs/assistant-behavior.md](docs/assistant-behavior.md).

Os contatos públicos ficam em [backend/config/support_contacts.json](backend/config/support_contacts.json),
com finalidade, abrangência, fonte e data de conferência. A tool
`get_support_contacts` distingue emergência de orientação/acolhimento.
Ela não realiza ligações. A tool `simulate_disguised_help` sinaliza o cenário
fictício de pizza usando os mesmos contatos configurados. Veja
[regras de sinalização](backend/config/README.md).

| Variável `CARECOMPASS_…` | Padrão / uso |
| --- | --- |
| `APP_NAME` | `Care Compass` |
| `CHAT_ENGINE` | `echo` ou `langgraph`; padrão `echo` |
| `CATALOG_PATH` | `data/processed/services.sample.json` na raiz |
| `PROMPT_PATH` | `backend/prompts/assistant.md` |
| `SUPPORT_CONTACTS_PATH` | `backend/config/support_contacts.json` |
| `FOUNDRY_BASE_URL` | Base HTTPS de inferência v1; exigida em LangGraph |
| `FOUNDRY_DEPLOYMENT` | Nome da implantação; exigido em LangGraph |
| `FOUNDRY_API_KEY` | Secret local; exigido em LangGraph |
| `AGENT_TIMEOUT_SECONDS` | `15`: timeout do turno completo |
| `AGENT_MAX_STEPS` | `6`: limite de passos do grafo |
| `AGENT_MAX_OUTPUT_TOKENS` | `600`: limite de saída por chamada ao modelo |

Todos os nomes da tabela recebem o prefixo `CARECOMPASS_`. Os caminhos padrão
são resolvidos a partir do código; caminhos personalizados relativos usam o
diretório de execução. Prefira caminhos absolutos ao sobrescrevê-los.
O catálogo e o prompt são carregados na inicialização; contatos são carregados
quando o motor LangGraph é criado. **Reinicie após editar esses arquivos**.
Prompt ausente/vazio, catálogo inválido ou configuração incompleta de LangGraph
impedem a inicialização, sem fallback silencioso para eco.

O frontend espera até 20 segundos; ajuste esse limite se aumentar o timeout do
agente. Timeout do agente retorna HTTP 504; outras falhas retornam HTTP 502 sem
detalhes do provedor. Se a tool já sinalizou urgência antes de uma falha, o backend
preserva a flag e os contatos em uma resposta mínima.

## Dados e rastreabilidade

Nove páginas oficiais estão preservadas em `data/raw/`, separadas por órgão, com
URL, data de coleta e hash em `data/sources.json`. Os originais somam cerca de
1,51 MiB. A coleta tem teto de **256 KiB por arquivo e 2 MiB acumulados**.

A amostra em [data/processed/services.sample.json](data/processed/services.sample.json)
tem 40 registros com nomes e endereços conferidos nas fontes preservadas.
Descrições são resumos editoriais das categorias; formas de acesso não confirmadas
ficam explicitamente pendentes. A API de listagem e a tool reutilizam a mesma
consulta ao catálogo. O seletor de zona serve à demonstração e não define a área
oficial de atendimento de cada unidade.

Veja [data/README.md](data/README.md) para procedência, critérios de seleção,
limites e comandos de reprodução. Não é necessário baixar novamente as fontes
para executar a aplicação.

## Estrutura do projeto

```text
├── backend/
│   ├── config/               # Contatos públicos e regras de sinalização
│   ├── prompts/              # Prompt executável em Markdown
│   ├── src/app/              # API, configuração, catálogo e agente
│   ├── tests/
│   ├── .env.example
│   ├── pyproject.toml
│   └── uv.lock
├── frontend/                 # React, TypeScript, CSS e testes de interface
├── data/
│   ├── raw/                  # HTMLs originais por órgão
│   ├── processed/            # Amostra JSON usada pela aplicação
│   └── sources.json          # Manifesto de procedência
├── scripts/                  # Coleta, geração da amostra e testes sem rede
├── notebooks/sample-agent.ipynb # Exemplo didático, usando o kernel do backend
├── docs/                     # Produto, arquitetura, comportamento e plano
├── assets/                   # Identificação acadêmica
├── third-party/              # Avisos de licença de arquivos reaproveitados
├── AGENTS.md
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

Da raiz, para os scripts e a rastreabilidade:

```powershell
backend/.venv/Scripts/python.exe -m unittest discover -s scripts -p "test_*.py"
```

Os testes não exigem secrets: usam modelo simulado e dados locais. Verificam o
grafo, tools, histórico, zonas, prompt, falhas e sinalização na interface, mas
não medem a qualidade de compreensão de um modelo real.
Nas verificações de 24/11/2026, passaram **36 testes backend e 12 frontend**,
além de lint, tipos, formatação e build. Os scripts de dados têm uma suíte separada
de sete testes. Isso não equivale a avaliação do modelo ou de acessibilidade.

O build gera arquivos estáticos; `vite preview` não fornece o proxy de API de
desenvolvimento. Para testar o chat localmente, use `npm run dev` com backend ativo.

## Roteiro de apresentação

Com o modo `langgraph` ativo e a API conectada:

1. Selecionar Leste e conferir os oito registros no painel lateral.
2. Usar “Encontrar alimentação” e “Buscar um CRAS”; comparar nomes e endereços
   das respostas com o catálogo exibido.
3. Trocar para outra zona e repetir a pergunta, mostrando que a seleção atual
   prevalece sobre a região anterior da conversa.
4. Usar “Estou com frio” para demonstrar acolhimento e o canal de encaminhamento.
5. Pedir uma explicação mais simples e observar a reformulação do texto.
6. Em nova conversa, encenar o pedido de pizza com sabor e endereço fictício;
   observar o alerta e sua persistência. A confirmação é somente narrativa.
7. Dispensar o aviso ou iniciar nova conversa para demonstrar a limpeza do alerta.

Usar apenas dados fictícios. A sinalização é experimental e depende do modelo;
não há promessa de detecção correta em todos os casos.

## Limitações e próximos passos

- Registrar uma rodada reproduzível de avaliação com Foundry, incluindo chamadas
  de tools, falhas e latência, além dos testes manuais exploratórios já realizados.
- Executar avaliação de PLN com cenários de compreensão, simplificação, histórico,
  mudança de zona e fidelidade ao catálogo; ainda não há métricas de IA reais.
- Avaliar a detecção de urgência, incluindo falsos positivos e omissões. O alerta
  é uma sinalização experimental, não diagnóstico ou triagem validada.
- Completar a revisão visual e de acessibilidade por teclado e em telas pequenas.
- Complementar informações de acesso dos equipamentos e registrar os resultados
  e limitações no relatório acadêmico.

O catálogo não informa vagas, estoque ou horários em tempo real. Não há ligação,
reserva ou acionamento automático de equipes. A simplificação é uma diretriz
conversacional do prompt; não há botão dedicado. Não há áudio, streaming,
autenticação de usuários, persistência de conversas ou hospedagem implementados.
O histórico fica na aba e o tracing de conteúdo para LangSmith é desativado no
contexto da execução do agente. O trabalho neste repositório é local.

Consulte a [especificação](docs/product-spec.md), a [arquitetura](docs/architecture.md)
e o [plano de execução](docs/implementation-plan.md).

## Licença

O código deste projeto é disponibilizado sob a licença [MIT](LICENSE).

A base de backend e frontend foi adaptada do projeto [SampleCodex](https://github.com/lnncrs/SampleCodex) que tem licença [MIT](https://opensource.org/licenses/MIT).

___

CMCC - Universidade Federal do ABC (UFABC) - Santo André - SP - Brasil
