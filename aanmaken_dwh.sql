CREATE DATABASE airfaresDWH;

use airfaresDWH;


CREATE TABLE DimFlight (
flightKey VARCHAR(255),
	flightID INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
  flightNumber VARCHAR(50),
  departureDate DATE,
  arrivalDate DATE,
  departureTime TIME,
  arrivalTime TIME,
  journeyDuration TIME,
  totalNumberOfStops INT,
  startDate DATE,
  endDate DATE
);


CREATE TABLE DimAirline (
carrierID INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
carrierCode VARCHAR(10),
carrierName VARCHAR(50)
);

CREATE TABLE DimAirport (
airportID INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
airportCode VARCHAR(10),
airportName VARCHAR(50),
city VARCHAR(50),
country VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS DimDate (
    dateID INT,
    fullDate DATE,
    dayOfMonth INT,
    dayOfYear INT,
    dayOfWeek INT,
    dayName VARCHAR(10),
    monthNumber INT,
    monthName VARCHAR(10),
    year INT,
    isItWeekend INT,
    isItVacationDay INT,
    PRIMARY KEY (dateID)
) ENGINE=InnoDB AUTO_INCREMENT=1000;





CREATE TABLE FactFlights (
	factID INT auto_increment,
  scrapeDateID INT,
   depAirportID INT,
  arrAirportID INT,
  flightID INT,
    carrierID INT,
  departureDateID INT,
  arrivalDateID int,
  availableSeats INT,
  adultPrice FLOAT,
  PRIMARY KEY (factID),
  FOREIGN KEY (flightID) REFERENCES DimFlight(flightID),
  FOREIGN KEY (carrierID) REFERENCES DimAirline(carrierID),
  FOREIGN KEY (depAirportID) REFERENCES DimAirport(airportID),
    FOREIGN KEY (arrAirportID) REFERENCES DimAirport(airportID),
  FOREIGN KEY (departureDateID) REFERENCES DimDate(dateID),
    FOREIGN KEY (arrivalDateID) REFERENCES DimDate(dateID),
      FOREIGN KEY (scrapeDateID) REFERENCES DimDate(dateID)
);