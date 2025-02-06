#!/bin/bash
# We initialize variables
p=""

# We first parse the command line argument
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -p) p="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done
# We check if  p was provided and if not, fix it to default values.
if [[ -z "$p" ]]; then
    p=8000
fi

echo "Running CicloAPI in port $p"
echo "---------------------------------"

echo "Building the API"

####################
rm -r dist #Removes dist folder if existing
uv build #Builds the package

echo "Building docker image"

docker build -t cicloapi . #Builds the docker container
docker run -p $p:8000 cicloapi #Runs the docker container in port 8000


