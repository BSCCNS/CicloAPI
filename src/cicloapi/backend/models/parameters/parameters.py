# PARAMETERS
# These are values to loop through for different runs
poi_source = "grid"  # railwaystation, grid
prune_measure = "betweenness"  # betweenness, clo seness, random

SERVER = False  # Whether the code runs on the server (important to avoid parallel job conflicts)


# SEMI-CONSTANTS
# These values should not be changed, unless the analysis shows we need to

smallcitythreshold = 46  # cities smaller or equal than this rank in the city list will be treated as "small" and get full calculations
prune_measures = {"betweenness": "Bq", "closeness": "Cq", "random": "Rq"}
prune_quantiles = [
    x / 40 for x in list(range(1, 41))
]  # The quantiles where the GT should be pruned using the prune_measure
networktypes = [
    "biketrack",
    "carall",
    "bikeable",
    "biketrackcarall",
    "biketrack_onstreet",
    "bikeable_offstreet",
]  # Existing infrastructures to analyze

# 02
gridl = 1707  # in m, for generating the grid
# https://en.wikipedia.org/wiki/Right_triangle#Circumcircle_and_incircle
# 2*0.5 = a+a-sqrt(2)a   |   1 = a(2-sqrt2)   |   a = 1/(2-sqrt2) = 1.707
# This leads to a full 500m coverage when a (worst-case) square is being triangulated
bearingbins = (
    72  # number of bins to determine bearing. e.g. 72 will create 5 degrees bins
)

h3_zoom = 8

# Example slider value

sanidad_slider = 5
educacion_slider = 6
administracion_slider = 7
aprovisionamiento_slider = 8
cultura_slider = 9
deporte_slider = 10
transporte_slider = 10

