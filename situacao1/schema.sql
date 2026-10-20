-- Prazo Certo — projeto físico do banco de dados (SQLite)
-- Em PostgreSQL/MySQL as tabelas são criadas pela aplicação (SQLAlchemy) com os tipos equivalentes.

PRAGMA foreign_keys = ON;

CREATE TABLE projeto (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nome          VARCHAR(100) NOT NULL,
    descricao     VARCHAR(500),
    criado_em     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_projeto_nome_nao_vazio CHECK (length(trim(nome)) > 0)
);

CREATE UNIQUE INDEX uq_projeto_nome ON projeto (lower(nome));

CREATE TABLE tarefa (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    projeto_id    INTEGER      NOT NULL,
    titulo        VARCHAR(150) NOT NULL,
    prazo         DATE,
    status        VARCHAR(10)  NOT NULL DEFAULT 'pendente',
    concluida_em  DATETIME,
    criado_em     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_tarefa_projeto FOREIGN KEY (projeto_id)
        REFERENCES projeto (id) ON DELETE CASCADE,
    CONSTRAINT ck_tarefa_titulo_nao_vazio CHECK (length(trim(titulo)) > 0),
    CONSTRAINT ck_tarefa_status CHECK (status IN ('pendente', 'concluida'))
);

CREATE INDEX ix_tarefa_projeto_id   ON tarefa (projeto_id);
CREATE INDEX ix_tarefa_status_prazo ON tarefa (status, prazo);

-- Consulta das tarefas atrasadas (requisito 5):
-- SELECT * FROM tarefa WHERE status = 'pendente' AND prazo IS NOT NULL AND prazo < date('now');

-- Progresso de cada projeto (requisito 4):
-- SELECT p.id, p.nome,
--        COUNT(t.id) AS total,
--        SUM(CASE WHEN t.status = 'concluida' THEN 1 ELSE 0 END) AS concluidas
-- FROM projeto p LEFT JOIN tarefa t ON t.projeto_id = p.id
-- GROUP BY p.id;
