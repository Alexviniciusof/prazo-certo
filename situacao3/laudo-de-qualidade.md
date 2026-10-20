# Laudo de qualidade — Prazo Certo

| | |
|---|---|
| **Sistema** | Prazo Certo — gerenciador de tarefas por projeto |
| **Versão avaliada** | commit `________` (preencher com a versão testada pelos colegas) |
| **Endereço** | https://prazo-certo-rouge.vercel.app |
| **Período dos testes** | __/__/2026 a __/__/2026 |
| **Responsável** | Alex Lima |

## 1. Objetivo
Registrar os erros encontrados no sistema, a gravidade de cada um, a correção feita e a evidência
de antes e depois, conforme pedido na Situação 3.

## 2. Como os testes foram feitos
1. **Testes automatizados** (pytest): 93 testes de unidade e de integração, em SQLite e PostgreSQL. Ver [verificação e validação](verificacao-e-validacao.md).
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
| E01 | Texto "1 atrasada(s)" e "0 de 0 tarefas concluídas" em projeto sem tarefas | Baixa | Lista de projetos e página do projeto | Plural automático e texto "Nenhuma tarefa ainda" | commit `725c03e` | ✅ Corrigido |
| E02 | Com `DATABASE_URL` vazio no `.env`, o sistema não iniciava | Média | Configuração | Variável vazia passa a usar o SQLite padrão | commit `4a6e5ad` | ✅ Corrigido |
| E03 | O endereço do PostgreSQL entregue pela hospedagem (`postgresql://`) não usaria o driver instalado (identificado antes do primeiro deploy) | Alta (só em produção) | Configuração | Função `normalizar_url_do_banco` + 5 testes em `test_config.py` | commit `f4c3b22` | ✅ Corrigido |
| E04 | No Render grátis, o site "dormia" após 15 min (primeiro acesso com ~50 s de espera), o banco expiraria em 30 dias e uma publicação travou esperando aprovação manual | Média | Hospedagem | Mudança para Vercel + Neon (publica em segundos, não dorme, banco sem prazo) | commit `49816a3` | ✅ Corrigido |
| E05 | Na Vercel, a variável `APP_ENV` foi cadastrada com o valor errado ("productionproduction") e o site respondia erro 500 | Alta | Configuração da hospedagem | Variável corrigida; o erro foi achado nos logs da Vercel e o roteiro de testes foi repetido no site | logs da Vercel de 20/10/2026 | ✅ Corrigido |

### 4.2 Encontrados pelos colegas
| ID | Descrição | Quem encontrou | Gravidade | Correção | Evidência (antes / depois) | Status |
|---|---|---|---|---|---|---|
| C01 | | | | | | |
| C02 | | | | | | |
| C03 | | | | | | |

### 4.3 Sugestões de melhoria recebidas
| ID | Sugestão | Quem sugeriu | Decisão (fazer agora / depois / não fazer) e motivo |
|---|---|---|---|
| S01 | | | |
| S02 | | | |

## 5. Funcionalidades não testadas pelos colegas
| Funcionalidade | Quantos não testaram | Motivo informado | Ação |
|---|---|---|---|
| | | | |

## 6. Indicadores
| Indicador | Valor |
|---|---|
| Testes automatizados | 93 passando, 0 falhando |
| Casos do roteiro de sistema | 18 de 18 passando |
| Colegas que testaram | _ de 5 |
| Nota média dos colegas | _ de 5 |
| Erros encontrados pelos colegas | _ (Alta: _ · Média: _ · Baixa: _) |
| Erros corrigidos | _ de _ |

## 7. Conclusão
_(Preencher depois das correções: o sistema atende ou não aos requisitos, o que foi corrigido e o que ficou para depois.)_
