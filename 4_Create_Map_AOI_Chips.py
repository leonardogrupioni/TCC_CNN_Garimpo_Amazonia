import math
from pathlib import Path
import folium
import geopandas as gpd
from folium.plugins import Fullscreen
from shapely.geometry import box, Polygon

SHP_GARIMPO = "SHP_Garimpo_Files/mineria.shp"
AOI_W, AOI_S, AOI_E, AOI_N = -58.338611, -8.546111, -54.683611, -4.495833
OUT_HTML = "map_demo_aoi_shp_chips.html"

CHIP_SIZE_METERS = 128 * 10

LIGHT_BLUE = "#52a9ff"
GRID_COLOR = "yellow"

def build_grid_inside_aoi(aoi_latlon: Polygon, cell_m: float) -> gpd.GeoDataFrame:
    gdf_aoi = gpd.GeoDataFrame(geometry=[aoi_latlon], crs="EPSG:4326").to_crs("EPSG:3857")
    aoi = gdf_aoi.geometry.iloc[0]
    xmin, ymin, xmax, ymax = aoi.bounds

    def snap_down(v, s): return math.floor(v / s) * s
    def snap_up(v, s):   return math.ceil(v / s) * s

    gxmin = snap_down(xmin, cell_m)
    gymin = snap_down(ymin, cell_m)
    gxmax = snap_up(xmax,  cell_m)
    gymax = snap_up(ymax,  cell_m)

    boxes = []
    y = gymin
    while y + cell_m <= gymax + 1e-9:
        x = gxmin
        while x + cell_m <= gxmax + 1e-9:
            cell = box(x, y, x + cell_m, y + cell_m)
            if cell.within(aoi): # apenas cels totalmente dentro da AOI
                boxes.append(cell)
            x += cell_m
        y += cell_m

    gdf_grid = gpd.GeoDataFrame(geometry=boxes, crs="EPSG:3857").to_crs("EPSG:4326")
    return gdf_grid

def format_coord(lat, lon, decimals=6):
    return f"{lat:.{decimals}f}, {lon:.{decimals}f}"

def main():
    center = [(AOI_S + AOI_N) / 2, (AOI_W + AOI_E) / 2]
    m = folium.Map(location=center, zoom_start=8, tiles="OpenStreetMap", control_scale=True)
    Fullscreen().add_to(m)

    # Bases
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        attr="Google Satellite",
        name="Satélite (Google)",
        overlay=False
    ).add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery",
        name="Satélite (Esri)",
        overlay=False
    ).add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
        attr="Esri Boundaries & Places",
        name="Cidades/limites (Esri)",
        overlay=True
    ).add_to(m)

    # AOI
    folium.Rectangle(
        bounds=[[AOI_S, AOI_W], [AOI_N, AOI_E]],
        color=LIGHT_BLUE, weight=3, fill=False, name="AOI"
    ).add_to(m)

    # Cantos
    corners = {"SW": (AOI_S, AOI_W), "SE": (AOI_S, AOI_E), "NE": (AOI_N, AOI_E), "NW": (AOI_N, AOI_W)}
    for label, (lat, lon) in corners.items():
        folium.Marker(
            location=[lat, lon],
            tooltip=f"{label} • {format_coord(lat, lon)}",
            icon=folium.Icon(color="lightblue", icon="info-sign")
        ).add_to(m)

    # Garimpo (SHP)
    gdf_garimpo = gpd.read_file(SHP_GARIMPO)
    if gdf_garimpo.crs is None:
        pass
    gdf_garimpo = gdf_garimpo.to_crs("EPSG:4326")
    folium.GeoJson(
        data=gdf_garimpo.__geo_interface__,
        name="Garimpo (SHP)",
        style_function=lambda x: {"color": "red", "weight": 1.5, "fill": False}
    ).add_to(m)

    # Grade de chips 1280m dentro da AOI
    aoi_poly = box(AOI_W, AOI_S, AOI_E, AOI_N)
    grid = build_grid_inside_aoi(aoi_poly, CHIP_SIZE_METERS)
    folium.GeoJson(
        data=grid.__geo_interface__,
        name="Chips 1280m (grade)",
        style_function=lambda x: {"color": GRID_COLOR, "weight": 0.7, "fill": False}
    ).add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    m.save(OUT_HTML)
    print(f"[OK] Mapa salvo em: {OUT_HTML}")

if __name__ == "__main__":
    main()
