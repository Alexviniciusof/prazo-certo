# Mapa conceitual — Prazo Certo

Num mapa conceitual, cada caixa é um **conceito** e cada seta é lida como uma frase:
**conceito → palavra de ligação → conceito**. Por exemplo: "Projeto **possui** Tarefas".

As imagens em PNG ficam em [`diagramas/`](diagramas/).

## 1. Mapa conceitual do sistema

Mostra as ideias principais do Prazo Certo e como elas se relacionam.

![Mapa conceitual](diagramas/11-mapa-conceitual.png)

<details>
<summary>Código do diagrama (Mermaid)</summary>

```mermaid
flowchart TD
    sistema(["<b>Prazo Certo</b><br/>sistema web de tarefas"])
    usuario(["Usuário"])
    projeto(["Projeto"])
    tarefa(["Tarefa"])
    nome(["Nome<br/>(obrigatório e único)"])
    descricao(["Descrição<br/>(opcional)"])
    titulo(["Título<br/>(obrigatório)"])
    prazo(["Prazo<br/>(opcional)"])
    status(["Status"])
    pendente(["Pendente"])
    concluida(["Concluída"])
    atrasada(["Atrasada"])
    progresso(["Progresso<br/>(% concluídas ÷ total)"])
    hoje(["Data de hoje"])
    mensagens(["Mensagens<br/>de sucesso e de erro"])
    exclusao(["Exclusão em cascata"])

    sistema -->|é usado pelo| usuario
    usuario -->|cadastra, edita e exclui| projeto
    usuario -->|marca e desmarca| tarefa
    usuario -->|recebe| mensagens
    projeto -->|possui 0 ou mais| tarefa
    projeto -->|é identificado pelo| nome
    projeto -->|pode ter uma| descricao
    projeto -->|mostra o seu| progresso
    tarefa -->|é identificada pelo| titulo
    tarefa -->|pode ter um| prazo
    tarefa -->|tem um| status
    status -->|pode ser| pendente
    status -->|pode ser| concluida
    progresso -->|é calculado contando as| concluida
    pendente -->|vira| atrasada
    prazo -->|quando é anterior à| hoje
    hoje -.->|define se a pendente é| atrasada
    projeto -->|ao ser excluído aciona a| exclusao
    exclusao -->|apaga as| tarefa
    mensagens -->|explicam o resultado de cada ação, sem| erro_tecnico(["Erro técnico"])

    classDef central fill:#0f766e,color:#fff,stroke:#0b5e58
    classDef entidade fill:#d6f1ee,stroke:#0f766e,color:#1c2430
    classDef regra fill:#fef0db,stroke:#b54708,color:#1c2430
    classDef negado fill:#fde8e6,stroke:#b42318,color:#1c2430
    class sistema central
    class usuario,projeto,tarefa entidade
    class atrasada,progresso,exclusao regra
    class erro_tecnico negado
```

</details>

**Como ler alguns caminhos do mapa:**
- Usuário → *cadastra* → Projeto → *possui 0 ou mais* → Tarefas.
- Tarefa → *tem um* → Status → *pode ser* → Pendente → *vira* → Atrasada, quando o prazo é anterior à data de hoje.
- Projeto → *mostra o seu* → Progresso → *é calculado contando as* → Concluídas.
- Projeto → *ao ser excluído aciona a* → Exclusão em cascata → *apaga as* → Tarefas.

## 2. Mapa de navegação (IHC)

Mostra as telas do sistema e como o usuário passa de uma para outra.

![Mapa de navegação](diagramas/12-mapa-de-navegacao.png)

<details>
<summary>Código do diagrama (Mermaid)</summary>

```mermaid
flowchart LR
    lista["📋 Lista de projetos"]
    form_p["📝 Novo ou editar projeto"]
    detalhe["📁 Página do projeto<br/>tarefas · progresso · filtro"]
    form_t["✏️ Editar tarefa"]
    atrasadas["⏰ Tarefas atrasadas<br/>de todos os projetos"]
    avaliacao["⭐ Avaliar o sistema"]
    obrigado["🙌 Avaliação enviada"]
    erro["⚠️ Página de erro"]

    lista -->|botão Novo projeto| form_p
    lista -->|clicar no cartão| detalhe
    form_p -->|salvar| detalhe
    detalhe -->|Editar| form_p
    detalhe -->|Editar na tarefa| form_t
    form_t -->|salvar ou cancelar| detalhe
    detalhe -->|Excluir e confirmar| lista
    lista -->|menu Atrasadas| atrasadas
    atrasadas -->|menu Projetos| lista
    atrasadas -->|nome do projeto| detalhe
    lista -.->|link no rodapé| avaliacao
    avaliacao -->|enviar| obrigado
    obrigado -->|voltar ao sistema| lista
    erro -->|voltar para os projetos| lista
```

</details>

Na página do projeto, **adicionar, concluir e excluir tarefas** acontece na própria tela, sem trocar de página.

### Mensagens de cada tela

| Tela | Sucesso (verde, some sozinha) | Erro (vermelho, fica até fechar) | Confirmação antes de apagar |
|---|---|---|---|
| Novo ou editar projeto | "Projeto criado com sucesso." · "Projeto atualizado com sucesso." | "Informe o nome do projeto." · "Já existe um projeto com esse nome." · limite de caracteres | — |
| Página do projeto | "Tarefa criada com sucesso." · "Tarefa marcada como concluída." / "como pendente." · "Tarefa excluída." · "Projeto e suas tarefas foram excluídos." | "Informe o título da tarefa." · "Informe um prazo válido (dia/mês/ano)." · "Sem conexão com o servidor..." | "Excluir o projeto e todas as suas tarefas?" · "Excluir a tarefa?" |
| Editar tarefa | "Tarefa atualizada com sucesso." | "Informe o título da tarefa." · "Informe um prazo válido (dia/mês/ano)." | — |
| Tarefas atrasadas | "Tarefa marcada como concluída." (e ela sai da lista) | "Sem conexão com o servidor..." | — |
| Avaliar o sistema | Página "Avaliação enviada. Muito obrigado!" | "Informe o seu nome." · "Conte o que você testou e funcionou." · "A data do teste não pode estar no futuro." · print inválido ou grande demais | — |
| Página de erro | — | "Projeto não encontrado." · "Tarefa não encontrada." · "Página não encontrada." · "Algo deu errado. Tente novamente em instantes." | — |

## 3. Princípios de IHC aplicados

Os princípios do material da disciplina e onde eles aparecem no sistema:

| Princípio | Onde aparece no Prazo Certo |
|---|---|
| **Clara** | Rótulos simples ("Nova tarefa", "Prazo (opcional)"), campo obrigatório marcado com * |
| **Consistente** | Mesmo layout, botões e cores em todas as telas; verde = sucesso, vermelho = erro/excluir, laranja = atraso |
| **Simples** | Só 2 itens no menu; o cadastro de tarefa fica na própria página do projeto |
| **Controlada pelo usuário** | Nada é apagado sem confirmação; o usuário escolhe o filtro "Todas" / "Atrasadas" |
| **Direta** | Clicar no quadradinho conclui a tarefa e a barra de progresso muda na hora |
| **Recuperável** | Tarefa concluída pode ser desmarcada; em erro de formulário, o que foi digitado não se perde |
| **Dá resposta** | Toda ação mostra uma mensagem; botão fica bloqueado enquanto salva |
| **Esteticamente agradável** | Cartões, barra de progresso, modo escuro e layout para celular |
