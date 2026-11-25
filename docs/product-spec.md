# Care Compass — especificação do produto

Projeto acadêmico de Processamento de Linguagem Natural da UFABC, desenvolvido
para pesquisa e demonstração de viabilidade, com entrega prevista para 25/11/2026.
A identificação acadêmica confirmada está no README; não inventar autores ou turma.

## Intenção e escopo da demonstração

Orientar sobre alimentação, acolhimento e saúde mental em São Paulo, com linguagem
simples, curta e adaptativa, sem presumir escolaridade ou capacidade pelos erros
de escrita. A proposta mais ampla inclui CREAS e Centro POP, ainda fora da amostra.
CRAS foi acrescentado com uma unidade por zona.

A amostra tem oito registros para cada região: Centro, Leste, Norte, Sul e Oeste.
Em cada região: dois de alimentação, dois de acolhimento e três CAPS (Adulto,
Álcool e Drogas e Infantojuvenil) e um CRAS. É uma seleção intencional, não representativa
estatisticamente nem um catálogo completo da cidade.

## Dois fluxos na interface

1. O painel de demonstração permite escolher uma zona para simular o GPS e
   consulta uma API não generativa, mostrando os oito locais com endereço e fonte.
2. O chat envia histórico e zona ativa. Em LangGraph, o agente consulta o catálogo
   pela tool antes de indicar opções pertinentes à pergunta.

O seletor visual não é mapa geográfico e não faz parte da interface proposta
para o produto futuro. Não requer coordenadas, geocodificação ou localização
precisa. Em tela pequena, o painel aparece acima do chat. A zona inicial é Leste;
ela é apenas o valor inicial, não uma restrição de cobertura à Leste.

Trocar a zona atualiza imediatamente o contexto do próximo turno, mantendo as
mensagens. A seleção da aplicação prevalece sobre regiões citadas no histórico.
Durante o envio, o seletor fica bloqueado. Nova conversa limpa mensagens,
rascunho e alerta, preservando a zona. Recarregar restaura todo o estado inicial.

## Modos e comunicação

Atalhos “Encontrar alimentação”, “Buscar um CRAS”, “Conhecer opções de acolhimento”
e “Estou com frio” ficam sempre visíveis acima do campo de mensagem, mesmo após
respostas. Eles enviam a mensagem ao clicar, usando a zona ativa; durante envio ficam
desabilitados. O atalho de frio não ativa urgência por si só: a classificação
continua sendo responsabilidade do agente.

- `echo` é o padrão sem credenciais: apenas repete a mensagem, sem agente ou triagem.
- `langgraph` usa inferência direta no Foundry com tools e histórico da mesma
  conversa, sem persistência no servidor ou recuperação de conversas antigas.
- Prompt executável em [backend/prompts/assistant.md](../backend/prompts/assistant.md),
  carregado uma vez ao iniciar o backend. Alterações exigem reinício.
- Português simples, preferência por até três frases curtas, uma pergunta por vez
  e uma ou duas opções relevantes. Informações essenciais podem exigir mais texto.
- Simplificação é conversacional; não há botão dedicado ou áudio implementado.
- Detalhes e critérios em [Comportamento do assistente](assistant-behavior.md).

## Possível urgência

A tool de contatos públicos pode sinalizar uma flag estruturada quando o agente
identifica risco imediato. O frontend aplica borda vermelha com brilho discreto
no chat, aviso textual e contatos. O aviso permanece até dispensa ou nova conversa;
cor não é o único indicador. Nada é acionado ou discado automaticamente.

Contatos e finalidades ficam em JSON separado e configurável, com fonte e data.
Orientação/acolhimento não substituem canais emergenciais. A classificação pelo
modelo é experimental, sujeita a falsos positivos e omissões, sem validação clínica.

## Dados e limites

Fontes originais em `data/raw/`, manifesto com URLs/datas/hashes e amostra em
`data/processed/services.sample.json`. Ver [Dados e rastreabilidade](../data/README.md).
Nomes e endereços foram conferidos contra os HTMLs preservados, não em campo.
Formas de acesso ainda precisam de complemento. Não inventar vagas, preços,
horários ou serviços nem apresentar ausência na amostra como inexistência na região.
Não calcular proximidade: a zona do mock não estabelece distância nem abrangência
oficial de atendimento. Não consultar disponibilidade em tempo real nesta demonstração.

## Aceite técnico e pendências

- API de listagem devolve somente os registros da zona escolhida; erros permitem
  nova tentativa, sem misturar respostas de consultas antigas.
- Chat envia histórico completo e zona atual; falha preserva rascunho.
- Tools usam somente dados configurados; nova execução não herda estado de outra.
- Prompt permanece fixo até reinício; configurações e arquivos inválidos falham
  claramente, sem substituir LangGraph por eco silenciosamente.
- Sinalização de urgência e dispensa são testadas com respostas simuladas.

O grafo e a interface possuem testes automatizados. Ainda faltam validação real
com Foundry, inspeção visual/acessibilidade, avaliação de PLN e relatório.
Preparar ao menos 20 cenários com linguagem informal, simplificação, ambiguidades,
contexto, troca de zona, fidelidade às fontes e urgência. Registrar resultados
reais, sem confundir testes técnicos com métricas de qualidade do modelo.

Voz, segundo motor Microsoft Agent Framework, streaming e hospedagem são adicionais.
