# Arquitetura

## Organização e ciclo de vida

Monorepo local: FastAPI/Python em `backend/`, React/TypeScript/Vite em `frontend/`.
Dependências reproduzíveis em `uv.lock` e `package-lock.json`; stack no README.
Frontend usa caminhos relativos `/api`, encaminhados pelo Vite à porta 8000.
Sem banco de dados, autenticação de usuários, memória persistida ou publicação.

`app.main.create_app` configura rotas e lifespan. Na inicialização:

1. Carregar configuração tipada de `app.config`.
2. Carregar `Catalog` do JSON e o prompt Markdown.
3. Se `CHAT_ENGINE=langgraph`, criar o motor e carregar o JSON de contatos.

Arquivos e configurações ficam fixos até reinício. Os caminhos padrão são
resolvidos pelo código; sobrescritas relativas usam o diretório do processo.
O checkout precisa manter `data/`, `backend/prompts/` e `backend/config/`.
Não há empacotamento de hospedagem. Configuração incompleta ou arquivos inválidos
impedem a inicialização, sem fallback silencioso. Não registrar conteúdo ou secrets.

## Domínio e execução

- `app.catalog`: contratos tipados e `Catalog.list_services(zone)`, sem dependência
  de LangGraph ou HTTP. API e tool reutilizam a mesma consulta.
- `app.support`: cadastro tipado de contatos públicos e estrutura `Urgency`.
- `app.chat`: contratos HTTP de conversa e resposta de eco.
- `app.agent`: protocolo `ChatEngine`, carregamento do prompt e motor LangGraph.
- Frontend: comunicação em `src/api/`; painel e listagem em `ServicesPanel.tsx`.

O prompt executável é [assistant.md](../backend/prompts/assistant.md). Diretrizes
explicativas em [assistant-behavior.md](assistant-behavior.md), sem segunda cópia
executável. `AGENTS.md` orienta o agente de desenvolvimento, não o chat do produto.

## Motor LangGraph

`CARECOMPASS_CHAT_ENGINE=echo|langgraph`; `echo` funciona sem credenciais.
LangGraph usa nós `assistant` e `tools`, retornando ao modelo após consultas.
Cada turno cria execução isolada, sem checkpointer nem previous_response_id.
Todo o histórico recebido da aba é passado ao modelo. A zona vem em campo separado
e prevalece sobre regiões antigas das mensagens.

- `list_services(zone)`: devolve registros da zona ativa; outra zona retorna
  `zone_mismatch` sem liberar registros daquela região. O prompt exige a consulta
  antes de recomendar. Isso não garante que texto livre nunca alucine.
- `get_support_contacts(situation, urgent)`: consulta o cadastro público. Com
  `urgent=true` e contato emergencial válido, registra a flag no contexto do turno.
  Não aceita telefone gerado pelo modelo como argumento nem realiza ligações.

Inferência por `langchain-openai.ChatOpenAI`, endpoint HTTPS de Chat Completions
compatível com OpenAI v1 (`/openai/v1/`), implantação com tool calling e chave.
Não usa endpoint de projeto nem agente hospedado Foundry. API legada e identidade
Microsoft não estão implementadas. Não há validação de conectividade ao iniciar:
a primeira chamada real ainda precisa ser testada com configuração local.

Timeout do turno, limite de passos e limite de saída por chamada são configuráveis.
Retries automáticos do provedor estão desativados. Tracing LangSmith é desativado
no contexto da execução. Sem persistência local de conteúdo; mensagens no modo IA
são enviadas ao endpoint configurado do Foundry.

## Contrato HTTP atual

### Saúde

`GET /api/health` retorna `{"status":"ok","mode":"echo"}` ou modo `langgraph`.
Indica saúde da aplicação, não prova conectividade ou qualidade do modelo.

### Catálogo

`GET /api/services?zone=leste` retorna `{zone, services}`. Cada serviço contém
identificador, nome, zona, categoria, tipo, endereço, descrição e procedência
pública (URL e data). Os oito registros não são filtrados pela pergunta do chat.

### Conversa

`POST /api/chat` recebe:

```json
{"zone":"leste","messages":[{"role":"user","content":"Preciso de alimentação"}]}
```

Exemplo de resposta em eco:

```json
{
  "zone": "leste",
  "mode": "echo",
  "message": {"role":"assistant","content":"Você disse: Preciso de alimentação"},
  "urgency": {"detected":false,"category":null,"contact_ids":[],"contacts":[]}
}
```

