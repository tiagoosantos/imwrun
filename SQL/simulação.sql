-- ==========================================
-- USUÁRIOS (caso não existam)
-- ==========================================

INSERT INTO usuarios (telegram_id, nome)
VALUES
(1001, 'Tiago'),
(1002, 'Mayara'),
(1003, 'Carlos')
ON CONFLICT (telegram_id) DO NOTHING;


-- ==========================================
-- VARIÁVEIS DE DATA
-- ==========================================

-- Mês atual
-- date_trunc('month', current_date)

-- Mês anterior
-- date_trunc('month', current_date - interval '1 month')


-- ==========================================
-- TREINOS MÊS ATUAL
-- ==========================================

INSERT INTO corridas
(telegram_id, data_corrida, distancia_metros, tempo_segundos, pace_segundos, pace_origem, calorias)
VALUES
-- TIAGO (volume alto)
(1001, date_trunc('month', current_date) + interval '2 day', 10000, 3000, 300, 'calculado', 750),
(1001, date_trunc('month', current_date) + interval '5 day', 12000, 3600, 300, 'calculado', 900),
(1001, date_trunc('month', current_date) + interval '8 day', 8000, 2400, 300, 'calculado', 600),
(1001, date_trunc('month', current_date) + interval '12 day', 15000, 4500, 300, 'calculado', 1100),
-- MAYARA (volume médio)
(1002, date_trunc('month', current_date) + interval '3 day', 5000, 1500, 300, 'calculado', 350),
(1002, date_trunc('month', current_date) + interval '9 day', 7000, 2100, 300, 'calculado', 500),
(1002, date_trunc('month', current_date) + interval '14 day', 6000, 1800, 300, 'calculado', 420),
-- CARLOS (volume menor)
(1003, date_trunc('month', current_date) + interval '4 day', 4000, 1400, 350, 'calculado', 280),
(1003, date_trunc('month', current_date) + interval '11 day', 5000, 1750, 350, 'calculado', 350);



-- ==========================================
-- TREINOS MÊS ANTERIOR
-- ==========================================

INSERT INTO corridas
(telegram_id, data_corrida, distancia_metros, tempo_segundos, pace_segundos, pace_origem, calorias)
VALUES
-- TIAGO
(1001, date_trunc('month', current_date - interval '1 month') + interval '5 day', 8000, 2500, 312, 'calculado', 600),
(1001, date_trunc('month', current_date - interval '1 month') + interval '15 day', 10000, 3200, 320, 'calculado', 750),
-- MAYARA
(1002, date_trunc('month', current_date - interval '1 month') + interval '6 day', 6000, 1800, 300, 'calculado', 400),
(1002, date_trunc('month', current_date - interval '1 month') + interval '18 day', 9000, 2700, 300, 'calculado', 650),
-- CARLOS
(1003, date_trunc('month', current_date - interval '1 month') + interval '10 day', 3000, 1100, 366, 'calculado', 220);

-- DELETE FROM corridas WHERE telegram_id IN (1001,1002,1003);
-- DELETE FROM usuarios WHERE telegram_id IN (1001,1002,1003);
