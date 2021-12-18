SELECT ar_id, name, telephone
FROM bilboard.arendator
WHERE ar_id IN (SELECT arend_id FROM bilboard.order)