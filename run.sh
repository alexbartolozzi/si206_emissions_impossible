#!/bin/bash

# Run the application
source env/bin/activate
echo "python main.py new 0 _"
python main.py new 0 _

for i in {1..56}
do
  if [ "$i" -gt 28 ]; then
    echo "python main.py _ $i halfway"
    python main.py _ "$i" halfway
  else
    echo "python main.py _ $i _"
    python main.py _ "$i" _
  fi
done
echo "python main.py done 57 halfway"
python main.py done 57 halfway