-- Step 3: run once after the RDS MySQL instance is available
CREATE DATABASE IF NOT EXISTS iot_db;
USE iot_db;

CREATE TABLE IF NOT EXISTS sensor_readings (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    timestamp   DATETIME      NOT NULL,
    sensor_id   VARCHAR(10)   NOT NULL,
    temperature DECIMAL(5,1)  NOT NULL,
    humidity    INT           NOT NULL,
    UNIQUE KEY uq_reading (sensor_id, timestamp),
    INDEX idx_sensor (sensor_id),
    INDEX idx_time (timestamp)
);
