# Verificação e validação

Seguindo o **Modelo V** do material da disciplina: cada nível de desenvolvimento tem um nível de teste.

| Desenvolvimento | Teste correspondente | Como foi feito no Prazo Certo | Resultado |
|---|---|---|---|
| Código | **Teste unitário** | pytest nas regras de negócio (`test_projetos.py`, `test_tarefas.py`, `test_avaliacoes.py` – classe `TestRegras`, `test_config.py`) | ✅ passando |
| Arquitetura | **Teste de integração** | pytest nas rotas: controller + model + banco + template (`test_rotas.py`, `test_avaliacoes.py` – classe `TestRotas`), em SQLite e em PostgreSQL | ✅ passando |
| Análise | **Teste de sistema** | [Roteiro de testes](roteiro-de-testes.md) executado no sistema publicado | ✅ 18 de 18 |
| Requisitos | **Teste de aceitação** | 5 colegas usando o sistema e preenchendo o [formulário](README.md#formulário-de-avaliação) | ⏳ aguardando os colegas |

## Verificação: "estamos construindo o sistema do jeito certo?"

- **TDD:** os testes foram escritos antes do código (commit `350973f`), depois o código foi feito até todos passarem (commit `4a6e5ad`).
- **Testes automatizados:** **93 testes**, rodando em menos de 1 segundo.
  ```
  $ pytest
  ============================== 93 passed ==============================
  ```
- **Os mesmos testes no PostgreSQL** (o banco de produção): `TEST_DATABASE_URL=postgresql://... pytest` → todos passando.
- **Testes no deploy:** o Render roda `pytest` antes de publicar. Se algum teste falhar, a versão nova não entra no ar.
- **Revisão contra a documentação:** as regras do [dicionário de dados](../situacao1/dicionario-de-dados.md)
  (tamanhos, campos obrigatórios, nome único, cascata) têm um teste cada.

### Casos obrigatórios pedidos para os testes automatizados

| Caso | Teste |
|---|---|
| Criar projeto e tarefa | `test_criar_projeto_com_nome_e_descricao`, `test_criar_tarefa_em_um_projeto` |
| Não permitir tarefa sem título | `test_nao_permite_tarefa_sem_titulo` (vazio, só espaços e nulo) |
| Marcar tarefa como concluída | `TestConcluir` (concluir, desmarcar, alternar) |
| Calcular o progresso do projeto | `TestProgresso` (0%, 33%, 50%, 100% e reabrir) |
| Listar só tarefas atrasadas | `TestAtrasadas` (vencida, vence hoje, sem prazo, concluída, de todos os projetos) |
| Excluir projeto com suas tarefas | `test_excluir_projeto_exclui_tambem_as_suas_tarefas` |

## Validação: "estamos construindo o sistema certo?"

- **Requisitos × casos de uso × testes:** cada requisito (RF1–RF7) está ligado a casos de uso na
  [rastreabilidade](../situacao1/diagramas-uml.md#rastreabilidade-requisitos--casos-de-uso), e cada caso de uso tem casos de teste no [roteiro](roteiro-de-testes.md).
- **Validação com usuários:** 5 colegas testam o sistema publicado e respondem ao formulário.
  As respostas estão no [registro dos testes](registro-dos-testes.md) e os problemas no [laudo de qualidade](laudo-de-qualidade.md).
