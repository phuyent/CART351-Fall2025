import requests #1. import library

token = "d398089c6ba7f09de5586cfee0a1d258e8ec741a" #2. personal key 

url = "https://api.waqi.info/search/" #3. website url varible

response = requests.get(url, params={"token": token, "keyword": "montreal"}) #4. access the data through the query that has the key and city

results = response.json() #5. results varible containing the parsed JSON response  


print(results) #6. confirm and verify data


print(type(results)) #7. 'results' varible is a dictionary <class 'dict'>


print(results.keys()) #8. result: dict_keys(['status', 'data'])

print(results["data"]) #9. access the content associated with the data field
responseData = results["data"] #10. save the content in responseData variable 
print(type(responseData)) # 11. responseData type is list <class 'list'>

for item in responseData:
    print(item) #12. what does each item represent? Each item is a separate dictionary for each station
    
print(type(item)) #13.write the code to determine the type of the item variable -> each item is a dictionary <class 'dict'>
print(item.keys())#14.write the code to determine the keys associated with the item variable -> dict_keys(['uid', 'aqi', 'time', 'station'])

# 15. print out the name of each station from the responseData. Document the results.
for item in responseData:
    print(item["station"]["name"]) 
# Results from 15
# Montreal
# Échangeur Décarie, Montreal, Canada
# Caserne 17, Montreal, Canada
# Roberval, York, Montreal, Canada
# Jardin Botanique, Montreal, Canada
# Ontario, Montreal, Canada
# Molson, Montreal, Canada
# Saint-Michel, Montreal, Canada
# Hochelaga-Maisonneuve, Montreal, Canada
# St-Dominique, Montreal, Canada
# Parc Pilon, Montreal, Canada
# Maisonneuve, Montreal, Canada
# Drummond, Montreal, Canada
# Verdun, Montreal, Canada
# Duncan, Montreal, Canada
# Anjou, Montreal, Canada
# Dorval, Montreal, Canada
# Chénier, Montreal, Canada
# Saint-Jean-Baptiste, Montreal, Canada
# Aéroport de Montréal, Montreal, Canada
# Sainte-Anne-de-Bellevue, Montreal, Canada


# 16. append the code above to also print out the geolocations of each station from the responseData.
for item in responseData:
    lat = item["station"]["geo"][0] #access the first item in geo list which is the latitude
    lng = item["station"]["geo"][1] #access the second item in geo list which is the latitude
    print("lat:",lat) #print latitude first
    print("lng:",lng) #then print longittude right after
# Results from 16
# lat: 45.5086699
# lng: -73.5539925
# lat: 45.594576
# lng: -73.641535
# lat: 45.472854
# lng: -73.57296
# lat: 45.563697
# lng: -73.610447
# lat: 45.501531
# lng: -73.574311
# lat: 45.539928
# lng: -73.540388
# lat: 45.464611
# lng: -73.582583
# lat: 45.512189
# lng: -73.566842
# lat: 45.593325
# lng: -73.637328
# lat: 45.502648
# lng: -73.663913
# lat: 45.52055
# lng: -73.563222
# lat: 45.497859
# lng: -73.573035
# lat: 45.542767
# lng: -73.572039
# lat: 45.56221
# lng: -73.571785
# lat: 45.4660102
# lng: -73.6336838
# lat: 45.602846
# lng: -73.558874
# lat: 45.439119
# lng: -73.7333
# lat: 45.60176
# lng: -73.541992
# lat: 45.641026
# lng: -73.499682
# lat: 45.468297
# lng: -73.741185
# lat: 45.426509
# lng: -73.928944

#17. print out the air quality index for each item AND the uid for each item. The output needs to be neat and labelled!
for item in responseData:
    aqi = item["aqi"] #access the value of each item's air quality index through its key "aqi"
    uid = item["uid"] #access the value of each item's unique ID through its key "uid"
    print("aqi:",aqi) #print aqi first
    print("uid:",uid) #print uid after

# Results from 17
# aqi: 18
# uid: 5922
# aqi: 61
# uid: 8596
# aqi: 53
# uid: 8594
# aqi: 47
# uid: 8696
# aqi: 44
# uid: 5465
# aqi: 41
# uid: 5463
# aqi: 41
# uid: 10716
# aqi: 24
# uid: 10138
# aqi: 21
# uid: 5461
# aqi: 21
# uid: 8628
# aqi: 21
# uid: 8626
# aqi: 18
# uid: 5467
# aqi: 18
# uid: 8595
# aqi: -
# uid: 8695
# aqi: -
# uid: 5462
# aqi: 21
# uid: 8625
# aqi: 41
# uid: 8627
# aqi: 21
# uid: 5460
# aqi: 17
# uid: 5459
# aqi: 21
# uid: 5466
# aqi: 24
# uid: 5468


#18. access the feed 
url_feed = "https://api.waqi.info/feed/@5468"
response_feed = requests.get(url_feed, params={"token": token})
results_feed = response_feed.json()
print(results_feed)

print(results_feed["data"]) #19. access the content associated with the data field
response_feed_data = results_feed["data"] #20. store content in variable
print(type(response_feed_data)) #21. variable type is a dictionary <class 'dict'>

#22. write a for loop to iterate through the `response_data_feed` variable . Document the results
for item in response_feed_data:
    print(item)
# Results from 22
# aqi
# idx
# attributions
# city
# dominentpol
# iaqi
# time
# forecast
# debug
# 23. according to the documentation what does aqi and dominentpol field represent?
print(response_feed_data["aqi"]) # this is a number type field representing Real-time air quality information.
print(response_feed_data["dominentpol"]) # this data represents a key to pm25 value.
# save both as varibles
aqi_feed = response_feed_data["aqi"]
dominentpol = response_feed_data["dominentpol"]

# access iaqi field
print(response_feed_data["iaqi"])
iaqi= response_feed_data["iaqi"] # saved dict as a varible

# print the keys and then values without 'v'
for key in iaqi:
    print(key)
    print(iaqi[key]["v"])
# results: 
# co
# 6.4
# h
# 75
# no2
# 7.4
# o3
# 13
# p
# 1017.7
# pm25
# 18
# so2
# 5.1
# t
# 18.1
# w
# 2
# wg
# 3.3

print(dominentpol) # is pm25
# access value of pm25 through key in iaqi
print(iaqi['pm25']) # is {'v': 18}
