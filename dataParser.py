import json
import pandas as pd
#import plotly.express as px
import plotly.express as px
#from plotly import offline
import sys
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point


def parse_json_to_excel(input_file, output_excel=None,plot=True):
    # Containers for echook and gps records
    echook_data = []
    gps_data = []

    # Read the newline-delimited JSON
    with open(input_file, "r") as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            base = {"SeqNo": entry.get("SeqNo"), "Timestamp": entry.get("Timestamp")}
            
            if "echook" in entry:
                echookDict=entry["echook"]
                try:
                    echookDict['echookTimestamp'] = echookDict.pop('Timestamp') #Timestamp is present in the top, so have an echookTimestamp
                except:
                    pass
                try:
                   echookDict['echookSeqNo'] = echookDict.pop('SeqNo') #Seq No is present in the top, so have an echookSeqNo
                except:
                    pass

                merged = {**base, **echookDict}
                echook_data.append(merged)
            if "gps" in entry:
                merged = {**base, **entry["gps"]}
                gps_data.append(merged)

    # Convert to DataFrames
    df_echook = pd.DataFrame(echook_data)
    df_gps = pd.DataFrame(gps_data)

    #import pdb
    #pdb.set_trace()
    if output_excel:
        # Save to Excel with two sheets
        with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
            df_echook.to_excel(writer, sheet_name="echook", index=False)
            df_gps.to_excel(writer, sheet_name="gps", index=False)

        print(f"Excel file saved as: {output_excel}")

    oldplot=False
    if oldplot:
        print("Plotting to a map")
        
        fig = px.scatter_geo(df_gps,lat='Lat',lon='Lng', hover_name="Timestamp")
        #fig = px.scatter_geo(df_gps,lat='Lat',lon='Lng', hover_name="Timestamp",color='Speed')
        if 1:
            fig.update_layout(title = 'World map', title_x=0.5)
            lat_foc = df_gps.mean()["Lat"]
            lon_foc = df_gps.mean()["Lng"]
            lat_foc = 51.117675
            lon_foc = -0.542965
            fig.update_layout(
                geo = dict(
                    projection_scale=10, #this is kind of like zoom
                    center=dict(lat=lat_foc, lon=lon_foc), # this will center on the point
                ))
        fig.show()
    if plot:
        # Convert to GeoDataFrame
        gdf = gpd.GeoDataFrame(
            df_gps,
            geometry=gpd.points_from_xy(df_gps['Lng'], df_gps['Lat']),
            crs='EPSG:4326'  # WGS84 Latitude/Longitude
        )

        # Load world map
        url= "ne_110m_admin_0_countries.zip"
        world = gpd.read_file(url)

        # Plot
        fig, ax = plt.subplots(figsize=(10, 6))
        world.plot(ax=ax, color='lightgray', edgecolor='black')
        gdf.plot(column=df_gps['Speed'],ax=ax, markersize=20,legend=True)

        # Annotate points
        for x, y, label in zip(df_gps['Lng'], df_gps['Lat'], df_gps['Timestamp']):
            ax.text(x + 1, y + 1, label, fontsize=9)

        minx, miny, maxx, maxy = gdf.total_bounds
        offset = 0.00001
        ax.set_xlim(minx - offset, maxx + offset)
        ax.set_ylim(miny - offset, maxy + offset)

        # fig=px.scatter_map(
        #     df_gps,
        #     lat="Lat",
        #     lon="Lng",
        #     #color="Speed"
        #     #color_discrete_map={"Eric": "turquoise", "Nico": "green", "Sanne": "brown"},
        # ).update_layout( mapbox={ "style": "carto-positron", "zoom": 1, }, margin={"l": 52, "r": 50, "t": 1, "r": 52}, )

        # fig.show()
        plt.title('Latitude and Longitude Plot using GeoPandas')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.show()


if __name__ == "__main__":
    input_file = "data_small.json"
    output_excel = "output_data.xlsx"
    if(len(sys.argv)<3):
        print("Too Few arguments, use %s input.json output.xlsx"%sys.argv[0])
        exit(0)

    #parse_json_to_excel(sys.argv[1], sys.argv[2])
    parse_json_to_excel(sys.argv[1],sys.argv[2],plot=False)
    parse_json_to_excel(sys.argv[1],None,True)