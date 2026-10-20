# Roteiro de testes do sistema

Casos de teste manuais, feitos no sistema publicado (https://prazo-certo.onrender.com) e no navegador.
Servem também de guia para os colegas. Cada caso aponta o requisito (RF) e o caso de uso (UC) que testa.

**Legenda do resultado:** ✅ passou · ❌ falhou · ⏳ ainda não executado

| ID | Requisito / UC | Passos | Resultado esperado | Resultado (20/10/2026) |
|---|---|---|---|---|
| CT01 | RF1 / UC01 | Clicar em "Novo projeto", informar nome "TCC" e salvar | Abre a página do projeto com "Projeto criado com sucesso." | ✅ |
| CT02 | RF1, RF7 / UC01 | Criar outro projeto com o mesmo nome | Formulário volta com "Já existe um projeto com esse nome." | ✅ |
| CT03 | RF1, RF7 / UC01 | Tentar salvar projeto com o nome vazio ou só com espaços | Mensagem "Informe o nome do projeto." embaixo do campo, sem enviar | ✅ |
| CT04 | RF1 / UC03 | Editar o nome e a descrição do projeto | "Projeto atualizado com sucesso." e os dados novos aparecem | ✅ |
| CT05 | RF2 / UC05 | Adicionar tarefa com título e prazo | Tarefa aparece na lista com "Tarefa criada com sucesso." | ✅ |
| CT06 | RF2, RF7 / UC05 | Adicionar tarefa sem título | "Informe o título da tarefa." e nada é criado | ✅ |
| CT07 | RF2 / UC07 | Editar título e prazo de uma tarefa | "Tarefa atualizada com sucesso." | ✅ |
| CT08 | RF3, RF4 / UC09 | Clicar no quadradinho de uma tarefa | Tarefa fica riscada, a barra e a % sobem sem recarregar a página | ✅ |
| CT09 | RF3, RF4 / UC09 | Clicar de novo na mesma tarefa | Volta para pendente e a % volta ao valor anterior | ✅ |
| CT10 | RF4 / UC02 | Projeto com 4 tarefas, 2 concluídas | Mostra 50% na lista de projetos e na página do projeto | ✅ |
| CT11 | RF5 / UC10 | Criar tarefa com prazo vencido e clicar em "Atrasadas" | Só aparecem as pendentes com prazo vencido, com o selo "Atrasada" | ✅ |
| CT12 | RF5 / UC11 | Abrir "Atrasadas" no menu e concluir uma tarefa ali | A tarefa sai da lista; sem atrasadas aparece "Tudo em dia!" | ✅ |
| CT13 | RF2 / UC08 | Excluir uma tarefa e confirmar | "Tarefa excluída." e ela some da lista | ✅ |
| CT14 | RF1, RF6 / UC04 | Excluir um projeto que tem tarefas e confirmar | Volta para a lista com "Projeto e suas tarefas foram excluídos."; o projeto e as tarefas somem | ✅ |
| CT15 | RF7 | Abrir um projeto que não existe (ex.: `/projetos/999999`) | Página "Projeto não encontrado." com botão para voltar, sem erro técnico | ✅ |
| CT16 | — | Abrir o sistema no celular | Layout se ajusta à tela, sem rolagem lateral | ✅ |
| CT17 | — | Usar o aparelho no modo escuro | Sistema aparece com cores escuras | ✅ |
| CT18 | Situação 3 | Enviar o formulário de avaliação com um print | Página "Avaliação enviada" e a avaliação aparece em `/avaliacoes?chave=...` | ✅ (local) |

**Como foram executados:** CT01 a CT15 foram executados no site publicado (Render + PostgreSQL),
por requisições HTTP e no navegador. CT16 e CT17 foram conferidos por capturas de tela (ver
`situacao1/prototipo/3-celular.png` e `8-modo-escuro.png`). CT18 foi executado na versão local e deve
ser repetido no site publicado.
