existing_locations_csv = 'taxi_zones.csv'
standard_query = "SELECT SUM(total_amount) FROM 'yellow_tripdata_2017-04' WHERE "
unused_columns = ['VendorID',
                  'tpep_pickup_datetime',
                  'passenger_count',
                  'trip_distance',
                  'RatecodeID',
                  'store_and_fwd_flag',
                  'PULocationID',
                  'fare_amount',
                  'extra',
                  'mta_tax',
                  'tip_amount',
                  'tolls_amount',
                  'improvement_surcharge',
                  'total_amount']
payment_methods_dict = {"Credit Card": 1,
                        "Cash": 2,
                        "No Charge": 3,
                        "Dispute":  4,
                        "Unknown": 5,
                        "Voided": 6}
