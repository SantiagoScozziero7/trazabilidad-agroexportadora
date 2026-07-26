SELECT provincia, SUM(superficie_en_hectáreas) as total_deforestacion FROM deforestacion
GROUP BY provincia
ORDER BY total_deforestacion DESC