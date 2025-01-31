
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

#---------------------------------------------------------#
from scripts import path
from scripts.initialize import cities
from scripts import prepare_networks,prepare_pois, cluster_pois
from parameters.parameters import h3_zoom, snapthreshold, sanidad_slider, educacion_slider, administracion_slider, aprovisionamiento_slider, cultura_slider, deporte_slider, transporte_slider
debug = False
PATH = path.PATH


if __name__ == '__main__':

    print("Running 01.py")
    prepare_networks.main(PATH, cities)

    print("Running 02.py")
    prepare_pois.main(PATH, cities)

    print("Running 03.py")
    cluster_pois.main(PATH, cities, h3_zoom, snapthreshold, sanidad_slider, educacion_slider, administracion_slider, aprovisionamiento_slider,cultura_slider, deporte_slider, transporte_slider)
    