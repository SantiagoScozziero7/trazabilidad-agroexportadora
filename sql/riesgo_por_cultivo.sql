WITH produccion_total AS (
    SELECT provincia,cultivo, SUM(produccion_tm) as total_produccion FROM produccion
    GROUP BY provincia,cultivo
    ORDER BY total_produccion DESC),
deforestacion_total AS (
    SELECT provincia, SUM(superficie_en_hectáreas) as total_deforestacion FROM deforestacion
    GROUP BY provincia
    ORDER BY total_deforestacion DESC)
SELECT p.provincia,p.cultivo, p.total_produccion, d.total_deforestacion,
    CASE
        WHEN d.total_deforestacion >= 20000 THEN 'Alto'
        WHEN d.total_deforestacion > 5000 THEN 'Medio'
        ELSE 'Bajo'
    END AS nivel_riesgo
FROM produccion_total p
JOIN deforestacion_total d ON p.provincia = d.provincia
ORDER BY p.cultivo,d.total_deforestacion DESC