#!/bin/bash

# Run the application
source env/bin/activate
#TODO: adjust this for count of celebs we fetch
# python main.py new 0
# for i in {1..63}
# do
#   python3 main.py _ $i
# done

echo "python main.py new 0"
for i in {1..56}
do
  echo "python main.py _ $i"
done
echo "python main.py done 57"