# Prazo Certo — como instalar, rodar, testar e usar

Sistema web de lista de tarefas por projeto: cadastre projetos, adicione tarefas, marque o que
já foi feito e acompanhe o progresso e os atrasos.

**Tecnologias:** Python 3.10+ · Flask 3 (MVC) · SQLAlchemy · SQLite (ou PostgreSQL/MySQL) ·
HTML, CSS e JavaScript puros · pytest

---

## 1. Instalação

Pré-requisitos: **Python 3.10 ou mais novo** e **Git**. Para conferir a versão do Python: `python3 --version`.

```bash
# 1) Baixe o projeto e entre na pasta do código
git clone <link-do-repositório> projeto-tarefas
cd projeto-tarefas/situacao2

# 2) Crie e ative um ambiente virtual (isola as bibliotecas do projeto)
python3 -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows (PowerShell ou CMD)

# 3) Instale as dependências
pip install -r requirements.txt

# 4) Crie o arquivo de configuração a partir do exemplo
cp .env.example .env               # macOS / Linux
# copy .env.example .env           # Windows
```

O `.env` pode ficar como está para rodar em desenvolvimento. Ele **não vai para o Git**.

## 2. Rodar

```bash
flask --app run run
```

Abra **http://127.0.0.1:5000** no navegador. Para parar o servidor, aperte `Ctrl + C`.

O banco SQLite é criado sozinho na primeira execução, em `instance/prazo_certo.db`.

**Dados de exemplo** (opcional, útil para demonstração). Cria 3 projetos com tarefas:

```bash
flask --app run popular-exemplo
```

**Abrir em outro aparelho da mesma rede** (por exemplo, no celular):

```bash
flask --app run run --host 0.0.0.0
```

E acesse `http://<IP-do-computador>:5000`.

## 3. Testar

```bash
pytest
```

São **66 testes automatizados** em `tests/`, e cada um usa um banco novo, em memória:

| Arquivo | O que testa |
|---|---|
| `test_projetos.py` | Criar, listar, editar e excluir projetos; nome obrigatório e único; excluir projeto apaga as tarefas; cálculo do progresso |
| `test_tarefas.py` | Criar tarefa; não aceitar tarefa sem título; prazo válido; concluir e desmarcar; ordem da lista; listar só as atrasadas |
| `test_rotas.py` | Páginas e formulários: mensagens de sucesso e de erro, filtro de atrasadas, resposta JSON para o JavaScript, página 404 e erro de banco sem mostrar detalhe técnico |

Resultado esperado: `66 passed`.

## 4. Configuração (variáveis de ambiente)

Nenhuma senha ou chave fica no código. Tudo vem do arquivo `.env` (ou das variáveis do servidor):

| Variável | Para que serve | Padrão |
|---|---|---|
| `APP_ENV` | `development` ou `production` | `development` |
| `SECRET_KEY` | Chave que protege as mensagens da sessão. **Obrigatória em produção** | gerada sozinha em desenvolvimento |
| `DATABASE_URL` | Endereço do banco de dados | SQLite em `instance/prazo_certo.db` |

