
		-- DEEL 1 --
        -- De tabel flight wordt gevuld. Dit moet gebeuren vóór het vullen van de tabel price omwille van foreign keys
        -- De tabel flight bevat o.a. flightKey, flightNumber, departureDate, arrivalDate, departureTime, arrivalTime, ...
        -- De bestanden móeten in de map C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\ staan
        -- Het pad C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\ is te vinden via het commando SHOW VARIABLES LIKE "secure_file_priv";
        -- Anders krijg je Error Code: 1290. The MySQL server is running with the --secure-file-priv option so it cannot execute this statement

		-- Hierna bevat de temporary table de structuur van de tabel flight, maar de tabel is leeg (WHERE flightKey = 'A')
		CREATE TEMPORARY TABLE temp_tbl 
		SELECT *
		FROM flight
		WHERE flightKey = 'A';        
	
		LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\Ryanair.csv'
		INTO TABLE temp_tbl
		FIELDS TERMINATED BY ','
		LINES TERMINATED BY '\n'
		(@flightKey, @flightNumber, @departureDate, @arrivalDate, @departureTime, @arrivalTime, @journeyDuration, @totalNumberOfStops, @carrierCode, @depAirportCode, @arrAirportCode, @scrapeDate, @availableSeats, @adultPrice)
		SET flightKey=@flightKey, flightNumber=@flightNumber, departureDate=@departureDate, arrivalDate=@arrivalDate, departureTime=@departureTime, arrivalTime=@arrivalTime, journeyDuration=@journeyDuration, totalNumberOfStops=@totalNumberOfStops,
		carrierCode=@carrierCode, depAirportCode=@depAirportCode, arrAirportCode=@arrAirportCode;
        
		LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\Tui.csv'
		INTO TABLE temp_tbl
		FIELDS TERMINATED BY ','
		LINES TERMINATED BY '\n'
		(@flightKey, @flightNumber, @departureDate, @arrivalDate, @departureTime, @arrivalTime, @journeyDuration, @totalNumberOfStops, @carrierCode, @depAirportCode, @arrAirportCode, @scrapeDate, @availableSeats, @adultPrice)
		SET flightKey=@flightKey, flightNumber=@flightNumber, departureDate=@departureDate, arrivalDate=@arrivalDate, departureTime=@departureTime, arrivalTime=@arrivalTime, journeyDuration=@journeyDuration, totalNumberOfStops=@totalNumberOfStops,
		carrierCode=@carrierCode, depAirportCode=@depAirportCode, arrAirportCode=@arrAirportCode;   
        
		LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\Transavia.csv'
		INTO TABLE temp_tbl
		FIELDS TERMINATED BY ','
		LINES TERMINATED BY '\n'
		(@flightKey, @flightNumber, @departureDate, @arrivalDate, @departureTime, @arrivalTime, @journeyDuration, @totalNumberOfStops, @carrierCode, @depAirportCode, @arrAirportCode, @scrapeDate, @availableSeats, @adultPrice)
		SET flightKey=@flightKey, flightNumber=@flightNumber, departureDate=@departureDate, arrivalDate=@arrivalDate, departureTime=@departureTime, arrivalTime=@arrivalTime, journeyDuration=@journeyDuration, totalNumberOfStops=@totalNumberOfStops,
		carrierCode=@carrierCode, depAirportCode=@depAirportCode, arrAirportCode=@arrAirportCode;
        
        -- Merge de nieuwe data met de al bestaande data
        -- In SQL Server bestaat het commando Merge (Zie Chamilo > Relational Databases > Docmenten > Slides > 2. SQL Advanced > Slide 38 Merge
        -- In MySQL bestaat dat niet. In plaats daarvan kunnen we gebruik maken van het volgende
        -- https://dev.mysql.com/doc/refman/5.7/en/insert-on-duplicate.html
        
    INSERT INTO flight
		SELECT * FROM temp_tbl
		ON DUPLICATE KEY UPDATE flight.departureTime = temp_tbl.departureTime, flight.arrivalTime = temp_tbl.arrivalTime, flight.journeyDuration = temp_tbl.journeyDuration, flight.totalNumberOfStops = temp_tbl.totalNumberOfStops;
        
        
		DROP TABLE temp_tbl;

		-- DEEL 2 --        
        -- De tabel price wordt gevuld met Ryanair.csv, Transavia.csv en Tui.csv
        -- De tabel price bevat o.a. priceID (AUTO INCREMENT), flightKey, scrapeDate, availableSeats, adultPrice
		-- Ook hier moet er gebruik gemaakt worden van een temporary table. Er is bewust geen primary key voorzien.
        -- Anders wordt de Load into price niet uitgevoerd vanuit het Python script omdat er met auto-increment gewerkt wordt en er geen primary keys zijn
		
		CREATE TEMPORARY TABLE temp_tbl_2 (
			`flightKey` char(255) DEFAULT NULL,
			`scrapeDate` date DEFAULT NULL,
			`availableSeats` int DEFAULT NULL,
			`adultPrice` double DEFAULT NULL
		);

		LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\Ryanair.csv'
		INTO TABLE temp_tbl_2
		FIELDS TERMINATED BY ','
		LINES TERMINATED BY '\n'
		(@flightKey, @flightNumber, @departureDate, @arrivalDate, @departureTime, @arrivalTime, @journeyDuration, @totalNumberOfStops, @carrierCode, @depAirportCode, @arrAirportCode, @scrapeDate, @availableSeats, @adultPrice)
		SET flightKey=@flightKey, scrapeDate=@scrapeDate, availableSeats=@availableSeats, adultPrice=@adultPrice;
        
		LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\Tui.csv'
		INTO TABLE temp_tbl_2
		FIELDS TERMINATED BY ','
		LINES TERMINATED BY '\n'
		(@flightKey, @flightNumber, @departureDate, @arrivalDate, @departureTime, @arrivalTime, @journeyDuration, @totalNumberOfStops, @carrierCode, @depAirportCode, @arrAirportCode, @scrapeDate, @availableSeats, @adultPrice)
		SET flightKey=@flightKey, scrapeDate=@scrapeDate, availableSeats=@availableSeats, adultPrice=@adultPrice;
        
        
		LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\Transavia.csv'
		INTO TABLE temp_tbl_2
		FIELDS TERMINATED BY ','
		LINES TERMINATED BY '\n'
		(@flightKey, @flightNumber, @departureDate, @arrivalDate, @departureTime, @arrivalTime, @journeyDuration, @totalNumberOfStops, @carrierCode, @depAirportCode, @arrAirportCode, @scrapeDate, @availableSeats, @adultPrice)
		SET flightKey=@flightKey, scrapeDate=@scrapeDate, availableSeats=@availableSeats, adultPrice=@adultPrice;

		-- Door de INSERT te doen met behulp van de temporary table, worden de AUTO INCREMENT primary keys gemaakt
  	INSERT INTO price(flightKey, scrapeDate, availableSeats, adultPrice)
		SELECT flightKey, scrapeDate, availableSeats, CAST(adultPrice AS DOUBLE(10,2)) FROM temp_tbl_2;

		DROP TABLE temp_tbl_2;
