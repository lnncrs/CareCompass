# Dados públicos para a demonstração acadêmica

Esta pasta preserva fontes e a amostra preparada para o Care Compass.
Não é um catálogo operacional. Não informa vagas, estoque de refeições ou
funcionamento em tempo real. Dados públicos das fontes não passam a ter a licença
do código do projeto: condições de uso e atribuição de cada origem devem ser
respeitadas. Não foram coletados dados de usuários do chat.

## Organização

```text
data/
├── sources.json                         # URL, coleta, tamanho e SHA-256
├── raw/                                 # HTML original, sem transformação
│   ├── smads/                           # Acolhida
│   ├── sesana/                          # Alimentação
│   ├── saude/                           # CAPS
│   └── desenvolvimento-social-estado/   # Reservada; nenhuma coleta ainda
└── processed/services.sample.json       # Amostra de 40 locais para o mock
```

Os HTMLs são cópias completas das respostas HTTP, não cópias de todo o site.
Imagens, CSS, JavaScript externo e anexos não foram baixados. Consulte os arquivos
como texto para inspeção; a aparência offline e recursos externos não são preservados.
O manifesto `sources.json` identifica cada arquivo e permite conferir sua integridade.
Datas de coleta estão em UTC, independentes da data editorial da página.

## Coleta e complementação — 24/11/2026

| ID da fonte | Órgão | Bytes preservados | Conteúdo |
| --- | --- | ---: | --- |
| cozinha-cidada | SESANA | 169.166 | Pontos de distribuição por território/lote |
| bom-prato-paulistano | SESANA | 168.084 | Unidades, endereços e orientações do programa |
| caps-territorios | Saúde | 221.553 | CAPS por território e modalidade |
| acolhida-leste | SMADS | 171.408 | Lista de acolhimento da Zona Leste |
| acolhida-norte | SMADS | 170.551 | Lista de acolhimento da Zona Norte |
| acolhida-sul | SMADS | 170.682 | Lista de acolhimento da Zona Sul |
| acolhida-oeste | SMADS | 169.598 | Lista de acolhimento da Zona Oeste |
| acolhida-centro | SMADS | 172.693 | Lista de acolhimento do Centro |
| cras-capital | SMDHC | 172.149 | Lista consolidada de CRAS (publicação de 2019) |
| **Total dos originais** | | **1.585.884** | **Cerca de 1,51 MiB** |

As URLs exatas, horários de coleta, tipos de conteúdo e hashes estão no manifesto.
Todas as nove respostas foram recebidas integralmente. O conteúdo editorial
ainda precisa de revisão por registro: coleta não significa validação de cada
endereço, telefone ou oferta.

A alimentação e os CAPS abrangem vários territórios. As fontes de acolhida agora
cobrem Centro, Leste, Norte, Sul e Oeste. CREAS, Centro POP e a lista
estadual de Bom Prato não foram coletados nesta rodada. Não confundir os lotes da
SESANA ou territórios da Saúde com zonas geográficas sem conferir a correspondência.

## Proteções da coleta

O script `scripts/collect_sources.py` usa lista explícita de nove URLs, sem
seguir links recursivamente, baixar recursos associados ou descompactar arquivos.

- Limite de corpo de resposta: 256 KiB por arquivo e 2 MiB acumulados na coleta.
- O orçamento conta bytes recebidos, inclusive tentativas interrompidas e
  execuções anteriores registradas no manifesto. O usuário autorizou aumentar
  o teto original de 1 MiB para 2 MiB na complementação.
- Content-Length é conferido quando disponível; o contador durante a leitura
  continua protegendo respostas sem tamanho informado.
- Respostas comprimidas ou de tipo diferente de HTML são rejeitadas.
- Leituras usam timeout de socket de 10 segundos e verificam prazo de 20 segundos
  entre blocos; uma leitura bloqueada pode consumir até o timeout de socket adicional.
- Arquivos incompletos não são persistidos. O manifesto registra bloqueios e erros.
- Não há retentativas automáticas nem aumento automático de limites.
- Uma nova execução sem `--extend` recusa sobrescrever `sources.json`.
  Com `--extend`, verifica os hashes existentes, preserva os registros e baixa
  somente IDs ainda não registrados. Fontes com erro também não são repetidas
  automaticamente. Não apagar o manifesto para repetir a coleta.

Esses limites cobrem os corpos HTTP lidos pelo script, não o tráfego de cabeçalhos
ou TLS. A meta inicial de menos de 500 KB não foi atingida com os HTMLs
completos; preservá-los mantém o total abaixo do novo teto de 2 MiB e evita tratarmos extratos
como originais. Os metadados e a documentação ocupam espaço adicional pequeno.

