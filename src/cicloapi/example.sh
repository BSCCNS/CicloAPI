# We first set up the city

curl -X 'POST' \
  'http://127.0.0.1:8000/tasks/city_setup' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "city": {
    "viladecans": {
      "nominatimstring": "Viladecans, Barcelona, Spain"
    }
  }
}'

#This produces the map

curl -X 'POST' \
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
}'

# This downloads the maps

curl -H "Accept: application/geo+json" -o output.geojson http://127.0.0.1:8000/tasks/map/127be4e1-4af5-4264-93fd-342e0b87d468
