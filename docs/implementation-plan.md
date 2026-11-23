# Plano de execução

Entrega prevista: 25/11/2026. Trabalhar localmente e priorizar um fluxo completo.

## Fase 1 — estrutura (23/11)

- [x] README acadêmico mínimo e documentação de produto e arquitetura.
- [x] AGENTS.md, .gitignore e configuração sem segredos.
- [x] FastAPI com saúde e chat de eco, recebendo histórico.
- [x] React/TypeScript com chat, rascunho preservado em falha e nova conversa.
- [x] Painel de mapa reservado e versão móvel com foco no chat.
- [x] Validar checks e fluxo integrado; resultado registrado abaixo.

### Verificação da fase estrutural — 23/11/2026

- Backend: Ruff (formatação e lint), Pyright e 7 testes passaram.
- Frontend: Prettier, ESLint, TypeScript, 2 testes e build passaram.
- Auditoria npm após correções compatíveis: zero vulnerabilidades reportadas.
- Integração HTTP real pelo proxy do Vite: página HTTP 200, saúde da API e
  resposta de eco com histórico de três mensagens verificados.
- Testes de interface verificam envio do histórico completo no segundo turno,
  nova conversa e rascunho preservado em falha.
- Verificação visual em navegador pendente: a prévia não conseguiu acessar
  o servidor local deste ambiente. Layout móvel ainda requer inspeção visual.
- Testes Python precisaram executar fora do sandbox; o TestClient ficou
  bloqueado no ambiente restrito. Fora dele, os testes passaram em 0,47 segundo.
- Aviso não bloqueante do Starlette: integração TestClient com httpx está
  depreciada; avaliar migração para httpx2 ao atualizar a base.

## Fase 2 — inteligência e dados (23–24/11)

- [ ] Confirmar configuração do Foundry fora do chat e sem versionar credenciais.
- [ ] Implementar adaptador LangGraph/LangChain com contexto de múltiplos turnos.
- [ ] Criar catálogo local revisado da Zona Leste com fontes e datas.
- [ ] Recuperar orientações oficiais independentemente do motor de execução.
- [ ] Respostas simples, curtas, fundamentadas e com opção de simplificação.
- [ ] Cartões e mapa sincronizados; pedir região quando faltar localização.
- [ ] Streaming se o fluxo principal estiver estável.

## Fase 3 — avaliação e entrega (25/11)

- [ ] Executar cenários de PLN e registrar resultados reais.
- [ ] Validar contexto, fontes, incertezas e comportamento de localização.
- [ ] Revisar acessibilidade, estados de erro e execução em ambiente limpo.
- [ ] Finalizar relatório, README e roteiro de demonstração.

## Adicionais

Voz com Azure Speech, segundo motor Microsoft Agent Framework e hospedagem.
Não comprometer o fluxo LangGraph para implementar esses adicionais.
