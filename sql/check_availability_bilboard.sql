SELECT bil_id, start_ar as date_start, end_ar as date_end
FROM string_order
WHERE bil_id = '$bil_id'
  AND ((start_ar BETWEEN '$date_start' AND '$date_end') or (end_ar BETWEEN '$date_start' AND '$date_end'))