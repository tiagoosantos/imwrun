-- =========================
-- TABELA DE USUÁRIOS
-- =========================
-- CREATE TABLE usuarios (
--     id SERIAL PRIMARY KEY,
--     telegram_id BIGINT UNIQUE NOT NULL,
--     username VARCHAR(100),
--     telegram_first_name VARCHAR(100),
--     nome VARCHAR(150),
--     nome_confirmado BOOLEAN DEFAULT FALSE,
--     ativo BOOLEAN DEFAULT TRUE,
--     data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    language_code VARCHAR(10),
    is_premium BOOLEAN,
    is_bot BOOLEAN,
    nome VARCHAR(150),
    nome_confirmado BOOLEAN DEFAULT FALSE,
    ultimo_acesso TIMESTAMP,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- drop table usuarios CASCADE;

-- =========================
-- TABELA DE CORRIDAS
-- =========================
CREATE TABLE IF NOT EXISTS corridas (
    id SERIAL PRIMARY KEY,

    telegram_id BIGINT NOT NULL,

    passos INTEGER CHECK (passos >= 0),
    calorias INTEGER CHECK (calorias >= 0),

    data_corrida TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    tempo_segundos INTEGER NOT NULL,
    distancia_metros INTEGER NOT NULL,
    pace_segundos INTEGER NOT NULL,
    pace_origem VARCHAR(20)

    tipo_treino VARCHAR(20) NOT NULL DEFAULT 'corrida',
    local_treino VARCHAR(30) NOT NULL DEFAULT 'rua'

    CONSTRAINT fk_corridas_usuario
        FOREIGN KEY (telegram_id)
        REFERENCES usuarios (telegram_id)
        ON DELETE CASCADE
);

-- ALTER TABLE corridas
-- ADD COLUMN tipo_treino VARCHAR(20) NOT NULL DEFAULT 'corrida',
-- ADD COLUMN local_treino VARCHAR(30) NOT NULL DEFAULT 'rua';


-- =========================
-- ÍNDICES
-- =========================
CREATE INDEX IF NOT EXISTS idx_corridas_usuario
    ON corridas (telegram_id);

CREATE INDEX IF NOT EXISTS idx_corridas_data
    ON corridas (data_corrida);

ALTER TABLE corridas
ADD CONSTRAINT chk_tempo_segundos CHECK (tempo_segundos > 0),
ADD CONSTRAINT chk_distancia_metros CHECK (distancia_metros > 0),
ADD CONSTRAINT chk_pace_segundos CHECK (pace_segundos > 0);

CREATE INDEX idx_corridas_distancia_metros
    ON corridas (distancia_metros DESC);

CREATE INDEX IF NOT EXISTS idx_corridas_tempo_segundos
    ON corridas (tempo_segundos DESC);

CREATE INDEX IF NOT EXISTS idx_corridas_pace_segundos
    ON corridas (pace_segundos ASC);


-- =========================
-- VIEWS
-- =========================
CREATE VIEW ranking_km AS
SELECT
    u.telegram_id,
    u.nome,
    ROUND(SUM(c.distancia_metros) / 1000.0, 2) AS total_km
FROM usuarios u
JOIN corridas c ON c.telegram_id = u.telegram_id
GROUP BY u.telegram_id, u.nome
ORDER BY total_km DESC;

----------------------------
CREATE VIEW ranking_tempo AS
SELECT
    u.telegram_id,
    u.nome,
    SUM(c.tempo_segundos) AS tempo_total_segundos
FROM usuarios u
JOIN corridas c ON c.telegram_id = u.telegram_id
GROUP BY u.telegram_id, u.nome
ORDER BY tempo_total_segundos DESC;

----------------------------
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

CREATE INDEX idx_corridas_telegram_id ON corridas(telegram_id);
CREATE INDEX idx_corridas_data ON corridas(data_corrida);
