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
