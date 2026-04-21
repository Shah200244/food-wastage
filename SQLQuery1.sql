create database food;
use food;

select * from dbo.food_listings_data
select * from dbo.receivers_data
select * from dbo.providers_data
select * from [dbo].[claims_data]

--total_provider and total_receiver by city
select p.City,
       COUNT(DISTINCT Provider_ID) AS Total_Providers,
       COUNT(DISTINCT Receiver_ID) AS Total_Receivers
FROM dbo.providers_data as p
FULL JOIN dbo.receivers_data as r 
on p.Provider_id = r.Receiver_ID
GROUP BY p.City;

--total_food by provider
SELECT Provider_Type,
       SUM(Quantity) AS Total_Food
FROM dbo.food_listings_data
GROUP BY Provider_Type
ORDER BY Total_Food DESC;

--contact information of food provider
select Name,Contact, City
from dbo.providers_data
where City = 'East Sheena'

--Receiver claim the most food
SELECT r.Name,
       COUNT(c.Claim_ID) AS Total_Claims
FROM claims_data c
JOIN receivers_data r ON c.Receiver_ID = r.Receiver_ID
GROUP BY r.Name
ORDER BY Total_Claims DESC

--Total quantity of food available from the all providers
SELECT Sum(Quantity) AS Total_Food_Available
FROM food_listings_data;

--City have highest number of food listing
SELECT Location,
       COUNT(*) AS Total_Listings
FROM food_listings_data
GROUP BY Location
ORDER BY Total_Listings desc

--most commonly available food 
SELECT Food_Type,
       COUNT(*) AS Count
FROM food_listings_data
GROUP BY Food_Type
ORDER BY Count DESC;

--food claims made for the each food
SELECT f.Food_Name,
       COUNT(c.Claim_ID) AS Total_Claims
FROM claims_data c
JOIN food_listings_data f ON c.Food_ID = f.Food_ID
GROUP BY f.Food_Name;

--which provider had highest number of successful food claim
SELECT p.Name,
       COUNT(c.Claim_ID) AS Successful_Claims
FROM claims_data c
JOIN food_listings_data f ON c.Food_ID = f.Food_ID
JOIN providers_data p ON f.Provider_ID = p.Provider_ID
WHERE c.Status = 'Completed'
GROUP BY p.Name
ORDER BY Successful_Claims desc;

--food claims are completed vs. pending vs. canceled
SELECT Status,
       COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims_data) AS Percentage
FROM claims_data
GROUP BY Status;

--average quantity of food claimed per receiver
SELECT r.Name,
       AVG(f.Quantity) AS Avg_Quantity
FROM claims_data c
JOIN receivers_data r ON c.Receiver_ID = r.Receiver_ID
JOIN food_listings_data f ON c.Food_ID = f.Food_ID
GROUP BY r.Name;

--meal type is claimed the most
SELECT f.Meal_Type,
       COUNT(c.Claim_ID) AS Total_Claims
FROM claims_data c
JOIN food_listings_data f ON c.Food_ID = f.Food_ID
GROUP BY f.Meal_Type
ORDER BY Total_Claims DESC;

--Total quantity of food donated by each provider
SELECT p.Name,
       SUM(f.Quantity) AS Total_Donated
FROM food_listings_data f
JOIN providers_data p ON f.Provider_ID = p.Provider_ID
GROUP BY p.Name;

