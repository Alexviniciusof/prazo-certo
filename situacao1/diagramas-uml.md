# Diagramas UML — Prazo Certo

Diagramas do sistema como ele foi implementado. Os desenhos estão em Mermaid (o GitHub mostra
direto nesta página), e as imagens PNG ficam em [`diagramas/`](diagramas/) para colar no documento de entrega.

| # | Diagrama | O que mostra |
|---|---|---|
| 1 | [Casos de uso](#1-diagrama-de-casos-de-uso) | O que o usuário pode fazer no sistema |
| 2 | [Classes](#2-diagrama-de-classes) | Classes do sistema em camadas MVC |
| 3 | [Sequência](#3-diagramas-de-sequência) | A troca de mensagens entre as camadas em 3 operações |
| 4 | [Atividades](#4-diagramas-de-atividades) | O passo a passo de 3 fluxos, com as decisões |
| 5 | [Estados](#5-diagrama-de-estados-da-tarefa) | Os estados por que passa uma tarefa |
| 6 | [Componentes](#6-diagrama-de-componentes-arquitetura-mvc) | Como as partes do sistema se ligam |

O diagrama de classes de persistência e o DER estão em [modelo-de-dados.md](modelo-de-dados.md).

---

## 1. Diagrama de casos de uso

**Ator:** Usuário, a pessoa que organiza os próprios projetos e tarefas. O sistema tem um único tipo de usuário.

```mermaid
flowchart LR
    usuario(["👤 Usuário"])

    subgraph sistema["Sistema Prazo Certo"]
        direction TB
        uc01(["UC01 · Cadastrar projeto"])
        uc02(["UC02 · Listar projetos com progresso"])
        uc03(["UC03 · Editar projeto"])
        uc04(["UC04 · Excluir projeto"])
        uc05(["UC05 · Cadastrar tarefa"])
        uc06(["UC06 · Listar tarefas do projeto"])
        uc07(["UC07 · Editar tarefa"])
        uc08(["UC08 · Excluir tarefa"])
        uc09(["UC09 · Concluir ou desmarcar tarefa"])
        uc10(["UC10 · Filtrar tarefas atrasadas do projeto"])
        uc11(["UC11 · Ver atrasadas de todos os projetos"])
        inc1(["Calcular progresso"])
        inc2(["Excluir tarefas do projeto"])
    end

    usuario --- uc01
    usuario --- uc02
    usuario --- uc03
    usuario --- uc04
    usuario --- uc05
    usuario --- uc06
    usuario --- uc07
    usuario --- uc08
    usuario --- uc09
    usuario --- uc10
    usuario --- uc11

    uc02 -.->|«include»| inc1
    uc09 -.->|«include»| inc1
    uc04 -.->|«include»| inc2
    uc10 -.->|«extend»| uc06
```

> Observação: o Mermaid não tem um tipo próprio para casos de uso. As elipses são os casos de uso, as linhas
> contínuas ligam o ator, e as setas tracejadas são as relações «include» e «extend».

### Rastreabilidade: requisitos × casos de uso

| Requisito funcional | Casos de uso |
|---|---|
| RF1 — Cadastrar, listar, editar e excluir projetos | UC01, UC02, UC03, UC04 |
| RF2 — Cadastrar, listar, editar e excluir tarefas | UC05, UC06, UC07, UC08 |
| RF3 — Marcar e desmarcar tarefa como concluída | UC09 |
| RF4 — Mostrar o progresso de cada projeto | UC02, UC09 (Calcular progresso) |
| RF5 — Filtrar tarefas atrasadas | UC10, UC11 |
| RF6 — Excluir projeto exclui as tarefas | UC04 (Excluir tarefas do projeto) |
| RF7 — Mensagens claras de erro e confirmação | Todos (fluxos alternativos abaixo) |

### Descrição dos casos de uso

**UC01 — Cadastrar projeto**
- **Pré-condição:** nenhuma.
- **Fluxo principal:** 1. O usuário clica em "Novo projeto". 2. Informa o nome e, se quiser, a descrição. 3. Clica em "Criar projeto". 4. O sistema valida, salva e abre a página do projeto com "Projeto criado com sucesso."
- **Fluxos alternativos:** 4a. Nome vazio → "Informe o nome do projeto." · 4b. Nome já usado → "Já existe um projeto com esse nome." · 4c. Texto acima do limite → mensagem com o limite. Em todos, o formulário volta com o que foi digitado.
- **Pós-condição:** o projeto existe com 0% de progresso.

**UC02 — Listar projetos com progresso**
- **Fluxo principal:** 1. O usuário abre o sistema. 2. O sistema mostra os projetos em ordem alfabética, cada um com a barra de progresso (concluídas ÷ total) e a quantidade de atrasadas.
- **Fluxo alternativo:** 2a. Não há projetos → mensagem com o botão "Criar o primeiro projeto".

**UC03 — Editar projeto**
- **Pré-condição:** o projeto existe.
- **Fluxo principal:** 1. Na página do projeto, o usuário clica em "Editar". 2. Altera o nome ou a descrição. 3. Salva. 4. O sistema mostra "Projeto atualizado com sucesso."
- **Fluxos alternativos:** os mesmos de UC01, e manter o próprio nome não conta como repetido. Projeto inexistente → "Projeto não encontrado."

**UC04 — Excluir projeto**
- **Pré-condição:** o projeto existe.
- **Fluxo principal:** 1. O usuário clica em "Excluir". 2. O sistema pede confirmação, avisando que as tarefas também serão apagadas. 3. O usuário confirma. 4. O sistema exclui o projeto **e todas as suas tarefas** e volta para a lista com "Projeto e suas tarefas foram excluídos."
- **Fluxo alternativo:** 3a. O usuário cancela → nada muda.

**UC05 — Cadastrar tarefa**
- **Pré-condição:** o projeto existe.
- **Fluxo principal:** 1. Na página do projeto, o usuário digita o título e, se quiser, o prazo. 2. Clica em "Adicionar". 3. O sistema salva a tarefa como **pendente** e mostra "Tarefa criada com sucesso."
- **Fluxos alternativos:** 2a. Título vazio ou só com espaços → "Informe o título da tarefa." (aparece antes de enviar, pelo JavaScript, e é conferido de novo no servidor) · 2b. Prazo inválido → "Informe um prazo válido (dia/mês/ano)."

**UC06 — Listar tarefas do projeto**
- **Fluxo principal:** o sistema mostra primeiro as pendentes (pelo prazo mais próximo, sem prazo por último) e depois as concluídas. Cada tarefa mostra o prazo e, se for o caso, o selo "Atrasada".
- **Fluxo alternativo:** projeto sem tarefas → mensagem convidando a adicionar a primeira.

**UC07 — Editar tarefa**
- **Fluxo principal:** 1. O usuário clica em "Editar" na tarefa. 2. Altera o título ou o prazo. 3. Salva. 4. "Tarefa atualizada com sucesso."
- **Fluxos alternativos:** os mesmos de UC05.

**UC08 — Excluir tarefa**
- **Fluxo principal:** 1. O usuário clica em "Excluir" na tarefa. 2. Confirma. 3. O sistema exclui e mostra "Tarefa excluída."
- **Fluxo alternativo:** 2a. O usuário cancela → nada muda.

**UC09 — Concluir ou desmarcar tarefa**
- **Fluxo principal:** 1. O usuário clica no quadradinho da tarefa. 2. O sistema troca o status (pendente ↔ concluída), registra a data de conclusão e **recalcula o progresso**. 3. A tela se atualiza sem recarregar e mostra "Tarefa marcada como concluída." (ou "como pendente").
- **Fluxos alternativos:** 2a. Sem conexão → "Sem conexão com o servidor..." e nada muda na tela · 2b. Sem JavaScript → o formulário é enviado normalmente e a página recarrega com a mensagem.

**UC10 — Filtrar tarefas atrasadas do projeto** (estende UC06)
- **Fluxo principal:** 1. Na página do projeto, o usuário clica em "Atrasadas". 2. O sistema mostra só as tarefas **pendentes cujo prazo já passou**.
- **Fluxo alternativo:** nenhuma atrasada → "Nenhuma tarefa atrasada neste projeto."

**UC11 — Ver atrasadas de todos os projetos**
- **Fluxo principal:** 1. O usuário clica em "Atrasadas" no menu. 2. O sistema lista as atrasadas de todos os projetos, da mais atrasada para a menos atrasada, com o nome do projeto. 3. Ao concluir uma tarefa ali, ela sai da lista.

---

## 2. Diagrama de classes

Classes do código, separadas pelas camadas do MVC.

```mermaid
classDiagram
    direction TB

    namespace Model {
        class Projeto {
            +int id
            +str nome
            +str descricao
            +datetime criado_em
            +datetime atualizado_em
            +list~Tarefa~ tarefas
            +total_tarefas() int
            +tarefas_concluidas() int
            +progresso() int
            +total_atrasadas(hoje) int
        }
        class Tarefa {
            +int id
            +int projeto_id
            +str titulo
            +date prazo
            +str status
            +datetime concluida_em
            +concluida() bool
            +concluir()
            +reabrir()
            +esta_atrasada(hoje) bool
        }
        class servicos {
            <<módulo>>
            +criar_projeto(nome, descricao) Projeto
            +editar_projeto(id, nome, descricao) Projeto
            +excluir_projeto(id)
            +listar_projetos() list
            +obter_projeto(id) Projeto
            +criar_tarefa(projeto_id, titulo, prazo) Tarefa
            +editar_tarefa(id, titulo, prazo) Tarefa
            +excluir_tarefa(id)
            +alternar_tarefa(id) Tarefa
            +listar_tarefas(projeto_id, apenas_atrasadas, hoje) list
            +listar_tarefas_atrasadas(hoje) list
        }
        class ErroNegocio {
            +str mensagem
        }
        class ErroValidacao
        class ErroNaoEncontrado
    }

    namespace Controller {
        class ProjetosController {
            <<blueprint /projetos>>
            +listar()
            +novo()
            +criar()
            +detalhar(id)
            +editar(id)
            +atualizar(id)
            +excluir(id)
            +criar_tarefa(id)
        }
        class TarefasController {
            <<blueprint /tarefas>>
            +atrasadas()
            +editar(id)
            +atualizar(id)
            +alternar(id)
            +excluir(id)
        }
        class TratamentoDeErros {
            +nao_encontrado() 404
            +erro_de_banco() 500
            +erro_inesperado() 500
        }
    }

    Projeto "1" *-- "0..*" Tarefa : possui
    ErroNegocio <|-- ErroValidacao
    ErroNegocio <|-- ErroNaoEncontrado
    servicos ..> Projeto : usa
    servicos ..> Tarefa : usa
    servicos ..> ErroNegocio : lança
    ProjetosController ..> servicos : chama
    TarefasController ..> servicos : chama
    TratamentoDeErros ..> ErroNaoEncontrado : trata
```

---

## 3. Diagramas de sequência

### 3.1 Cadastrar tarefa (UC05)

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuário
    participant V as Navegador<br/>(View + JavaScript)
    participant C as ProjetosController
    participant S as servicos (Model)
    participant DB as Banco de dados

    U->>V: Digita título e prazo e clica em "Adicionar"
    V->>V: Confere se o título não está vazio
    alt título vazio
        V-->>U: "Informe o título da tarefa." (sem enviar)
    else título preenchido
        V->>C: POST /projetos/{id}/tarefas
        C->>S: criar_tarefa(id, titulo, prazo)
        S->>DB: SELECT projeto WHERE id = {id}
        DB-->>S: projeto
        S->>S: valida título e converte o prazo
        alt dados inválidos
            S-->>C: ErroValidacao(mensagem)
            C-->>V: 400 + página com a mensagem e os dados digitados
            V-->>U: Mostra o erro em vermelho
        else dados válidos
            S->>DB: INSERT INTO tarefa (status = 'pendente')
            S->>DB: COMMIT
            S-->>C: tarefa
            C-->>V: 302 → /projetos/{id} + "Tarefa criada com sucesso."
            V->>C: GET /projetos/{id}
            C-->>V: Página com a nova tarefa
            V-->>U: Mostra a tarefa e a mensagem verde
        end
    end
```

### 3.2 Concluir tarefa sem recarregar a página (UC09)

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuário
    participant V as Navegador<br/>(JavaScript)
    participant C as TarefasController
    participant S as servicos (Model)
    participant DB as Banco de dados

    U->>V: Clica no quadradinho da tarefa
    V->>C: fetch POST /tarefas/{id}/alternar<br/>(Accept: application/json)
    C->>S: alternar_tarefa(id)
    S->>DB: SELECT tarefa WHERE id = {id}
    DB-->>S: tarefa (pendente)
    S->>S: tarefa.concluir()<br/>status = 'concluida', concluida_em = agora
    S->>DB: UPDATE tarefa + COMMIT
    S-->>C: tarefa
    C->>C: calcula progresso e atrasadas do projeto
    C-->>V: 200 JSON {status, progresso, atrasadas, mensagem}
    V->>V: Risca a tarefa, atualiza a barra e os números
    V-->>U: "Tarefa marcada como concluída."

    opt falha no banco
        S->>DB: ROLLBACK
        C-->>V: 500 JSON {mensagem: "Algo deu errado..."}
        V-->>U: Mensagem vermelha, a tela não muda
    end
```

### 3.3 Excluir projeto com suas tarefas (UC04)

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuário
    participant V as Navegador<br/>(View + JavaScript)
    participant C as ProjetosController
    participant S as servicos (Model)
    participant DB as Banco de dados

    U->>V: Clica em "Excluir" no projeto
    V-->>U: "Excluir o projeto e todas as suas tarefas?"
    alt usuário cancela
        U->>V: Cancelar
        V-->>U: Nada muda
    else usuário confirma
        U->>V: OK
        V->>C: POST /projetos/{id}/excluir
        C->>S: excluir_projeto(id)
        S->>DB: SELECT projeto WHERE id = {id}
        alt projeto não existe
            S-->>C: ErroNaoEncontrado
            C-->>V: 404 "Projeto não encontrado."
        else projeto existe
            S->>DB: DELETE FROM projeto WHERE id = {id}
            Note over DB: ON DELETE CASCADE apaga<br/>as tarefas do projeto
            S->>DB: COMMIT
            C-->>V: 302 → /projetos + "Projeto e suas tarefas foram excluídos."
            V-->>U: Lista de projetos sem o projeto excluído
        end
    end
```

---

## 4. Diagramas de atividades

### 4.1 Cadastrar tarefa

```mermaid
flowchart TD
    inicio((●)) --> a1[Abrir a página do projeto]
    a1 --> a2[Digitar o título e, se quiser, o prazo]
    a2 --> a3[Clicar em Adicionar]
    a3 --> d1{Título preenchido?}
    d1 -- Não --> e1[Mostrar 'Informe o título da tarefa.'<br/>embaixo do campo]
    e1 --> a2
    d1 -- Sim --> a4[Enviar ao servidor]
    a4 --> d2{Projeto existe?}
    d2 -- Não --> e2[Mostrar 'Projeto não encontrado.']
    e2 --> fim1((◉))
    d2 -- Sim --> d3{Título até 150 caracteres<br/>e prazo válido?}
    d3 -- Não --> e3[Voltar o formulário com a mensagem<br/>e o que foi digitado]
    e3 --> a2
    d3 -- Sim --> a5[Salvar a tarefa como pendente]
    a5 --> d4{Banco gravou?}
    d4 -- Não --> e4[Desfazer e mostrar<br/>'Algo deu errado. Tente novamente.']
    e4 --> fim1
    d4 -- Sim --> a6[Mostrar a tarefa na lista<br/>e 'Tarefa criada com sucesso.']
    a6 --> fim2((◉))
```

### 4.2 Concluir ou desmarcar tarefa

```mermaid
flowchart TD
    inicio((●)) --> a1[Clicar no quadradinho da tarefa]
    a1 --> a2[Bloquear o botão e enviar o pedido]
    a2 --> d1{Servidor respondeu?}
    d1 -- Não --> e1[Mostrar 'Sem conexão com o servidor']
    e1 --> a9[Liberar o botão]
    d1 -- Sim --> d2{Status atual}
    d2 -- Pendente --> a3[Marcar como concluída<br/>e guardar a data de conclusão]
    d2 -- Concluída --> a4[Voltar para pendente<br/>e apagar a data de conclusão]
    a3 --> a5[Recalcular progresso e atrasadas]
    a4 --> a5
    a5 --> a6[Atualizar a tarefa, a barra e os números na tela]
    a6 --> d3{Está na lista de atrasadas<br/>e foi concluída?}
    d3 -- Sim --> a7[Retirar a tarefa da lista]
    d3 -- Não --> a8[Mostrar a mensagem de sucesso]
    a7 --> a8
    a8 --> a9
    a9 --> fim((◉))
```

### 4.3 Excluir projeto

```mermaid
flowchart TD
    inicio((●)) --> a1[Abrir o projeto e clicar em Excluir]
    a1 --> a2[Sistema pergunta se quer excluir<br/>o projeto e todas as tarefas]
    a2 --> d1{Usuário confirma?}
    d1 -- Não --> fim1((◉))
    d1 -- Sim --> a3[Enviar a exclusão ao servidor]
    a3 --> d2{Projeto existe?}
    d2 -- Não --> e1[Mostrar 'Projeto não encontrado.']
    e1 --> fim1
    d2 -- Sim --> par[[Em uma única transação]]
    par --> a4[Excluir as tarefas do projeto]
    par --> a5[Excluir o projeto]
    a4 --> j[[Confirmar a transação]]
    a5 --> j
    j --> a6[Voltar para a lista de projetos<br/>com 'Projeto e suas tarefas foram excluídos.']
    a6 --> fim2((◉))
```

---

## 5. Diagrama de estados da tarefa

O status gravado é só **pendente** ou **concluída**. "No prazo" e "atrasada" são calculados na hora,
comparando o prazo com a data de hoje.

```mermaid
stateDiagram-v2
    direction LR
    [*] --> Pendente : cadastrar tarefa

    state Pendente {
        direction LR
        [*] --> NoPrazo
        NoPrazo : No prazo (ou sem prazo)
        Atrasada : Atrasada
        NoPrazo --> Atrasada : o prazo passou
        Atrasada --> NoPrazo : prazo alterado para hoje ou depois
    }

    Pendente --> Concluida : marcar como concluída
    Concluida --> Pendente : desmarcar
    Concluida : Concluída
    Concluida : guarda a data de conclusão

    Pendente --> [*] : excluir tarefa ou projeto
    Concluida --> [*] : excluir tarefa ou projeto
```

---

## 6. Diagrama de componentes (arquitetura MVC)

```mermaid
flowchart LR
    subgraph cliente["Navegador"]
        html["Páginas HTML"]
        css["estilo.css"]
        js["app.js<br/>(validação, confirmação,<br/>concluir sem recarregar)"]
    end

    subgraph servidor["Servidor Python (Flask + gunicorn)"]
        subgraph controller["Controller"]
            rp["projetos.py"]
            rt["tarefas.py"]
            re["erros.py"]
        end
        subgraph view["View"]
            tpl["templates Jinja2"]
        end
        subgraph model["Model"]
            sv["servicos.py<br/>(regras de negócio)"]
            md["Projeto · Tarefa<br/>(SQLAlchemy)"]
        end
        cfg["config.py<br/>(variáveis de ambiente)"]
    end

    banco[("PostgreSQL (produção)<br/>SQLite (desenvolvimento)")]

    html -- "requisição HTTP" --> rp & rt
    js -- "fetch (JSON)" --> rt
    rp & rt --> sv
    sv --> md
    md -- "SQL" --> banco
    rp & rt --> tpl
    tpl -- "HTML" --> html
    re -. "trata erros de" .-> rp & rt
    cfg -. "DATABASE_URL" .-> md
```
