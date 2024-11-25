#!/bin/bash

echo "Container is running!!!"

args="$@"
echo "Command: $args"

if [[ -z ${args} ]]; 
then
    echo "No command provided. Container is ready."
else
    # Remove any unexpected characters and use the full path
    cleaned_args=$(echo "$args" | tr -d '\r\n')
    pipenv run $cleaned_args
fi
