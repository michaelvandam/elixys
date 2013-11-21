#!/bin/bash
# File shall be placed in a folder of .seq files
# Shell script shall convert all the .seq files into
# .p (Python Pickle) files.

echo "Converting all .seq files in the current directory..."
if [ ! -d "/opt/elixys/config" ]; then
    echo "Could not find directory '/opt/elixys/config'"
    exit
fi

if [ ! -f "/opt/elixys/config/sequence_json_to_pickle.py" ]; then
    echo "Could not find Python file '/opt/elixys/config/sequence_json_to_pickle.py"
    exit
fi

# Obtain all .seq files in the current directory.
# Run the python coverter on each file.
for files in *.seq
do
    python /opt/elixys/config/sequence_json_to_pickle.py -l $files
done

echo "Sucessfully converted all .seq files!"
echo "All .p files are located in the current path."
