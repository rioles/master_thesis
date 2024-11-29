CREATE DATABASE IF NOT EXISTS enterprise_register;
CREATE USER IF NOT EXISTS 'rodolphe' @'localhost' IDENTIFIED BY 'Rodolphe_123_pwd';
GRANT USAGE ON *.* TO 'rodolphe' @'localhost';
GRANT SELECT ON `performance_schema`.* TO 'rodolphe' @'localhost';
GRANT ALL PRIVILEGES ON `enterprise_register`.* TO 'rodolphe' @'localhost';
FLUSH PRIVILEGES;
