# Arquitetura

## Base implementada

Monorepo com projetos independentes: `backend/` usa FastAPI, Pydantic Settings,
uv e Python 3.13+; `frontend/` usa React, TypeScript e Vite. Dependências travadas
em `uv.lock` e `package-lock.json`. Não há necessidade de ferramenta de monorepo.

O frontend acessa caminhos relativos `/api`; o proxy do Vite encaminha para
`127.0.0.1:8000`. Backend ligado apenas ao loopback no desenvolvimento.
Não há autenticação, banco de dados, persistência de conversa, telemetria,
integração com IA ou publicação nesta fase.

`app.main.create_app` monta a aplicação e seu lifespan. `app.config` reúne
configuração tipada. `app.chat` define o contrato e a função de eco, independente
do transporte HTTP. O frontend separa comunicação HTTP em `src/api/chat.ts`.

## Contrato HTTP inicial

- `GET /api/health`: `{"status":"ok","mode":"echo"}`.
- `POST /api/chat`: recebe `{"messages":[{"role":"user","content":"Olá"}]}`.
- Resposta: `{"mode":"echo","message":{"role":"assistant","content":"Você disse: Olá"}}`.
- Recebe histórico ordenado com papéis `user` e `assistant`; último turno deve
  ser `user`. Não aceita instruções `system` fornecidas pelo cliente.
- Limites: até 100 mensagens, 4.000 caracteres por mensagem do usuário,
  4.100 por mensagem do assistente e 40.000 caracteres no histórico total.
  Entradas inválidas retornam HTTP 422.
- Frontend mantém histórico confirmado em memória e envia todos os turnos.
  O eco usa somente o último conteúdo por definição desta fase; isso não
  representa memória inteligente. Nada é gravado no servidor.
- Timeout de envio de 20 segundos. Falhas mantêm rascunho e histórico confirmado.

## Evolução proposta

Separar recuperação de serviços e orientações da execução do agente.
O recuperador retornará dados tipados com fonte e data de conferência,
sem tipos de LangChain ou Agent Framework nos contratos de domínio.

LangGraph será o primeiro adaptador, recebendo histórico completo e estado
estruturado de necessidade, localização e preferência de comunicação. Não
adicionar silenciosamente um segundo motor: seleção não implementada deve
produzir erro claro. Confirmar endpoint, implantação, API e autenticação do
Foundry antes de escolher a integração concreta.

Catálogo local revisado primeiro. Não depender de Azure AI Search para a entrega.
Mapa e cartões devem usar os mesmos identificadores de serviço. Coordenadas
devem ser verificadas; não inventar marcadores ou precisão de localização.

## Referências e licenças

SampleCodex orientou organização, ferramentas, proxy e visual com tons de verde
e superfícies claras. Configurações frontend e setup de testes foram reaproveitados;
aviso original em `third-party/SampleCodex-LICENSE`.
SampleAgent é referência futura de chat/streaming; não copiar a redução de
histórico à última mensagem nem a busca acoplada ao Agent Framework.
Diabetes Mellitus Prediction orientou a organização acadêmica do README.

O projeto adota PolyForm Noncommercial 1.0.0. Componentes de terceiros mantêm
suas licenças. Não publicar nem provisionar recursos sem solicitação.
