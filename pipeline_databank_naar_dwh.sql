USE airfaresdwh;

SET SQL_SAFE_UPDATES = 0;

-- temporarily disable sp_DimDateconstraints
SET FOREIGN_KEY_CHECKS=0;


-- Empty + recreate DimDate 
delimiter //


CREATE PROCEDURE  DimDateBuild (p_start_date DATE, p_end_date DATE)
BEGIN
    DECLARE v_full_date DATE;

    DELETE FROM DimDate;

    SET v_full_date = p_start_date;
    WHILE v_full_date < p_end_date DO

        INSERT INTO DimDate (
            fullDate ,
            dayOfMonth ,
            dayOfYear ,
            dayOfWeek ,
            dayName ,
            monthNumber,
            monthName,
            year,
            isItWeekend,
            isItVacationday
        ) VALUES (
            v_full_date,
            DAYOFMONTH(v_full_date),
            DAYOFYEAR(v_full_date),
            DAYOFWEEK(v_full_date),
            DAYNAME(v_full_date),
            MONTH(v_full_date),
            MONTHNAME(v_full_date),
            YEAR(v_full_date),
            IF(DAYOFWEEK(v_full_date) IN (1,7), 1, 0), -- 1 for weekends, 0 for weekdays
			IF(
				(MONTH(v_full_date) = 4 AND DAY(v_full_date) >= 8 AND DAY(v_full_date) <= 17) OR -- Easter break
				(MONTH(v_full_date) = 12 AND DAY(v_full_date) >= 24) OR -- Christmas break
				(MONTH(v_full_date) IN (7,8)), -- July and August
				1, -- is a vacation day
				0 -- not a vacation day
        ));

        SET v_full_date = DATE_ADD(v_full_date, INTERVAL 1 DAY);
    END WHILE;
END;

CALL DimDateBuild('2023-04-01', '2023-10-01');

-- create a temporary table to hold the transformed data
CREATE TEMPORARY TABLE IF NOT EXISTS temp_flight_data AS 
SELECT 
    f.carrierCode,
    f.flightKey,
    p.scrapeDate,
    f.depAirportCode AS airportCode,
    f.flightNumber,
    f.departureDate,
    f.arrivalDate,
    f.totalNumberOfStops
FROM 
    airfares.Flight AS f
    JOIN airfares.Price AS p ON f.flightKey = p.flightKey_id;


-- update DimAirline + insert nieuwe records

UPDATE DimAirline da 
SET carrierName = (SELECT carrierName FROM airfares.Airline WHERE airfares.Airline.carrierCode = da.carrierCode);

INSERT INTO DimAirline(carrierCode, carrierName)
SELECT DISTINCT carrierCode, carrierName FROM airfares.Airline WHERE carrierCode NOT IN (SELECT DISTINCT carrierCode FROM DimAirline);



-- update DimAirport + insert nieuwe recordes
UPDATE DimAirport dap
SET airportName = (SELECT airportName from airfares.Airport WHERE airfares.Airport.airportCode = dap.airportCode); -- zou hier eventueel dus ook kunnen checken op country en city maar is beetje absurd natuurlijk

INSERT INTO DimAirport(airportCode, airportName, city, country)
SELECT DISTINCT airportCode, airportName, city, country FROM airfares.Airport WHERE airportCode NOT IN (SELECT DISTINCT airportCode FROM DimAirport);



-- DimPrice insert nieuwe records vanuit OLTP
INSERT INTO DimPrice (
    flightKey,
    scrapeDate,
    availableSeats,
    adultPrice
)
SELECT 
    p.flightKey_id,
    p.scrapeDate,
    p.availableSeats,
    p.adultPrice
FROM 
    airfares.Price AS p;


-- DIMFLIGHT + SCD!!!
-- Insert new flights into the DimFlight table
INSERT INTO DimFlight (flightKey, flightNumber, departureDate, arrivalDate, departureTime, arrivalTime, journeyDuration, totalNumberOfStops, carrierCode, depAirportCode, arrAirportCode, startDate, endDate)
SELECT f.flightKey, f.flightNumber, f.departureDate, f.arrivalDate, f.departureTime, f.arrivalTime, f.journeyDuration, f.totalNumberOfStops, f.carrierCode, f.depAirportCode, f.arrAirportCode, NOW(), NULL
FROM airfares.Flight f
LEFT JOIN DimFlight df ON f.flightNumber = df.flightNumber AND f.departureDate = df.departureDate
WHERE df.flightKey IS NULL;

-- Use a temporary table to hold the flights that have changed
CREATE TEMPORARY TABLE IF NOT EXISTS TempFlightChanges (
    flightKey INT NOT NULL,
    totalNumberOfStops INT,
    journeyDuration INT,
    arrivalTime TIME,
    departureTime TIME
);

INSERT INTO TempFlightChanges (flightKey, totalNumberOfStops, journeyDuration, arrivalTime, departureTime)
SELECT df.flightKey, f.totalNumberOfStops, f.journeyDuration, f.arrivalTime, f.departureTime
FROM airfares.Flight f
INNER JOIN DimFlight df ON f.flightKey = df.flightKey
WHERE f.totalNumberOfStops <> df.totalNumberOfStops OR f.journeyDuration <> df.journeyDuration OR f.arrivalTime <> df.arrivalTime OR f.departureTime <> df.departureTime;

-- Set the end date in DimFlight for the flights that have changed, on yesterday
UPDATE DimFlight df
INNER JOIN TempFlightChanges tfc ON df.flightKey = tfc.flightKey
SET df.endDate = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
WHERE df.endDate IS NULL;

-- Add extra records to DimFlight with most recent info of the flights
INSERT IGNORE INTO DimFlight (flightKey, flightNumber, departureDate, arrivalDate, departureTime, arrivalTime, journeyDuration, totalNumberOfStops, carrierCode, depAirportCode, arrAirportCode, startDate, endDate)
SELECT f.flightKey, f.flightNumber, f.departureDate, f.arrivalDate, f.departureTime, f.arrivalTime, f.journeyDuration, f.totalNumberOfStops, f.carrierCode, f.depAirportCode, f.arrAirportCode, NOW(), NULL
FROM airfares.Flight f
LEFT JOIN DimFlight df ON f.flightKey = df.flightKey
WHERE df.flightKey IS NULL;


    


-- Fact table opvullen adhv (eerste) temporary table
INSERT IGNORE INTO FactFlights (
    carrierCode, 
    flightKey, 
    scrapeDate, 
    airportCode, 
    flightNumber, 
    departureDate, 
    arrivalDate, 
    totalNumberOfStops
)
SELECT 
    carrierCode,
    flightKey,
    scrapeDate,
    airportCode,
    flightNumber,
    departureDate,
    arrivalDate,
    totalNumberOfStops
FROM 
    temp_flight_data;



-- drop the temporary table
DROP TEMPORARY TABLE IF EXISTS temp_flight_data;

-- drop procedure
DROP PROCEDURE IF EXISTS DimDateBuild;
