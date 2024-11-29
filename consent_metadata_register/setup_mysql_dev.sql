CREATE DATABASE IF NOT EXISTS consent_registration;
CREATE USER IF NOT EXISTS 'rodolphe' @'localhost' IDENTIFIED BY 'Rodolphe_123_pwd';
GRANT USAGE ON *.* TO 'rodolphe' @'localhost';
GRANT SELECT ON `performance_schema`.* TO 'rodolphe' @'localhost';
GRANT ALL PRIVILEGES ON `consent_registration`.* TO 'rodolphe' @'localhost';
FLUSH PRIVILEGES;
