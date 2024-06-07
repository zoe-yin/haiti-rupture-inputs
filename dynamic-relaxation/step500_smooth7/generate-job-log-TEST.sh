#!/bin/bash

# >> appends to existing file
echo "This is a test" > test-output.txt
echo $1 >> test-output.txt
echo "The last line should be the jobID" >> test-output.txt