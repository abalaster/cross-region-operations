import sys
import pymongo
from datetime import datetime as dt
import pandas as pd
from IPython.display import display
from pymongo.write_concern import WriteConcern
import dns


def main(argv):
    arguments = sys.argv[1:]
    if len(arguments) != 0:
        n_writes = int(arguments[0])
    else:
        n_writes = 100

    concerns_to_test = [
        {"w": 0, "j": False},
        {"w": 1, "j": False},
        {"w": 2, "j": False},
        {"w": 1, "j": True},
        {"w": "majority", "j": True},
    ]

    try:
        with open("my_mongodb_connection_string.txt", "r") as f:
            connection_string = f.read().rstrip()
    except FileNotFoundError:
        with open("mongodb_connection_string.txt", "r") as f:
            connection_string = f.read().rstrip()
    with open("app.conf", "r") as f:
        location_value = f.read().rstrip()

    client = pymongo.MongoClient(connection_string)
    db = client.BA
    collection = db.consumer_deposit_account
    collection.insert_one({"test": True})

    def write_one(doc, w_arg, j_arg):
        start_time = dt.now()
        collection.with_options(write_concern=WriteConcern(w=w_arg, j=j_arg)).insert_one(doc)
        end_time = dt.now()
        measured_duration_milliseconds = (end_time - start_time).total_seconds() * 1000
        return measured_duration_milliseconds


    def test_inserts(n_inserts, concerns):
        test_results = {}
        for concern in concerns:
            concern_label = "w:" + str(concern["w"]) + ", j:" + str(concern["j"])
            test_results[concern_label] = None
            results = []
            print("testing write concern: ", str(concern))
            for i in range(n_inserts):
                write_duration = write_one({"test": concern, "location": location_value}, w_arg=concern["w"], j_arg=concern["j"])
                results.append(write_duration)
                test_results[concern_label] = results
        df = pd.DataFrame(test_results)
        return df


    # Run the test
    raw_results = test_inserts(n_writes, concerns_to_test)

    # Display the result stats
    with pd.option_context('display.expand_frame_repr', False, 'display.max_rows', None):
        # display(raw_results)
        display(raw_results.describe())


    client.close()
if __name__ == "__main__":
	main(sys.argv[1:])
