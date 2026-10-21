# Laudo de qualidade — Prazo Certo

| | |
|---|---|
| **Sistema** | Prazo Certo — gerenciador de tarefas por projeto |
| **Versão avaliada** | commit `4d27a88` (testada pelos colegas) · versão corrigida: commit `a5611da` |
| **Endereço** | https://prazo-certo-pit.vercel.app |
| **Período dos testes** | 20/10/2026 |
| **Responsável** | Alex Lima |

## 1. Objetivo
Registrar os erros encontrados no sistema, a gravidade de cada um, a correção feita e a evidência
de antes e depois, conforme pedido na Situação 3.

## 2. Como os testes foram feitos
1. **Testes automatizados** (pytest): 108 testes de unidade e de integração, em SQLite e PostgreSQL. Ver [verificação e validação](verificacao-e-validacao.md).
2. **Teste de sistema:** [roteiro com 18 casos de teste](roteiro-de-testes.md) no sistema publicado.
3. **Teste de aceitação:** 5 colegas usaram o sistema e responderam ao [formulário de avaliação](README.md#formulário-de-avaliação). Ver [registro dos testes](registro-dos-testes.md).

## 3. Classificação da gravidade
| Gravidade | Quando usar |
|---|---|
| **Alta** | Impede uma função principal ou perde dados |
| **Média** | A função funciona, mas com erro ou de um jeito confuso |
| **Baixa** | Problema visual, de texto ou de conforto |
| **Sugestão** | Melhoria ou função nova, sem erro |

## 4. Erros encontrados e correções

### 4.1 Encontrados na verificação interna (durante o desenvolvimento)
| ID | Descrição | Gravidade | Onde | Correção | Evidência | Status |
|---|---|---|---|---|---|---|
| E01 | Texto "1 atrasada(s)" e "0 de 0 tarefas concluídas" em projeto sem tarefas | Baixa | Lista de projetos e página do projeto | Plural automático e texto "Nenhuma tarefa ainda" | commit `0f7aa7e` | ✅ Corrigido |
| E02 | Com `DATABASE_URL` vazio no `.env`, o sistema não iniciava | Média | Configuração | Variável vazia passa a usar o SQLite padrão | commit `6206bf5` | ✅ Corrigido |
| E03 | O endereço do PostgreSQL entregue pela hospedagem (`postgresql://`) não usaria o driver instalado (identificado antes do primeiro deploy) | Alta (só em produção) | Configuração | Função `normalizar_url_do_banco` + 5 testes em `test_config.py` | commit `8493a2d` | ✅ Corrigido |
| E04 | No Render grátis, o site "dormia" após 15 min (primeiro acesso com ~50 s de espera), o banco expiraria em 30 dias e uma publicação travou esperando aprovação manual | Média | Hospedagem | Mudança para Vercel + Neon (publica em segundos, não dorme, banco sem prazo) | commit `5faee18` | ✅ Corrigido |
| E05 | Na Vercel, a variável `APP_ENV` foi cadastrada com o valor errado ("productionproduction") e o site respondia erro 500 | Alta | Configuração da hospedagem | Variável corrigida; o erro foi achado nos logs da Vercel e o roteiro de testes foi repetido no site | logs da Vercel de 20/10/2026 | ✅ Corrigido |

### 4.2 Encontrados pelos colegas
| ID | Descrição | Quem encontrou | Gravidade | Correção | Evidência (antes / depois) | Status |
|---|---|---|---|---|---|---|
| C01 | Ao cadastrar uma tarefa com prazo anterior a hoje, o sistema não avisava; a tarefa aparecia como atrasada sem explicação | Lucas Oliveira | Média | Aviso embaixo do campo de prazo **antes de salvar** (JavaScript) e mensagem de atenção **depois de salvar** (servidor), ao criar e ao editar. A tarefa continua sendo aceita, porque registrar algo já atrasado é válido. 4 testes novos em `test_rotas.py` | [antes de salvar](imagens/correcoes/c01-aviso-antes-de-salvar.png) / [depois de salvar](imagens/correcoes/c01-aviso-depois-de-salvar.png) · commit `a5611da` | ✅ Corrigido |
| C02 | No celular, os botões Editar e Excluir da tarefa eram pequenos e ficavam colados, facilitando apertar o errado | Camila Ferreira | Baixa | No celular, os botões passaram de 34 px para 44 px de altura (tamanho mínimo recomendado para toque), com Editar à esquerda e Excluir à direita; o quadradinho de concluir também aumentou | [antes](imagens/correcoes/c02-antes-celular.png) / [depois](imagens/correcoes/c02-depois-celular.png) · commit `a5611da` | ✅ Corrigido |
| C03 | Em projetos com muitas tarefas era difícil achar uma tarefa, porque não havia busca | Pedro Henrique Sousa | Baixa | Campo "Buscar tarefa…" (busca por parte do nome, sem diferenciar maiúsculas) e escolha da ordem: pendentes primeiro, prazo ou nome. Funciona junto com o filtro de atrasadas. 11 testes novos | [antes](imagens/correcoes/c03-antes.png) / [depois](imagens/correcoes/c03-depois-busca.png) · commit `a5611da` | ✅ Corrigido |

### 4.3 Sugestões de melhoria recebidas
| ID | Sugestão | Quem sugeriu | Decisão (fazer agora / depois / não fazer) e motivo |
|---|---|---|---|
| S01 | Avisar quando a tarefa for cadastrada com data anterior à atual | Lucas Oliveira | **Feito agora** (é a correção C01) |
| S02 | Aumentar os botões e o espaço entre as opções no celular | Camila Ferreira | **Feito agora** (é a correção C02) |
| S03 | Barra de pesquisa e opções para ordenar as tarefas por nome, prazo ou situação | Pedro Henrique Sousa | **Feito agora** (é a correção C03); as três ordens pedidas foram implementadas |

## 5. Funcionalidades não testadas pelos colegas
| Funcionalidade | Quem não testou | Motivo informado | Ação |
|---|---|---|---|
| Uso no celular | Lucas Oliveira | Usou só o notebook | Coberto pela Camila, que testou no celular, e pelos casos CT16 e CT20 |
| Uso no computador | Camila Ferreira | Focou na experiência no celular | Coberto pelos outros 4 colegas, que usaram notebook |
| Exclusão de projetos | Mariana Costa | Focou no cadastro e na edição | Coberto pelo caso CT14 e por testes automatizados (exclusão em cascata) |
| Edição de projetos | Pedro Henrique Sousa | Focou na consulta das tarefas | Coberto pela Mariana, que testou a edição, pelo caso CT04 e por testes automatizados |

Nenhuma funcionalidade ficou sem teste: o que um colega não testou foi testado por outro colega ou pelo roteiro de testes.

## 6. Indicadores
| Indicador | Valor |
|---|---|
| Testes automatizados | 108 passando, 0 falhando (93 antes + 15 novos das correções), em SQLite e PostgreSQL |
| Casos do roteiro de sistema | 21 de 21 passando (CT19 a CT21 criados para as correções) |
| Colegas que testaram | 5 de 5 |
| Nota média dos colegas | 4,2 de 5 |
| Erros encontrados pelos colegas | 3 (Alta: 0 · Média: 1 · Baixa: 2) |
| Erros corrigidos | 3 de 3 (colegas) · 5 de 5 (verificação interna) |

## 7. Conclusão
O Prazo Certo **atende aos requisitos** da disciplina. Os 5 colegas conseguiram usar as funções principais (projetos, tarefas, concluir, progresso e atrasadas), e nenhum erro de gravidade alta foi encontrado por eles.

Os 3 problemas relatados eram de usabilidade e foram **todos corrigidos** na versão `a5611da`, já publicada:
- **C01:** aviso de prazo que já passou, antes e depois de salvar;
- **C02:** botões maiores e afastados no celular;
- **C03:** busca de tarefas e escolha da ordem.

Cada correção foi feita com testes automatizados escritos antes do código (TDD) e conferida no site publicado. Nenhuma sugestão dos colegas ficou pendente.
