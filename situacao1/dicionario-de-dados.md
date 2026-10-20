# Dicionário de dados — Prazo Certo

Legenda: **PK** = chave primária · **FK** = chave estrangeira · **NN** = não nulo (obrigatório) · **UQ** = único

## Tabela `projeto`
Guarda os projetos do usuário.

| Campo | Tipo (SQLite) | Tamanho | Restrições | Domínio / valores válidos | Valor padrão | Descrição |
|---|---|---|---|---|---|---|
| `id` | INTEGER | — | PK, NN, autoincremento | inteiro > 0 | gerado pelo banco | Identificador do projeto |
| `nome` | VARCHAR | 100 | NN, UQ | texto de 1 a 100 caracteres, sem espaços nas pontas | — | Nome do projeto. Ex.: "TCC" |
| `descricao` | VARCHAR | 500 | — | texto de até 500 caracteres ou vazio | NULL | Descrição opcional do projeto |
| `criado_em` | DATETIME | — | NN | data e hora válidas | data e hora atuais | Quando o projeto foi cadastrado |
| `atualizado_em` | DATETIME | — | NN | data e hora ≥ `criado_em` | data e hora atuais | Última alteração do projeto |

## Tabela `tarefa`
Guarda as tarefas, cada uma ligada a um projeto.

| Campo | Tipo (SQLite) | Tamanho | Restrições | Domínio / valores válidos | Valor padrão | Descrição |
|---|---|---|---|---|---|---|
| `id` | INTEGER | — | PK, NN, autoincremento | inteiro > 0 | gerado pelo banco | Identificador da tarefa |
| `projeto_id` | INTEGER | — | FK → `projeto.id`, NN, ON DELETE CASCADE | id de um projeto existente | — | Projeto ao qual a tarefa pertence |
| `titulo` | VARCHAR | 150 | NN | texto de 1 a 150 caracteres, sem espaços nas pontas | — | O que precisa ser feito. Ex.: "Escrever introdução" |
| `prazo` | DATE | — | — | data válida (AAAA-MM-DD) ou vazio | NULL | Data limite para concluir (opcional) |
| `status` | VARCHAR | 10 | NN, CHECK | `pendente` ou `concluida` | `pendente` | Situação da tarefa |
| `concluida_em` | DATETIME | — | — | data e hora, preenchida só quando `status = 'concluida'` | NULL | Quando a tarefa foi concluída |
| `criado_em` | DATETIME | — | NN | data e hora válidas | data e hora atuais | Quando a tarefa foi cadastrada |
| `atualizado_em` | DATETIME | — | NN | data e hora ≥ `criado_em` | data e hora atuais | Última alteração da tarefa |

## Relacionamentos
| Origem | Destino | Cardinalidade | Regra ao excluir |
|---|---|---|---|
| `tarefa.projeto_id` | `projeto.id` | N:1 (muitas tarefas para 1 projeto) | CASCADE: excluir o projeto exclui as tarefas |

## Campos calculados (não ficam no banco)
| Nome | Calculado a partir de | Regra |
|---|---|---|
| `progresso` (projeto) | `tarefa.status` das tarefas do projeto | concluídas ÷ total × 100, inteiro; 0% se não há tarefas |
| `atrasada` (tarefa) | `tarefa.prazo`, `tarefa.status` e a data de hoje | verdadeiro quando `prazo < hoje` e `status = 'pendente'` |

## Mensagens de validação ligadas aos campos
| Situação | Mensagem ao usuário |
|---|---|
| Projeto sem nome | "Informe o nome do projeto." |
| Nome com mais de 100 caracteres | "O nome do projeto pode ter no máximo 100 caracteres." |
| Nome repetido | "Já existe um projeto com esse nome." |
| Descrição com mais de 500 caracteres | "A descrição pode ter no máximo 500 caracteres." |
| Tarefa sem título | "Informe o título da tarefa." |
| Título com mais de 150 caracteres | "O título da tarefa pode ter no máximo 150 caracteres." |
| Prazo em formato inválido | "Informe um prazo válido (dia/mês/ano)." |
| Projeto ou tarefa não encontrado | "Projeto não encontrado." / "Tarefa não encontrada." |
| Erro inesperado no banco | "Não foi possível salvar agora. Tente novamente." |
