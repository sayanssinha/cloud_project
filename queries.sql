-- Step 5: descriptive analytics (MySQL)
-- 1. Total readings
SELECT COUNT(*) AS total_readings FROM sensor_readings;

-- 2. Overall average temperature and humidity
SELECT ROUND(AVG(temperature),2) AS avg_temp, ROUND(AVG(humidity),2) AS avg_humidity
FROM sensor_readings;

-- 3. Min and max
SELECT MIN(temperature) AS min_temp, MAX(temperature) AS max_temp,
       MIN(humidity)    AS min_hum,  MAX(humidity)    AS max_hum
FROM sensor_readings;

-- 4. Sensor-wise summary
SELECT sensor_id, COUNT(*) AS readings,
       ROUND(AVG(temperature),2) AS avg_temp,
       MIN(temperature) AS min_temp, MAX(temperature) AS max_temp,
       ROUND(AVG(humidity),2) AS avg_humidity
FROM sensor_readings
GROUP BY sensor_id ORDER BY sensor_id;

-- 5. Hourly trend over time
SELECT DATE_FORMAT(timestamp, '%Y-%m-%d %H:00') AS hour_slot,
       ROUND(AVG(temperature),2) AS avg_temp, ROUND(AVG(humidity),2) AS avg_humidity
FROM sensor_readings
GROUP BY hour_slot ORDER BY hour_slot;

-- 6. Hottest 5 readings
SELECT * FROM sensor_readings ORDER BY temperature DESC LIMIT 5;

-- 7. Latest 5 readings
SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 5;
