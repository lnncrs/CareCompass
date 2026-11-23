# Orientações para agentes

Care Compass é um projeto acadêmico de PLN da UFABC, desenvolvido para fins de pesquisa. Leia `docs/product-spec.md`, `docs/architecture.md` e
`docs/implementation-plan.md` antes de alterar o escopo ou a arquitetura.

## Trabalho no repositório

- Trabalhar somente localmente. Não publicar, enviar commits a remotes ou
  provisionar recursos sem solicitação explícita.
- Manter backend e frontend separados. Usar SampleCodex como referência seletiva;
  preservar avisos de licença de terceiros ao reaproveitar arquivos.
- Nunca versionar credenciais ou arquivos `.env`. Não colocar segredos em `VITE_*`.
- A licença do projeto é PolyForm Noncommercial 1.0.0; preservar `LICENSE`.
- Preferir mudanças pequenas, configurações tipadas e responsabilidades claras.
- Atualizar a documentação quando contratos, configuração ou execução mudarem.

## Regras do produto

- Português simples, respostas curtas e opção de simplificação na fase inteligente.
- Preservar histórico e localização informada; não reduzir a conversa à última mensagem.
- Busca e catálogo independentes do motor de execução.
- LangGraph será a prioridade; Agent Framework e voz são adicionais.
- Não inventar serviços, vagas ou horários. Registrar fonte e data de conferência.
- Só afirmar proximidade com localização suficientemente precisa.
- Na fase estrutural, identificar o modo de eco e não simular resultados de serviços.
- Não registrar conteúdos das conversas em logs por padrão.

## Verificação

Em `backend/`: `uv run ruff format --check .`, `uv run ruff check .`,
`uv run pyright`, `uv run pytest`.

Em `frontend/`: `npm run format:check`, `npm run lint`, `npm run typecheck`,
`npm run test`, `npm run build`.

Adicionar testes para contratos e comportamentos relevantes. Reportar checks
executados, falhas e limitações; não afirmar verificações que não foram feitas.
