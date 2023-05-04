CREATE DATABASE airfaresDWH;

use airfaresDWH;


CREATE TABLE DimFlight (
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
    dateID INT UNSIGNED,
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
  flightKey VARCHAR(255),
  flightNumber VARCHAR(50),
  carrierCode VARCHAR(50),
  scrapeDate DATE,
  depAirportCode VARCHAR(50),
  arrAirportCode VARCHAR(50),
  flightID INT,
  departureDate DATE,
  arrivalDate DATE,
  totalNumberOfStops INT,
  availableSeats INT,
  adultPrice FLOAT,
  carrierID INT,
  airportID INT,
  dateID INT UNSIGNED,
  PRIMARY KEY (flightKey),
  FOREIGN KEY (flightID) REFERENCES DimFlight(flightID),
  FOREIGN KEY (carrierID) REFERENCES DimAirline(carrierID),
  FOREIGN KEY (airportID) REFERENCES DimAirport(airportID),
  FOREIGN KEY (dateID) REFERENCES DimDate(dateID)
  
);