poiparameters = {
    # Sanidad (Health)
    "hospital": {"amenity": "hospital"},
    "clinic": {"amenity": "clinic"},
    "pharmacy": {"amenity": "pharmacy"},
    "dentist": {"amenity": "dentist"},
    "veterinary": {"amenity": "veterinary"},
    "daycare": {"amenity": "social_facility", "social_facility": "day_care"},
    "socialservices": {"amenity": "social_facility"},
    "doctors": {"amenity": "doctors"},
    "nursing_home": {"amenity": "nursing_home"},
    # "optician": {'shop': 'optician'},
    # Educación (Education)
    "school": {"amenity": "school"},
    "university": {"amenity": "university"},
    "kindergarten": {"amenity": "kindergarten"},
    "college": {"amenity": "college"},
    "training": {"amenity": "training"},
    "language_school": {"amenity": "language_school"},
    "music_school": {"amenity": "music_school"},
    # Administración (Administration)
    "townhall": {"amenity": "townhall"},
    "courthouse": {"amenity": "courthouse"},
    "police": {"amenity": "police"},
    "firestation": {"amenity": "fire_station"},
    "postoffice": {"amenity": "post_office"},
    "media": {"office": "media"},
    "embassy": {"amenity": "embassy"},
    "recycling": {"amenity": "recycling"},
    # Aprovisionamiento (Supplies)
    "supermarket": {"shop": "supermarket"},
    "mall": {"shop": "mall"},
    "bakery": {"shop": "bakery"},
    "butcher": {"shop": "butcher"},
    "greengrocer": {"shop": "greengrocer"},
    "marketplace": {"amenity": "marketplace"},
    "electronics": {"shop": "electronics"},
    "clothes": {"shop": "clothes"},
    "furniture": {"shop": "furniture"},
    "hardware": {"shop": "hardware"},
    "beverages": {"shop": "beverages"},
    "convenience": {"shop": "convenience"},
    # Cultura/Ocio (Culture/Leisure)
    "museum": {"tourism": "museum"},
    "theatre": {"amenity": "theatre"},
    "cinema": {"amenity": "cinema"},
    "library": {"amenity": "library"},
    "park": {"leisure": "park"},
    "playground": {"leisure": "playground"},
    "communitycentre": {"amenity": "community_centre"},
    "art_gallery": {"tourism": "art_gallery"},
    "zoo": {"tourism": "zoo"},
    "theme_park": {"tourism": "theme_park"},
    # Otros (Others)
    "place_of_worship": {"amenity": "place_of_worship"},
    "atm": {"amenity": "atm"},
    "bank": {"amenity": "bank"},
    "restaurant": {"amenity": "restaurant"},
    "cafe": {"amenity": "cafe"},
    "bar": {"amenity": "bar"},
    "fast_food": {"amenity": "fast_food"},
    "hotel": {"tourism": "hotel"},
    "hostel": {"tourism": "hostel"},
    "camp_site": {"tourism": "camp_site"},
    "public_toilet": {"amenity": "toilets"},
    "fountain": {"amenity": "fountain"},
    # Deporte (Sports)
    "sportscentre": {"leisure": "sports_centre"},  # General sports center
    "stadium": {"leisure": "stadium"},  # Sports stadiums
    "swimmingpool": {"leisure": "swimming_pool"},  # Swimming pools
    "pitch": {"leisure": "pitch"},  # Sports pitches (soccer, rugby, etc.)
    "fitnesscentre": {"leisure": "fitness_centre"},  # Fitness gyms and centers
    "outdoor_sports": {"leisure": "sports"},  # General outdoor sports areas
    "climbing": {"sport": "climbing"},  # Rock climbing walls and facilities
    "golf_course": {"leisure": "golf_course"},  # Golf courses
    "tennis": {"leisure": "pitch", "sport": "tennis"},  # Tennis courts
    "basketball": {"leisure": "pitch", "sport": "basketball"},  # Basketball courts
    "skatepark": {"leisure": "skatepark"},  # Skateboarding parks
    "equestrian": {"sport": "equestrian"},  # Equestrian facilities
    "ice_rink": {"leisure": "ice_rink"},  # Ice skating rinks
    "bowling": {"amenity": "bowling_alley"},  # Bowling alleys
    "running_track": {"leisure": "track", "sport": "running"},  # Running tracks
    "table_tennis": {"sport": "table_tennis"},  # Table tennis facilities
    "squash": {"sport": "squash"},  # Squash courts
    "volleyball": {"sport": "volleyball"},  # Volleyball courts
    "cricket": {"sport": "cricket"},  # Cricket pitches
    "baseball": {"sport": "baseball"},  # Baseball diamonds
    "boating": {"leisure": "marina"},  # Boating and marinas
    "fishing": {"leisure": "fishing"},  # Fishing areas
    "shooting": {"sport": "shooting"},  # Shooting ranges
    "archery": {"sport": "archery"},  # Archery ranges
    "surfing": {"sport": "surfing"},  # Surfing spots
    "skiing": {"sport": "skiing"},  # Skiing facilities
    "motor_sports": {"sport": "motor"},  # Motor sports facilities
    "cycling": {"sport": "cycling"},  # Cycling tracks or paths
    "rowing": {"sport": "rowing"},  # Rowing facilities
    "karate": {"sport": "karate"},  # Karate or martial arts dojos
    "yoga": {"sport": "yoga"},  # Yoga centers or studios
    "paddle": {"sport": "paddle_tennis"},  # Paddle tennis courts
    "rugby": {"sport": "rugby"},  # Rugby pitches
    "hockey": {"sport": "hockey"},  # Hockey fields or rinks
    "badminton": {"sport": "badminton"},  # Badminton courts
    "diving": {"sport": "diving"},  # Diving facilities
    "horse_racing": {"sport": "horse_racing"},  # Horse racing tracks
    "skating": {"sport": "skating"},  # Skating rinks or facilities
    "kitesurfing": {"sport": "kitesurfing"},  # Kitesurfing locations
    "paragliding": {"sport": "paragliding"},  # Paragliding locations
    "windsurfing": {"sport": "windsurfing"},  # Windsurfing spots
    "aerobics": {"sport": "aerobics"},  # Aerobics studios
    "parkour": {"sport": "parkour"},  # Parkour parks or spots
    "futsal": {"sport": "futsal"},  # Futsal pitches
    # Transporte (Transport)
    "railwaystation": {"railway": ["station", "halt"]},  # Train stations and halts
    "busstop": {"highway": "bus_stop"},  # Bus stops
    "tramstop": {"railway": "tram_stop"},  # Tram stops
    "subwayentrance": {"railway": "subway_entrance"},  # Subway entrances
    "taxistand": {"amenity": "taxi"},  # Taxi stands
    "parking": {"amenity": "parking"},  # Parking lots
    "bicyclerental": {"amenity": "bicycle_rental"},  # Bicycle rental services
    "car_rental": {"amenity": "car_rental"},  # Car rental services
    "fuel": {"amenity": "fuel"},  # Fuel stations
    "charging_station": {"amenity": "charging_station"},  # EV charging stations
    "ferry_terminal": {"amenity": "ferry_terminal"},  # Ferry terminals
    "aerodrome": {"aeroway": "aerodrome"},  # Small airfields and private airports
    "airport": {"aeroway": "airport"},  # Airports
    "helipad": {"aeroway": "helipad"},  # Helipads
    "bus_station": {"amenity": "bus_station"},  # Bus stations
    "coach_stop": {"amenity": "coach_station"},  # Long-distance coach stops
    "motorcycle_parking": {"amenity": "motorcycle_parking"},  # Motorcycle parking areas
    "bicycle_parking": {"amenity": "bicycle_parking"},  # Bicycle parking areas
    "train_crossing": {"railway": "level_crossing"},  # Railway level crossings
    "tramway": {"railway": "tram"},  # Tramway infrastructure
    "subway_station": {"railway": "subway"},  # Subway stations
    "monorail": {"railway": "monorail"},  # Monorail systems
    "light_rail": {"railway": "light_rail"},  # Light rail stations
    "park_and_ride": {"amenity": "park_and_ride"},  # Park-and-ride facilities
    "bus_shelter": {
        "amenity": "shelter",
        "shelter_type": "public_transport",
    },  # Bus shelters
    "cargo_terminal": {"landuse": "depot"},  # Cargo or freight terminals
    "container_terminal": {
        "man_made": "container_terminal"
    },  # Shipping container terminals
    "seaport": {"amenity": "seaport"},  # Seaports
    "dock": {"man_made": "dock"},  # Docks
    "carpool_parking": {"amenity": "carpool_parking"},  # Carpool parking lots
    "toll_booth": {"barrier": "toll_booth"},  # Toll booths
    "customs": {"amenity": "customs"},  # Customs facilities at borders
    "weigh_station": {"amenity": "weighbridge"},  # Weigh stations for trucks
    "pier": {"man_made": "pier"},  # Piers and wharfs
    "boat_rental": {"amenity": "boat_rental"},  # Boat rental services
    "canoe_rental": {"sport": "canoe"},  # Canoe or kayak rentals
    "car_sharing": {"amenity": "car_sharing"},  # Car sharing services
    "roadside_rest_area": {"highway": "rest_area"},  # Roadside rest areas
    "service_area": {"highway": "services"},  # Service areas on highways
    "bike_repair_station": {
        "amenity": "bicycle_repair_station"
    },  # Bicycle repair stations
    "tram_depot": {"railway": "tram_depot"},  # Tram depots
    "bus_depot": {"railway": "bus_depot"},  # Bus depots
    "cable_car": {"aerialway": "cable_car"},  # Cable car systems
    "gondola": {"aerialway": "gondola"},  # Gondola lifts
    "chair_lift": {"aerialway": "chair_lift"},  # Chair lifts
    "funicular": {"aerialway": "funicular"},  # Funicular railways
}


