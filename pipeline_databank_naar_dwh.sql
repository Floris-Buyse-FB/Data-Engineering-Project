USE airfaresdwh;

SET SQL_SAFE_UPDATES = 0;

-- temporarily disable sp_DimDateconstraints
SET FOREIGN_KEY_CHECKS=0;

SET GLOBAL wait_timeout = 600;


-- Empty + recreate DimDate 
delimiter //


CREATE PROCEDURE  DimDateBuild (p_start_date DATE, p_end_date DATE)
BEGIN
    DECLARE v_full_date DATE;

    DELETE FROM DimDate;

    SET v_full_date = p_start_date;
    WHILE v_full_date < p_end_date DO

        INSERT INTO DimDate (
			dateID,
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
			UNIX_TIMESTAMP(v_full_date),
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

CALL DimDateBuild('2023-04-01', '2024-01-01');



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




-- DIMFLIGHT + SCD!!!
-- Insert new flights into the DimFlight table
INSERT INTO DimFlight (flightKey, flightNumber, departureDate, arrivalDate, departureTime, arrivalTime, journeyDuration, totalNumberOfStops, startDate, endDate)
SELECT f.flightKey, f.flightNumber, f.departureDate, f.arrivalDate, f.departureTime, f.arrivalTime, f.journeyDuration, f.totalNumberOfStops, '2023-01-01', NULL
FROM airfares.Flight f
WHERE NOT EXISTS (
  SELECT 1 FROM DimFlight df WHERE f.flightKey = df.flightKey
);


DROP TABLE IF EXISTS TempFlightChanges;

-- Use a temporary table to hold the flights that have changed
CREATE TEMPORARY TABLE TempFlightChanges AS
SELECT f.flightKey, df.flightID, f.flightNumber, f.departureDate, f.arrivalDate, f.departureTime, f.arrivalTime, f.journeyDuration, f.totalNumberOfStops
FROM airfares.Flight f
LEFT JOIN airfaresdwh.DimFlight df ON f.flightKey = df.flightKey
WHERE df.totalNumberOfStops <> f.totalNumberOfStops OR df.departureTime <> f.departureTime OR df.arrivalTime <> f.arrivalTime OR df.journeyDuration <> f.journeyDuration;


-- Set the end date in DimFlight for the flights that have changed, on yesterday
UPDATE DimFlight df
LEFT JOIN TempFlightChanges tfc ON df.flightKey = tfc.flightKey
SET df.endDate = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
WHERE df.endDate IS NULL;

-- Add extra records to DimFlight with most recent info of the flights
INSERT INTO DimFlight (flightKey, flightNumber, departureDate, arrivalDate, departureTime, arrivalTime, journeyDuration, totalNumberOfStops, startDate, endDate)
SELECT f.flightKey, f.flightNumber, f.departureDate, f.arrivalDate, f.departureTime, f.arrivalTime, f.journeyDuration, f.totalNumberOfStops, NOW(), NULL
FROM TempFlightChanges tf
WHERE NOT EXISTS (
  SELECT 1 FROM DimFlight df WHERE f.flightKey = tf.flightKey
)



USE airfaresdwh;
-- ints toevoegen in datawarehouse => auto-increment (allemaal), behalve voor dimdate van date cijfer maken (code zoeken)!!!!!!!!!!!!
INSERT INTO FactFlights(
scrapeDateID,
depAirportID,
arrAirportID,
flightID,
carrierID,
departureDateID,
arrivalDateID,
availableSeats,
adultPrice
)
SELECT DISTINCT
dwh_date.dateID,
dwh_airport.airportID,
dwh_airport.airportID,
dwh_flight.flightID, 
dwh_airline.carrierID,
dwh_date.dateID,
dwh_date.dateID,
oltp_price.availableSeats,
oltp_price.adultPrice

FROM airfares.flight oltp_flight INNER JOIN airfaresdwh.dimflight dwh_flight ON oltp_flight.flightKey = dwh_flight.flightKey
inner join airfaresdwh.dimairline dwh_airline ON oltp_flight.carrierCode = dwh_airline.carrierCode 
INNER JOIN airfaresdwh.dimAirport dwh_airport ON oltp_flight.depAirportCode = dwh_airport.airportCode
INNER JOIN airfaresdwh.dimAirport dwh_airport2 ON oltp_flight.arrAirportCode = dwh_airport2.airportCode
INNER JOIN airfares.price oltp_price ON oltp_flight.flightKey = oltp_price.flightKey_id 
INNER JOIN airfaresdwh.dimDate dwh_date ON oltp_price.scrapeDate = dwh_date.fullDate
INNER JOIN airfaresdwh.dimDate dwh_date2 ON oltp_flight.departureDate = dwh_date2.fullDate
INNER JOIN airfaresdwh.dimDate dwh_date3 ON oltp_flight.arrivalDate = dwh_date3.fullDate

WHERE 


/* only add new lines + make sure it runs from an empty FactFlights table */
oltp_price.priceID > (SELECT IFNULL (MAX(factID),0) from FactFlights)
AND
/* Slowly Changing Dimension DimFlight */
oltp_price.scrapeDate >= dwh_flight.startDate and (dwh_flight.endDate is null or oltp_price.scrapeDate <= dwh_flight.endDate) 





-- drop procedure
DROP PROCEDURE IF EXISTS DimDateBuild;