Para gerar uma `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Trocar SQLite por PostgreSQL ou MySQL

1. Instale o driver do banco:
   - PostgreSQL: `pip install "psycopg[binary]"`
   - MySQL: `pip install PyMySQL`
2. Crie um banco vazio chamado `prazo_certo`.
3. Ajuste o `DATABASE_URL` no `.env`:

```
DATABASE_URL=postgresql+psycopg://usuario:senha@localhost:5432/prazo_certo
DATABASE_URL=mysql+pymysql://usuario:senha@localhost:3306/prazo_certo
```

As tabelas são criadas automaticamente quando o sistema inicia. Não é preciso mudar nada no código.

### Rodar em produção

```bash
pip install gunicorn
APP_ENV=production SECRET_KEY=<sua-chave> DATABASE_URL=<seu-banco> gunicorn "run:app"
```

## 5. Manual de uso

### Tela inicial: Projetos
![Lista de projetos](../situacao1/prototipo/1-lista-de-projetos.png)

- Cada cartão mostra o **nome**, a **descrição**, a **barra de progresso** (tarefas concluídas sobre o total) e quantas tarefas estão **atrasadas**.
- Clique em um cartão para abrir o projeto.
- **+ Novo projeto** abre o cadastro.

### Cadastrar ou editar um projeto
![Cadastro de projeto](../situacao1/prototipo/5-novo-projeto.png)

- **Nome** é obrigatório (até 100 caracteres) e não pode repetir o nome de outro projeto.
- **Descrição** é opcional (até 500 caracteres). O contador embaixo mostra quantos caracteres faltam.
- Clique em **Criar projeto** ou **Salvar alterações**. Se faltar algo, a mensagem aparece embaixo do campo e o que você digitou não se perde.

### Tarefas de um projeto
![Tarefas do projeto](../situacao1/prototipo/2-tarefas-do-projeto.png)

- **Adicionar tarefa:** escreva o título (obrigatório), escolha um prazo se quiser e clique em **Adicionar**.
- **Concluir:** clique no quadradinho à esquerda da tarefa. Ela fica riscada e o progresso se atualiza na hora. Clique de novo para **desmarcar**.
- **Atrasada:** tarefa pendente cujo prazo já passou. Ganha uma faixa laranja e o selo "Atrasada". Tarefa sem prazo nunca fica atrasada.
- **Filtro:** use **Todas** / **Atrasadas** para ver só as tarefas atrasadas do projeto.
- **Editar** muda o título e o prazo. **Excluir** pede confirmação antes de apagar.
- A lista mostra primeiro as pendentes, pelo prazo mais próximo, e as concluídas no fim.
- **Editar** e **Excluir** no topo servem para o projeto. Ao excluir um projeto, **todas as suas tarefas também são apagadas** (o sistema avisa antes).

### Tarefas atrasadas de todos os projetos
![Tarefas atrasadas](../situacao1/prototipo/4-tarefas-atrasadas.png)

- Acesse pelo menu **Atrasadas**, no topo.
- Mostra as tarefas atrasadas de todos os projetos, da mais atrasada para a menos atrasada.
- Ao concluir uma tarefa aqui, ela sai da lista.

### Mensagens do sistema
- **Verde:** a ação deu certo (ex.: "Tarefa criada com sucesso."). Some sozinha depois de alguns segundos.
- **Vermelha:** algo precisa ser corrigido (ex.: "Informe o título da tarefa.") ou houve um problema. Fica na tela até você fechar.
- Erros internos nunca mostram detalhes técnicos. O usuário vê "Algo deu errado. Tente novamente em instantes." e o detalhe fica só no log do servidor.

### Celular e modo escuro
O sistema se adapta à tela do celular e usa o modo escuro automaticamente quando o aparelho está nele.

| Celular | Modo escuro |
|---|---|
| ![Celular](../situacao1/prototipo/3-celular.png) | ![Modo escuro](../situacao1/prototipo/8-modo-escuro.png) |

## 6. Arquitetura (MVC)

```
situacao2/
├── run.py                  ponto de entrada (flask --app run run)
├── app/
│   ├── __init__.py         cria a aplicação (application factory)
│   ├── config.py           configurações lidas do ambiente
│   ├── comandos.py         comando popular-exemplo
│   ├── models/             MODEL: tabelas e regras de negócio
│   │   ├── projeto.py      tabela projeto + cálculo do progresso
│   │   ├── tarefa.py       tabela tarefa + regra de atraso
│   │   ├── servicos.py     validações e operações (criar, editar, excluir, concluir...)
│   │   ├── erros.py        erros de negócio com mensagem para o usuário
│   │   └── banco.py        conexão SQLAlchemy
│   ├── controllers/        CONTROLLER: rotas, recebe a requisição e escolhe a resposta
│   │   ├── projetos.py
│   │   ├── tarefas.py
│   │   └── erros.py        tratamento central de erros (404, 500, banco)
│   ├── templates/          VIEW: páginas HTML (Jinja2)
│   └── static/             CSS e JavaScript
└── tests/                  testes automatizados (pytest)
```

Fluxo de uma requisição: **navegador → controller → model (servicos) → banco → controller → template (view) → HTML**.

### Rotas

| Método | Endereço | O que faz |
|---|---|---|
| GET | `/` | Redireciona para `/projetos` |
| GET | `/projetos` | Lista os projetos |
| GET | `/projetos/novo` | Formulário de novo projeto |
| POST | `/projetos` | Cria um projeto |
| GET | `/projetos/<id>` | Tarefas do projeto (`?filtro=atrasadas` mostra só as atrasadas) |
| GET / POST | `/projetos/<id>/editar` | Edita o projeto |
| POST | `/projetos/<id>/excluir` | Exclui o projeto e suas tarefas |
| POST | `/projetos/<id>/tarefas` | Cria uma tarefa no projeto |
| GET | `/tarefas/atrasadas` | Tarefas atrasadas de todos os projetos |
| GET / POST | `/tarefas/<id>/editar` | Edita a tarefa |
| POST | `/tarefas/<id>/alternar` | Conclui ou desmarca (responde JSON se pedido com `Accept: application/json`) |
| POST | `/tarefas/<id>/excluir` | Exclui a tarefa |

A documentação do banco (diagramas, modelo lógico e dicionário de dados) está em [`../situacao1`](../situacao1).

## 7. Problemas comuns

| Problema | Solução |
|---|---|
| `command not found: flask` | O ambiente virtual não está ativo. Rode `source .venv/bin/activate` (ou `.venv\Scripts\activate` no Windows) |
| `Address already in use` | A porta 5000 está ocupada (no macOS, pelo AirPlay). Use outra: `flask --app run run --port 5050` |
| `Defina a variável de ambiente SECRET_KEY` | Em produção a chave é obrigatória. Coloque `SECRET_KEY=...` no `.env` |
| Quero começar do zero | Apague o arquivo `instance/prazo_certo.db` e rode o sistema de novo |