sanidad = {
    "hospital": {"amenity": "hospital"},
    "clinic": {"amenity": "clinic"},
    "pharmacy": {"amenity": "pharmacy"},
    "dentist": {"amenity": "dentist"},
    "veterinary": {"amenity": "veterinary"},
}

educacion = {
    "school": {"amenity": "school"},
    "university": {"amenity": "university"},
    "kindergarten": {"amenity": "kindergarten"},
    "college": {"amenity": "college"},
}

administracion = {
    "townhall": {"amenity": "townhall"},
    "courthouse": {"amenity": "courthouse"},
    "police": {"amenity": "police"},
    "firestation": {"amenity": "fire_station"},
    "postoffice": {"amenity": "post_office"},
}

aprovisionamiento = {
    "supermarket": {"shop": "supermarket"},
    "mall": {"shop": "mall"},
    "bakery": {"shop": "bakery"},
    "butcher": {"shop": "butcher"},
    "greengrocer": {"shop": "greengrocer"},
    "marketplace": {"amenity": "marketplace"},
}

cultura = {
    "museum": {"tourism": "museum"},
    "theatre": {"amenity": "theatre"},
    "cinema": {"amenity": "cinema"},
    "library": {"amenity": "library"},
    "park": {"leisure": "park"},
    "playground": {"leisure": "playground"},
}

