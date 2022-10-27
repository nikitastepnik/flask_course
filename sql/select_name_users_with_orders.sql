SELECT ar_id, name, telephone
FROM bilboard.arendator
WHERE ar_id IN (SELECT arend_id
                FROM bilboard.order
                         JOIN string_order ON ord_id = or_id)