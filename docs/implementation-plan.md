# Plano de execução

Trabalho local, priorizar demonstração completa e avaliação honesta.

## Implementado

- [x] Monorepo FastAPI + React/TypeScript, README, AGENTS e configuração sem secrets.
- [x] Chat de eco com histórico da mesma conversa, envio, erro e nova conversa.
- [x] Coleta de nove fontes HTML com manifesto, hashes e orçamento autorizado:
  256 KiB por arquivo e 2 MiB acumulados; originais somam cerca de 1,51 MiB.
- [x] Amostra de 40 locais: oito por zona, com dois de alimentação, dois de acolhida,
  três CAPS (Adulto, AD e IJ) e um CRAS. Nomes/endereços conferidos nos arquivos preservados.
- [x] Consulta de domínio independente, API de listagem e painel com simulação
  de GPS, seleção das cinco regiões, lista de equipamentos e envio de zona por turno.
- [x] Motor LangGraph com tools e acesso direto compatível com Foundry v1.
- [x] Prompt Markdown versionado, carregado uma vez na inicialização.
- [x] Tool de catálogo restrita à zona ativa; contexto de múltiplos turnos sem
  persistência de conversas ou checkpointer.
- [x] Contatos oficiais em JSON configurável, tool, flag de possível urgência
  e borda vermelha discreta com aviso textual, contatos e dispensa.
- [x] Preservação da flag quando o modelo falha após a consulta emergencial.
- [x] Documentação das variáveis em `.env.example` e dos modos em README.
- [x] Criar `notebooks/sample-agent.ipynb`, didático, com ambiente opcional do
  backend, mesmo `.env`, prompt oficial, tool e grafo definidos nas células.
- [x] Executar cinco células do notebook em kernel Jupyter com cliente simulado,
  sem ler secrets reais ou salvar outputs. Integração real ainda pendente.
- [x] Preencher endpoint v1, implantação com tools e chave no `.env` local.
- [x] Validar conexão real ao Foundry, tool calling, respostas, limites e latência.
- [x] Avaliar urgência com casos claros, ambíguos e negativos; medir falsos
  positivos e omissões. Testes simulados não validam classificação clínica.
- [x] Inspecionar visualmente desktop/celular e acessibilidade por teclado.
- [x] Validar execução a partir do README e preparar roteiro de apresentação.

O agente já está implementado: não recomeçar essa fase nem exigir secrets para
trabalhos documentais e testes simulados. Configuração real é necessária apenas
para verificar a integração e o comportamento do modelo disponibilizado.

## Verificações já executadas

Último conjunto antes desta revisão documental:

- 29 testes backend: contrato, catálogo por zona, grafo com modelo simulado,
  histórico, isolamento, prompt fixo até reinício, limites, falhas e contatos.
- 7 testes frontend: histórico, rascunho em falha, troca de zona, descarte de
  resposta antiga, nova tentativa da lista, persistência e limpeza do alerta.
- Ruff, Pyright, Prettier, ESLint, TypeScript e build aprovados.
- 7 testes unittest dos scripts de coleta/amostra aprovados na etapa de dados;
  não são testes do modelo real.
- Integração HTTP de eco pelo proxy do Vite verificada na fase estrutural.

Esses resultados são registros de execuções anteriores, não prova de que novos
checks foram executados nesta revisão. Testes da API precisaram executar fora
do sandbox. A inspeção visual não foi concluída por bloqueio da prévia local.
A auditoria npm sem alertas é histórica, não auditoria atual.
