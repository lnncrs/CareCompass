# Contatos públicos de apoio

A tool `simulate_disguised_help(stage="identify"|"confirm")` reutiliza os
contatos emergenciais de `violence` e a mesma flag visual para o cenário fictício
de pizza. Retorna `simulation=true` e `external_action=false`; não coleta endereço
como argumento, não faz pedidos nem envia ajuda. A confirmação é somente narrativa.

`support_contacts.json` é um cadastro editorial versionado, não um arquivo de
secrets. Fontes oficiais e data de conferência estão em cada registro. O caminho
é configurável por `CARECOMPASS_SUPPORT_CONTACTS_PATH`; o padrão é resolvido a
partir do código, independentemente do diretório do terminal.

O motor LangGraph lê o cadastro ao iniciar. Reinicie após alterações. JSON
inválido, telefone fora do formato ou IDs duplicados impedem sua inicialização.
Nada é baixado ou atualizado automaticamente durante a execução local.

| Situação da tool | Canal | Emergencial |
| --- | --- | --- |
| medical | SAMU 192 | Sim |
| violence | Polícia Militar 190 | Sim |
| fire_rescue | Bombeiros 193 | Sim |
| shelter | SP156 | Não: abordagem/acolhimento |
| women_support | Ligue 180 | Não: orientação/denúncias |

O prompt orienta consultar `get_support_contacts(situation, urgent)` para informar
telefones. A tool não realiza ligações. `urgent=true` só sinaliza a interface
quando existe contato emergencial na categoria consultada. Orientação pelo 156/180
não deve substituir resgate ou intervenção imediata. A detecção é feita pelo
modelo e pode falhar; não é diagnóstico ou triagem validada.

A resposta HTTP contém `urgency: {detected, category, contact_ids, contacts}`.
Os contatos são objetos do cadastro, não telefones fornecidos pelo modelo.
Se mais de uma categoria for consultada como urgente no turno, os contatos são
acumulados e `category` indica a última sinalizada. Cada execução começa sem flag;
o frontend mantém o alerta até dispensa explícita ou nova conversa, sem gravá-lo.
Se o provedor falhar após a tool sinalizar, o backend preserva o aviso e devolve
uma orientação mínima com os contatos já consultados. Falha antes da tool não
gera detecção determinística nem substitui o modelo por triagem por palavras-chave.

O efeito visual é uma borda vermelha com sombra difusa discreta apenas no chat,
sem animação. O aviso textual e os contatos acompanham a cor. Dispensar o aviso
não significa que a situação foi resolvida. `tel:` abre o discador por ação da
pessoa; a aplicação não inicia ligações automaticamente.
