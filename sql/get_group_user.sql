SELECT access.login, access.group
FROM bilboard.access
WHERE login = '$login' and password = '$password'