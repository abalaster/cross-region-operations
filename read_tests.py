import sys
import pymongo
import datetime
from datetime import datetime as dt
import pandas as pd
from IPython.display import display
from pymongo.write_concern import WriteConcern
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
import re
import dns


def main(argv):
    try:
        with open("my_mongodb_connection_string.txt", "r") as f:
            connection_string = f.read().rstrip()
    except FileNotFoundError:
        with open("mongodb_connection_string.txt", "r") as f:
            connection_string = f.read().rstrip()
    with open("app.conf", "r") as f:
        location_value = f.read().rstrip()
    arguments = sys.argv[1:]
    if len(arguments) != 0:
        n = int(arguments[0])
    else:
        n = 100

    client = pymongo.MongoClient(connection_string)
    db = client.BA
    acct_balance = db.consumer_deposit_account_balance
    acct_transactions = db.consumer_deposit_account_transactions
    acct_balance.insert_one({"test": True})
    acct_transactions.insert_one({"test": True})

    rc = pymongo.read_concern
    rp = pymongo.read_preferences

    def read_one(query, collection, read_preference, read_concern):
        start_time = dt.now()
        collection.with_options(read_preference=read_preference, read_concern=read_concern).find_one(query)
        end_time = dt.now()
        measured_duration_milliseconds = (end_time - start_time).total_seconds() * 1000
        return measured_duration_milliseconds


    def test_reads(n, concerns):
        test_results = {}
        for concern in concerns:
            # print(concern)
            conc = re.findall(r'\(.*?\)', str(concern["read_concern"]))[0].replace('(', '').replace(')', '')
            pref = str(concern["read_preference"])[:str(concern["read_preference"]).find("(")]
            concern_label = "pref_" + pref + "_concern_" + conc
            print(concern_label)
            test_results[concern_label] = None
            results = []
            print("testing read concerns and preference: ", str(concern["read_concern"]), " ", str(concern["read_preference"]))
            for i in range(n):
                duration = read_one({"account_entity_id": 764584569,
                                     "location": location_value},
                                    collection=acct_balance,
                                    read_preference=concern["read_preference"],
                                    read_concern=concern["read_concern"])
                results.append(duration)
                test_results[concern_label] = results
        df = pd.DataFrame(test_results)
        return df


    concerns_to_test = [
        {"read_concern": rc.ReadConcern("local"), "read_preference": rp.ReadPreference.NEAREST},
        {"read_concern": rc.ReadConcern("local"), "read_preference": rp.ReadPreference.NEAREST},
        {"read_concern": rc.ReadConcern("available"), "read_preference": rp.ReadPreference.NEAREST},
        {"read_concern": rc.ReadConcern("majority"), "read_preference": rp.ReadPreference.NEAREST},
        {"read_concern": rc.ReadConcern("linearizable"), "read_preference": rp.ReadPreference.PRIMARY}
    ]

    # Run the test
    raw_results = test_reads(n, concerns_to_test)

    # Display the result stats
    with pd.option_context('display.expand_frame_repr', False, 'display.max_rows', None):
        # display(raw_results)
        display(raw_results.describe())


    acct_balance.delete_many({"test": True})
    acct_transactions.delete_many({"test": True})


    client.close()

if __name__ == "__main__":
    main(sys.argv[1:])
