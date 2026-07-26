SELECT provincia,anio, SUM(produccion_tm) as total_produccion FROM produccion
    WHERE provincia in ('Santiago del Estero','Chaco','Formosa')
    GROUP BY provincia, anio
    ORDER BY anio