## Reprodução e verificação

Da raiz, antes de existir um manifesto de coleta:

```powershell
backend/.venv/Scripts/python.exe scripts/collect_sources.py
```

Para acrescentar fontes explicitamente incluídas na lista, preservando as anteriores:

```powershell
backend/.venv/Scripts/python.exe scripts/collect_sources.py --extend
```

Verificação dos limites sem rede:

```powershell
backend/.venv/Scripts/python.exe -m unittest discover -s scripts -p "test_*.py"
```

## Amostra preparada — 40 locais

`processed/services.sample.json` contém 40 registros: oito para Centro, Leste,
Norte, Sul e Oeste. Em cada região há dois locais de alimentação, dois de
acolhimento e três CAPS (Adulto, AD e IJ) e um CRAS. Seleção intencional para demonstrar
necessidades diferentes, sem pretensão de representatividade estatística.

Cada nome e endereço foi localizado no HTML preservado, por âncora única, com
hash conferido. Os pontos da Cozinha Cidadã recebem rótulos editoriais por
endereço; não são nomes oficiais de unidades. Norte e Oeste têm dois pontos
Cozinha Cidadã; as outras regiões têm um ponto e um Bom Prato Paulistano.

O arquivo tem um objeto raiz com `schema_version`, `dataset_id`, `purpose`,
`selection`, `limitations` e `services`. Cada serviço tem `id`, `name`, `zone`,
`category`, `type`, `address`, `city`, `state`, descrição editorial e `provenance`.
As categorias são `food`, `shelter`, `mental_health` e `social_assistance`; zonas usam nomes sem
acentos (`centro`, `leste`, `norte`, `sul`, `oeste`).

`provenance` traz a URL, `source_id`, caminho e hash do original, data da coleta,
data da conferência e trecho de evidência com nome/endereço. A data de conferência
representa comparação com o arquivo preservado, não confirmação do funcionamento
atual. `access_instructions` permanece `null`: essas listas de endereços não
sustentam uma regra específica de acesso para todos os registros. Descrições
são resumos editoriais da categoria, não ofertas individualizadas verificadas.

As zonas são o filtro editorial do mock, não áreas de atendimento garantidas.
Não há coordenadas nem consultas de vaga. A interface carrega o catálogo por
`GET /api/services?zone=...`; a tool do futuro agente poderá reutilizar a mesma
função de consulta, mas ainda não está implementada.

Para reproduzir e testar a transformação, sem rede:

```powershell
backend/.venv/Scripts/python.exe scripts/build_sample.py
backend/.venv/Scripts/python.exe -m unittest discover -s scripts -p "test_*.py"
```

O gerador recusa fontes com hash alterado ou âncora ausente/ambígua. A seleção
está explícita em `scripts/build_sample.py`. Enriquecer condições de acesso e
integrar catálogo à API e à tool continuam como próximas etapas.

Ao enriquecer um registro, indicar `source_id`, localização do trecho na fonte,
data de conferência e condições de acesso confirmadas.
Separar informações gerais do programa das ofertas específicas da unidade.
Coordenadas permanecem ausentes até verificação; não criar pontos fictícios.
Registrar critérios de seleção, divergências e qualquer classificação de zona
produzida pelo projeto. Um arquivo de evidência extraído deve ser identificado
como derivado, sem alterar o HTML original.

## Ampliação com CRAS

A fonte `cras-capital` foi preservada em `raw/smdhc/cras-capital.html` (Prefeitura,
Secretaria Municipal de Direitos Humanos e Cidadania). Ela é uma lista consolidada
com data editorial de **15/02/2019**: essa antiguidade é registrada em
`provenance.source_note` de cada CRAS e exposta pela API/tool e na lista lateral.
Não foi tratada como prova de funcionamento atual. A extração preserva literalmente
os endereços e identifica o tipo `cras` pelo título explícito da fonte.

Seleção adicionada: Sé (Centro), Itaquera (Leste), Cachoeirinha (Norte), Grajaú
(Sul) e Butantã (Oeste). Os 35 registros anteriores e seus IDs foram preservados;
os cinco CRAS recebem o sufixo `-08`. A categoria nova é `social_assistance`.
O novo total é 40 locais, oito por zona. Não foram adicionadas tags de serviços
não comprovados, nem CREAS/Centro POP por inferência.

API e tool aceitam o filtro opcional `equipment_type=cras`; a seleção de zona
continua obrigatória. O filtro não calcula proximidade. Regenerar com
`scripts/build_sample.py` e reiniciar o backend para recarregar o JSON.
