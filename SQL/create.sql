-- =========================
-- TABELA DE USUÁRIOS
-- =========================
CREATE TABLE IF NOT EXISTS usuarios (
    telegram_id BIGINT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- TABELA DE CORRIDAS
-- =========================
CREATE TABLE IF NOT EXISTS corridas (
    id SERIAL PRIMARY KEY,

    telegram_id BIGINT NOT NULL,

    tempo_minutos INTEGER NOT NULL CHECK (tempo_minutos > 0),
    distancia_km NUMERIC(6,2) NOT NULL CHECK (distancia_km > 0),
    passos INTEGER CHECK (passos >= 0),
    calorias INTEGER CHECK (calorias >= 0),

    pace NUMERIC(6,2) NOT NULL,

    data_corrida TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_corridas_usuario
        FOREIGN KEY (telegram_id)
        REFERENCES usuarios (telegram_id)
        ON DELETE CASCADE
);

-- =========================
-- ÍNDICES
-- =========================
CREATE INDEX IF NOT EXISTS idx_corridas_usuario
    ON corridas (telegram_id);

CREATE INDEX IF NOT EXISTS idx_corridas_data
    ON corridas (data_corrida);

CREATE INDEX IF NOT EXISTS idx_corridas_distancia
    ON corridas (distancia_km DESC);

CREATE INDEX IF NOT EXISTS idx_corridas_tempo
    ON corridas (tempo_minutos DESC);

-- =========================
-- VIEWS DE RANKING
-- =========================
CREATE OR REPLACE VIEW ranking_km AS
SELECT
    u.telegram_id,
    u.nome,
    ROUND(SUM(c.distancia_km), 2) AS total_km
FROM usuarios u
JOIN corridas c ON c.telegram_id = u.telegram_id
GROUP BY u.telegram_id, u.nome
ORDER BY total_km DESC;

CREATE OR REPLACE VIEW ranking_tempo AS
SELECT
    u.telegram_id,
    u.nome,
    SUM(c.tempo_minutos) AS tempo_total
FROM usuarios u
JOIN corridas c ON c.telegram_id = u.telegram_id
GROUP BY u.telegram_id, u.nome
ORDER BY tempo_total DESC;

-- =========================
-- VIEW MENSAL (RELATÓRIOS / IA)
-- =========================
CREATE OR REPLACE VIEW corridas_mensais AS
SELECT
    u.telegram_id,
    u.nome,
    DATE_TRUNC('month', c.data_corrida) AS mes,
    COUNT(*) AS total_treinos,
    ROUND(SUM(c.distancia_km), 2) AS km_total,
    SUM(c.tempo_minutos) AS tempo_total,
    ROUND(AVG(c.pace), 2) AS pace_medio
FROM usuarios u
JOIN corridas c ON c.telegram_id = u.telegram_id
GROUP BY u.telegram_id, u.nome, mes;


ALTER TABLE corridas
ADD COLUMN tempo_segundos INTEGER,
ADD COLUMN distancia_metros INTEGER,
ADD COLUMN pace_segundos INTEGER,
ADD COLUMN pace_origem VARCHAR(20);

SELECT * from corridas;

ALTER TABLE corridas
ALTER COLUMN tempo_segundos SET NOT NULL,
ALTER COLUMN distancia_metros SET NOT NULL,
ALTER COLUMN pace_segundos SET NOT NULL;

ALTER TABLE corridas
ADD CONSTRAINT chk_tempo_segundos CHECK (tempo_segundos > 0),
ADD CONSTRAINT chk_distancia_metros CHECK (distancia_metros > 0),
ADD CONSTRAINT chk_pace_segundos CHECK (pace_segundos > 0);

ALTER TABLE corridas
DROP COLUMN tempo_minutos,
DROP COLUMN distancia_km,
DROP COLUMN pace;

DROP INDEX IF EXISTS idx_corridas_distancia;
DROP INDEX IF EXISTS idx_corridas_tempo;


CREATE INDEX idx_corridas_distancia_metros
    ON corridas (distancia_metros DESC);

CREATE INDEX idx_corridas_tempo_segundos
    ON corridas (tempo_segundos DESC);

CREATE INDEX idx_corridas_pace_segundos
    ON corridas (pace_segundos ASC);



DROP VIEW IF EXISTS ranking_km;
DROP VIEW IF EXISTS ranking_tempo;
DROP VIEW IF EXISTS corridas_mensais;

SELECT *
FROM pg_depend d
JOIN pg_class c ON d.refobjid = c.oid
WHERE c.relname = 'corridas';

CREATE VIEW ranking_km AS
SELECT
    u.telegram_id,
    u.nome,
    ROUND(SUM(c.distancia_metros) / 1000.0, 2) AS total_km
FROM usuarios u
JOIN corridas c ON c.telegram_id = u.telegram_id
GROUP BY u.telegram_id, u.nome
ORDER BY total_km DESC;

CREATE VIEW ranking_tempo AS
SELECT
    u.telegram_id,
    u.nome,
    SUM(c.tempo_segundos) AS tempo_total_segundos
FROM usuarios u
JOIN corridas c ON c.telegram_id = u.telegram_id
GROUP BY u.telegram_id, u.nome
ORDER BY tempo_total_segundos DESC;

CREATE VIEW corridas_mensais AS
SELECT
    u.telegram_id,
    u.nome,
    DATE_TRUNC('month', c.data_corrida) AS mes,
    COUNT(*) AS total_treinos,
    ROUND(SUM(c.distancia_metros) / 1000.0, 2) AS km_total,
    SUM(c.tempo_segundos) AS tempo_total_segundos,
    ROUND(AVG(c.pace_segundos), 0) AS pace_medio_segundos
FROM usuarios u
JOIN corridas c ON c.telegram_id = u.telegram_id
GROUP BY u.telegram_id, u.nome, mes;
