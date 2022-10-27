SELECT start_ar, end_ar, bil_id, ord_id
FROM bilboard.string_order
WHERE start_ar = '$date_start'
  AND end_ar = '$date_end'
  AND bil_id = '$num_bil'
  AND ord_id = '$num_ord'