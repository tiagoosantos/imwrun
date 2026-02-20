SELECT *
FROM corridas_mensais
WHERE TO_CHAR(mes, 'YYYY-MM') = TO_CHAR(current_date, 'YYYY-MM');


SELECT
    u.nome,
    ROUND(SUM(c.distancia_metros)/1000.0,2) AS total_km
FROM corridas c
JOIN usuarios u ON u.telegram_id = c.telegram_id
WHERE date_trunc('month', c.data_corrida) = date_trunc('month', CURRENT_DATE)
GROUP BY u.nome
ORDER BY total_km DESC;