deporte = {
    "sportscentre": {"leisure": "sports_centre"},
    "stadium": {"leisure": "stadium"},
    "swimmingpool": {"leisure": "swimming_pool"},
    "pitch": {"leisure": "pitch"},
    "fitnesscentre": {"leisure": "fitness_centre"},
}

transporte = {
    "railwaystation": {"railway": ["station", "halt"]},
    "busstop": {"highway": "bus_stop"},
    "tramstop": {"railway": "tram_stop"},
    "subwayentrance": {"railway": "subway_entrance"},
    "taxistand": {"amenity": "taxi"},
    "parking": {"amenity": "parking"},
}

# 04
buffer_walk = (
    500  # Buffer in m for coverage calculations. (How far people are willing to walk)
)
numnodepairs = 500  # Number of node pairs to consider for random sample to calculate directness (O(numnodepairs^2), so better not go over 1000)

# 05
nodesize_grown = 7.5
plotparam = {
    "bbox": (1280, 1280),
    "dpi": 96,
    "carall": {"width": 0.5, "edge_color": "#999999"},
    # "biketrack": {"width": 1.25, "edge_color": '#2222ff'},
    "biketrack": {"width": 1, "edge_color": "#000000"},
    "biketrack_offstreet": {"width": 0.75, "edge_color": "#00aa22"},
    "bikeable": {"width": 0.75, "edge_color": "#222222"},
    # "bikegrown": {"width": 6.75, "edge_color": '#ff6200', "node_color": '#ff6200'},
    # "highlight_biketrack": {"width": 6.75, "edge_color": '#0eb6d2', "node_color": '#0eb6d2'},
    "bikegrown": {"width": 3.75, "edge_color": "#0eb6d2", "node_color": "#0eb6d2"},
    "highlight_biketrack": {
        "width": 3.75,
        "edge_color": "#2222ff",
        "node_color": "#2222ff",
    },
    "highlight_bikeable": {
        "width": 3.75,
        "edge_color": "#222222",
        "node_color": "#222222",
    },
    "poi_unreached": {"node_color": "#ff7338", "edgecolors": "#ffefe9"},
    "poi_reached": {"node_color": "#0b8fa6", "edgecolors": "#f1fbff"},
    "abstract": {"edge_color": "#000000", "alpha": 0.75},
}

plotparam_analysis = {
    "bikegrown": {
        "linewidth": 3.75,
        "color": "#0eb6d2",
        "linestyle": "solid",
        "label": "Grown network",
    },
    "bikegrown_abstract": {
        "linewidth": 3.75,
        "color": "#000000",
        "linestyle": "solid",
        "label": "Grown network (unrouted)",
        "alpha": 0.75,
    },
    "mst": {"linewidth": 2, "color": "#0eb6d2", "linestyle": "dashed", "label": "MST"},
    "mst_abstract": {
        "linewidth": 2,
        "color": "#000000",
        "linestyle": "dashed",
        "label": "MST (unrouted)",
        "alpha": 0.75,
    },
    "biketrack": {
        "linewidth": 1,
        "color": "#2222ff",
        "linestyle": "solid",
        "label": "Protected",
    },
    "bikeable": {
        "linewidth": 1,
        "color": "#222222",
        "linestyle": "dashed",
        "label": "Bikeable",
    },
    "constricted": {
        "linewidth": 3.75,
        "color": "#D22A0E",
        "linestyle": "solid",
        "label": "Street network",
    },
    "constricted_SI": {
        "linewidth": 2,
        "color": "#D22A0E",
        "linestyle": "solid",
        "label": "Street network",
    },
    "constricted_3": {
        "linewidth": 2,
        "color": "#D22A0E",
        "linestyle": "solid",
        "label": "Top 3%",
    },
    "constricted_5": {
        "linewidth": 2,
        "color": "#a3210b",
        "linestyle": "solid",
        "label": "Top 5%",
    },
    "constricted_10": {
        "linewidth": 2,
        "color": "#5a1206",
        "linestyle": "solid",
        "label": "Top 10%",
    },
    "bikegrown_betweenness": {
        "linewidth": 2.5,
        "color": "#0eb6d2",
        "linestyle": "solid",
        "label": "Betweenness",
    },
    "bikegrown_closeness": {
        "linewidth": 2,
        "color": "#186C7A",
        "linestyle": "dashed",
        "label": "Closeness",
    },
    "bikegrown_random": {
        "linewidth": 1.5,
        "color": "#222222",
        "linestyle": "dotted",
        "label": "Random",
    },
}

