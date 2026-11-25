# Orientações para agentes

Care Compass é um projeto acadêmico de PLN da UFABC, desenvolvido para fins de pesquisa. Leia `docs/product-spec.md`, `docs/architecture.md` e
`docs/implementation-plan.md` antes de alterar o escopo ou a arquitetura.
Consulte também `docs/assistant-behavior.md`, `data/README.md` e
`backend/config/README.md` ao trabalhar em prompt, dados ou urgência.

## Trabalho no repositório

- Trabalhar somente localmente. Não publicar, enviar commits a remotes ou
  provisionar recursos sem solicitação explícita.
- Manter backend e frontend separados. Usar SampleCodex como referência seletiva;
  preservar avisos de licença de terceiros ao reaproveitar arquivos.
- Nunca versionar credenciais ou arquivos `.env`. Não colocar segredos em `VITE_*`.
- A licença do projeto é PolyForm Noncommercial 1.0.0; preservar `LICENSE`.
- Preferir mudanças pequenas, configurações tipadas e responsabilidades claras.
- Atualizar a documentação quando contratos, configuração ou execução mudarem.

## Estado atual e fontes de verdade

- Agente LangGraph já implementado e testado com modelo simulado; validação real
  com Foundry e inspeção visual ainda pendentes. Não confundir implementação
  técnica com avaliação de qualidade do modelo.
- `backend/prompts/assistant.md` é o prompt executável e versionado. Carregar
  uma vez ao iniciar o backend; aplicar edições somente após reinício. Evitar
  duplicar o texto em docs ou embuti-lo no código.
- `data/processed/services.sample.json` contém 40 locais (oito por zona, incluindo um CRAS).
  API e tool devem reutilizar a consulta de domínio, sem catálogos divergentes.
- `backend/config/support_contacts.json` contém contatos públicos, fontes e datas;
  não são secrets. Carregar ao iniciar LangGraph; editar e reiniciar para aplicar.
- Toda variável nova ou alterada deve aparecer em `backend/.env.example`.
- Inferência atual é direta, OpenAI-compatible v1, por chave e implantação;
  não trocar para projeto/agente hospedado sem solicitação.

## Regras do produto

- Português simples, respostas curtas e opção de simplificação na fase inteligente.
- Preservar histórico e localização informada; não reduzir a conversa à última mensagem.
- Busca e catálogo independentes do motor de execução.
- LangGraph é o primeiro motor implementado; Agent Framework, voz, streaming
  e hospedagem são adicionais, não bloqueadores da demonstração.
- Não inventar serviços, vagas ou horários. Registrar fonte e data de conferência.
- O painel é um seletor esquemático de zonas para simular GPS, não mapa geográfico.
  Não adicionar coordenadas, geocodificação ou busca por distância para o mock.
- Centro, Leste, Norte, Sul e Oeste são suportados. A zona ativa enviada pela
  aplicação prevalece sobre regiões no histórico; a tool rejeita outra zona.
- Nova conversa limpa mensagens, rascunho e alerta, preservando a zona selecionada.
  Recarregar restaura o estado inicial. Não persistir conversas nesta fase.
- Identificar o modo ativo. Eco não chama IA nem detecta urgência. Testes simulados
  não autorizam afirmar que a conexão real com Foundry foi validada.
- Urgência usa flag estruturada produzida pela tool e contatos do JSON. Não
  inferir a flag por palavras-chave no frontend nem aceitar telefones do modelo.
- A borda vermelha tem aviso textual e contatos; persiste até dispensa ou nova
  conversa. Não realizar ligações ou acionar serviços automaticamente.
- Não inventar disponibilidade, horários ou condições de acesso ausentes na amostra.
- Não registrar conteúdos das conversas em logs por padrão.

## Verificação

Em `backend/`: `uv run ruff format --check .`, `uv run ruff check .`,
`uv run pyright`, `uv run pytest`.

Em `frontend/`: `npm run format:check`, `npm run lint`, `npm run typecheck`,
`npm run test`, `npm run build`.

Para scripts/dados, da raiz: `backend/.venv/Scripts/python.exe -m unittest discover
-s scripts -p "test_*.py"`. Conferir hashes e origem ao alterar a amostra. Preservar
HTMLs em `data/raw/`; coleta limitada a 256 KiB por arquivo e 2 MiB acumulados,
sem aumentar automaticamente os tetos ou baixar bases completas.

Adicionar testes para contratos e comportamentos relevantes. Reportar checks
executados, falhas e limitações; não afirmar verificações que não foram feitas.
