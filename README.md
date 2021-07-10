# Description
A module for timing individual MongoDB write operations across a range of write concerns.
No special tuning or handling for failed writes, network partitions, or failovers.
Therefore, only appropriate for small number of write operations where you can be reasonable certain of 100% successful writes (ie reliable network and MongoDB server)
Recommended max: 100 from a remote client or 1000 for a robust datacenter with client colocated with the MongoDB primary.

# Verify that python3 is installed
python3 --version

# install libraries.
python3 -m pip install -r requirements.txt

# Connection String:
Python module uses a mongodb connection string located in a file in the project root called "mongodb_connection_string.txt"
Content of mongodb_connection_string.txt should be the target mongodb connection string (without quotes).

# Connection String for git contributors:
If you are contributing code, you can put your connections string in a file called my_mongodb_connection_string.txt.
Be sure to include that file in your .gitignore so that you do not submit any db credentials to the git repo.

# Write Tests Usage: Example to run the default number of tests for each write concern (DEFAULT: 100)
python3 ack_time_by_write_concern.py

### Write Tests Usage: Example to run and time 200 tests for each write concern:
python3 ack_time_by_write_concern.py 200


# Read Test Usage: Example to run the default number of tests for each combination of read concern and read preference:
python3 read_tests.py 

### Read Tests Usage:  Example to run and time 200 tests for each combination of read concern and read preference:
python3 read_tests.py 200


### Configuration for a replica set:
read_tests.py queries an existing cluster. The query used for the tests can be configured under the variable test_query.

### Configuration for a MongoDB Global Cluster:
For performing read_tests.py on a MongoDB Global Cluster, put an instance of this code onto a client in one or more local zones. Update app.conf with the local zone code (e.g. "US-VA"). read_test will use this value in test_query for performing the read tests.
