-- SQLite
drop table CombinedTable
drop table UserSubmissionRecord
drop table ArrangingTheDataInProperOrder
drop table UserSubmissionRecord
drop table UserSubmittedFeedback  

SELECT DISTINCT BusinessFunction
FROM ArrangingTheDataInProperOrder 
WHERE BusinessSector = "MINING" AND BusinessFunction = "Supply Chain and Logistics" 
ORDER BY MeasuringElt 


SELECT DISTINCT MeasuringElt 
FROM ArrangingTheDataInProperOrder 
WHERE BusinessSector = "MINING" AND BusinessFunction="Mining Operations"
ORDER BY MeasuringElt 

 


SELECT SUbCategory
FROM ArrangingTheDataInProperOrder 
WHERE BusinessSector = "MINING" AND BusinessFunction = "Data Utilization and Analytics" AND MeasuringElt = "Exploration and Geology"  
ORDER BY MeasuringElt  


SELECT * FROM ArrangingTheDataInProperOrder