- Zonas: `centro`, `leste`, `norte`, `sul`, `oeste`. Ausência/invalidez: HTTP 422.
- Papéis aceitos: `user` e `assistant`; último turno deve ser `user`.
- Limites: 100 mensagens, 4.000 caracteres por mensagem do usuário, 4.100 por
  mensagem do assistente e 40.000 no histórico. Entradas inválidas: HTTP 422.
- Falha do agente: HTTP 502; timeout: 504; nenhum detalhe privado do provedor.
- Exceção: se a tool já sinalizou urgência antes da falha, retornar HTTP 200 com
  flag, contatos e orientação mínima, preservando a sinalização.
- Frontend espera até 20 segundos; backend usa 15 por padrão. Falhas preservam
  histórico confirmado e rascunho. Eco usa somente o turno atual por definição.

## Localização simulada e alerta

Respostas do assistente usam `react-markdown`, sem HTML bruto ou imagens.
O tratamento padrão de URLs bloqueia protocolos perigosos; links abrem em nova
aba com `noopener noreferrer`. Markdown não altera o conteúdo do histórico
enviado ao backend. Mensagens do usuário continuam em texto simples.

Botões esquemáticos simulam GPS e mostram a lista da zona ativa. Não há mapa
geográfico, coordenadas ou medição de proximidade. No celular, painel acima do
chat. Trocas cancelam consultas antigas e remontam a lista. Zona inicial Leste;
seletor bloqueado durante envio. Nova conversa limpa mensagens/rascunho/alerta,
mas preserva a zona. Recarregar restaura Leste.

A flag de urgência é independente por turno no backend; no frontend, permanece
até dispensa explícita ou nova conversa, mesmo após turno sem flag ou troca de zona.
Borda vermelha suave, aviso textual e contatos acompanham o sinal. Não há
classificação por palavras-chave no frontend. Detecção pelo modelo pode falhar.
Detalhes e fontes em [Contatos públicos](../backend/config/README.md).

## Evolução e referências

### Exemplo didático em notebook

`notebooks/sample-agent.ipynb` usa o kernel `backend/.venv` com grupo opcional
`notebook` (ipykernel, nbformat, nbclient e python-dotenv). Não exige outro
ambiente nem Uvicorn. Lê explicitamente `backend/.env` com precedência das
variáveis do processo e reutiliza prompt e catálogo oficiais, sem importar os
componentes de execução da aplicação. O grafo e a tool são definidos nas células
para tornar o fluxo visível. O recorte é alimentação por zona, sem urgência.

O notebook cria o cliente direto independentemente de `CHAT_ENGINE`. Alterar
prompt/zona exige reexecutar células; o comportamento não equivale a hot reload
da API. Versionar sem outputs ou contagens. Execução completa foi verificada
com cliente simulado em kernel Jupyter, sem secrets reais ou chamada ao Foundry.

`notebooks/sample-agent-collab.ipynb` é uma distribuição independente para
Colab: instala dependências, solicita os parâmetros de inferência na sessão e
incorpora retratos do prompt oficial e do catálogo. Esses retratos não acompanham
alterações automaticamente e devem ser
atualizados ao preparar outra versão; a fonte executável do backend não muda.
O exemplo mantém a pergunta fixa sobre alimentação e não implementa contatos,
interface ou sinalização de urgência.

## Referências técnicas:

- [ChatOpenAI](https://docs.langchain.com/oss/python/integrations/chat/openai)
- [API v1 no Foundry](https://learn.microsoft.com/en-us/azure/foundry/openai/api-version-lifecycle)
- [Roteamento de tools](https://reference.langchain.com/python/langgraph.prebuilt/tool_node/tools_condition)

SampleCodex orientou a base e suas licenças estão em `third-party/`.
SampleAgent é referência de chat/streaming, sem copiar a redução de histórico à
última mensagem ou a busca acoplada ao Agent Framework. Diabetes Mellitus
Prediction orientou a apresentação acadêmica. Licença do projeto: MIT; preservar condições dos componentes e dados de terceiros.

## Filtro por tipo de equipamento

`GET /api/services?zone=leste&equipment_type=cras` e
`list_services(zone, equipment_type)` aceitam o mesmo filtro opcional tipado.
O tipo principal de CRAS é `cras`, categoria `social_assistance`. Sem filtro,
a listagem retorna os oito registros da zona. Tipos desconhecidos na API geram 422.
A nota da fonte consolidada de CRAS, publicada em 2019, é preservada em
`provenance.source_note` e compartilhada com a tool/interface.
