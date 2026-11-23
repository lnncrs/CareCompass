# Care Compass — especificação do produto

Projeto acadêmico de Processamento de Linguagem Natural da Universidade Federal
do ABC, com entrega prevista para 25/11/2026. Autores e identificação da turma
a confirmar.

## Objetivo

Ajudar pessoas em vulnerabilidade a encontrar serviços oficiais em São Paulo:
alimentação, acolhimento, CRAS, CREAS, Centro POP e saúde mental. Piloto na Zona
Leste, com cobertura explicitada e sem prometer abrangência municipal completa.

Português simples por padrão, respostas curtas e opção de simplificação.
Considerar contexto da conversa e localização, sem inferir capacidade de leitura
ou condições pessoais. Pedir esclarecimentos quando necessário.

## Fase estrutural

- Chat de eco acessível e responsivo, com identificação explícita do protótipo.
- Histórico enviado à API; nenhum modelo ou mecanismo de recuperação acionado.
- Estados de envio, sucesso e falha, com preservação do rascunho em falhas.
- Sugestões preenchem o campo; o usuário confirma pelo botão Enviar.
- Nova conversa limpa o estado local. Recarregar também apaga a conversa.
- Painel reservado para mapa no desktop; foco no chat no celular.
- Nenhuma localização solicitada e nenhum serviço fictício exibido.

Aceite: iniciar backend e frontend, enviar dois turnos e receber os ecos pela
API real; interromper a API e verificar a mensagem de erro sem perder o texto.

## Próximas fases

LangGraph com integrações LangChain e modelo no Microsoft Foundry, catálogo
local revisado, recuperação de orientações oficiais, fontes visíveis, cartões
e mapa dos serviços. Execução isolada para permitir outro motor por configuração;
Microsoft Agent Framework e Azure Speech são adicionais.

Fontes candidatas: GeoSampa/SMADS e páginas municipais de CRAS, CREAS, Centro POP,
acolhimento, CAPS e Cozinha Cidadã; Bom Prato requer fonte estadual.
Cada registro deve conter URL e data de conferência. Esta fase não revisou
nem coletou serviços. Não prometer vagas ou horários desconhecidos. Só afirmar
proximidade com localização suficientemente precisa; bairro permite filtrar,
mas não comprova distância individual.

## Avaliação de PLN planejada

Criar ao menos 20 cenários com pedidos informais, erros de escrita, ambiguidade,
simplificação e múltiplos turnos. Medir identificação de necessidade, relevância
da recuperação, preservação de contexto, fidelidade às fontes e clareza.
Registrar resultados e limitações no relatório acadêmico, sem inventar métricas.
