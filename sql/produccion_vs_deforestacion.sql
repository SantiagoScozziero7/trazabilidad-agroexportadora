WITH produccion_total AS (
    SELECT provincia, SUM(produccion_tm) as total_produccion FROM produccion
    GROUP BY provincia
    ORDER BY total_produccion DESC),
deforestacion_total AS (
    SELECT provincia, SUM(superficie_en_hectáreas) as total_deforestacion FROM deforestacion
    GROUP BY provincia
    ORDER BY total_deforestacion DESC)
SELECT p.provincia, p.total_produccion, d.total_deforestacion
FROM produccion_total p
JOIN deforestacion_total d ON p.provincia = d.provincia