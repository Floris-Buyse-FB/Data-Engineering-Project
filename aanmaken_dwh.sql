CREATE DATABASE airfaresDWH;

use airfaresDWH;

CREATE TABLE FactFlights (
  carrierCode VARCHAR(50),
  flightKey VARCHAR(255),
  scrapeDate DATE,
  airportCode VARCHAR(50),
  flightNumber VARCHAR(50),
  departureDate DATE,
  arrivalDate DATE,
  totalNumberOfStops INT,
  PRIMARY KEY (flightKey, scrapeDate)
);

CREATE TABLE DimFlight (
  flightKey VARCHAR(255) NOT NULL,
  flightNumber VARCHAR(50),
  departureDate DATE,
  arrivalDate DATE,
  departureTime TIME,
  arrivalTime TIME,
  journeyDuration TIME,
  totalNumberOfStops INT,
  carrierCode VARCHAR(50),
  depAirportCode VARCHAR(50),
  arrAirportCode VARCHAR(50),
  startDate DATE,
  endDate DATE,
  PRIMARY KEY (flightKey),
  UNIQUE KEY (flightKey)
);

CREATE TABLE DimPrice (
  priceID INT AUTO_INCREMENT PRIMARY KEY,
  flightKey VARCHAR(255),
  scrapeDate DATE,
  availableSeats INT,
  adultPrice FLOAT,
  FOREIGN KEY (flightKey) REFERENCES DimFlight(flightKey)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE DimAirline (
carrierCode VARCHAR(10),
carrierName VARCHAR(50)
);

CREATE TABLE DimAirport (
airportCode VARCHAR(10) PRIMARY KEY,
airportName VARCHAR(50),
city VARCHAR(50),
country VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS DimDate  (
    date_id INT NOT NULL auto_increment,
    fullDate DATE,
    dayOfMonth INT,
    dayOfYear INT,
    dayOfWeek INT,
    dayName VARCHAR(10),
    monthNumber INT,
    monthName VARCHAR(10),
    year INT,
    isItWeekend INT,
    isItVacationday INT,
    PRIMARY KEY(date_id)
) ENGINE=InnoDB AUTO_INCREMENT=1000;