# We first set up the city

city_id=$(curl -X 'POST' \
  'http://127.0.0.1:8000/tasks/city_setup' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "city": {
    "viladecans": {
      "nominatimstring": "Viladecans, Barcelona, Spain"
    }
  }
}'| jq -r '.task_id')

echo "\n Waiting for city setup to finish\n"
while true; do
status=$(curl -s -X GET "http://127.0.0.1:8000/tasks/status/$city_id" \
  -H "accept: application/json" | jq -r '.status')

  if [[ "$status" == "Completed" ]]; then
    echo "Task completed!"
    break
  fi
  sleep 1
done
#This produces the map

task_id=$(curl -s -X 'POST' \
  'http://127.0.0.1:8000/tasks/run' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "city": {
    "viladecans": {
      "nominatimstring": "Viladecans, Barcelona, Spain"
    }
  },
  "prune_measure": "betweenness",
  "prune_quantiles": 40,
  "h3_zoom": 10,
  "sliders": {
    "sanidad": 1,
    "educacion": 2,
    "administracion": 2,
    "aprovisionamiento": 3,
    "cultura": 4,
    "deporte": 5,
    "transporte": 2
  },
  "buffer_walk_distance": 500
}' | jq -r '.task_id')

echo "\n Waiting for running task to finish\n"
while true; do
status=$(curl -s -X GET "http://127.0.0.1:8000/tasks/status/$task_id" \
  -H "accept: application/json" | jq -r '.status')

  if [[ "$status" == "Completed" ]]; then
    echo "Task completed!"
    break
  fi
  sleep 1
done
# This downloads the maps
echo "\n Downloading geojson map"
curl -H "Accept: application/geo+json" -o output.geojson http://127.0.0.1:8000/tasks/map/$task_id