constricted_parameternamemap = {
    "betweenness": "_metrics",
    "grid": "",
    "railwaystation": "_rail",
}
constricted_plotinfo = {
    "title": [
        "Global Efficiency",
        "Local Efficiency",
        "Directness of LCC",
        "Spatial Clustering",
        "Anisotropy",
    ]
}
analysis_existing_rowkeys = {
    "bikeable": 0,
    "bikeable_offstreet": 1,
    "biketrack": 2,
    "biketrack_onstreet": 3,
    "biketrackcarall": 4,
    "carall": 5,
}


# CONSTANTS
# These values should be set once and not be changed

# 01
osmnxparameters = {
    "car30": {
        "network_type": "drive",
        "custom_filter": '["maxspeed"~"^30$|^20$|^15$|^10$|^5$|^20 mph|^15 mph|^10 mph|^5 mph"]',
        "export": True,
        "retain_all": True,
    },
    "carall": {
        "network_type": "drive",
        "custom_filter": None,
        "export": True,
        "retain_all": False,
    },
    "bike_cyclewaytrack": {
        "network_type": "bike",
        "custom_filter": '["cycleway"~"track"]',
        "export": False,
        "retain_all": True,
    },
    "bike_highwaycycleway": {
        "network_type": "bike",
        "custom_filter": '["highway"~"cycleway"]',
        "export": False,
        "retain_all": True,
    },
    "bike_designatedpath": {
        "network_type": "all",
        "custom_filter": '["highway"~"path"]["bicycle"~"designated"]',
        "export": False,
        "retain_all": True,
    },
    "bike_cyclewayrighttrack": {
        "network_type": "bike",
        "custom_filter": '["cycleway:right"~"track"]',
        "export": False,
        "retain_all": True,
    },
    "bike_cyclewaylefttrack": {
        "network_type": "bike",
        "custom_filter": '["cycleway:left"~"track"]',
        "export": False,
        "retain_all": True,
    },
    "bike_cyclestreet": {
        "network_type": "bike",
        "custom_filter": '["cyclestreet"]',
        "export": False,
        "retain_all": True,
    },
    "bike_bicycleroad": {
        "network_type": "bike",
        "custom_filter": '["bicycle_road"]',
        "export": False,
        "retain_all": True,
    },
    "bike_livingstreet": {
        "network_type": "bike",
        "custom_filter": '["highway"~"living_street"]',
        "export": False,
        "retain_all": True,
    },
}
# Special case 'biketrack': "cycleway"~"track" OR "highway"~"cycleway" OR "bicycle"~"designated" OR "cycleway:right=track" OR "cycleway:left=track" OR ("highway"~"path" AND "bicycle"~"designated") OR "cyclestreet" OR "highway"~"living_street"
# Special case 'bikeable': biketrack OR car30
# See: https://wiki.openstreetmap.org/wiki/Key:cycleway#Cycle_tracks
# https://wiki.openstreetmap.org/wiki/Tag:highway=path#Usage_as_a_universal_tag
# https://wiki.openstreetmap.org/wiki/Tag:highway%3Dliving_street
# https://wiki.openstreetmap.org/wiki/Key:cyclestreet


# 02
snapthreshold = 500  # in m, tolerance for snapping POIs to network
