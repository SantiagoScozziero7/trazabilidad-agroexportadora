SELECT provincia, SUM(produccion_tm) as total_produccion FROM produccion
GROUP BY provincia
ORDER BY total_produccion DESC