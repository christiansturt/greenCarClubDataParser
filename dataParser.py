# File to pass the green car club data from Matthew
# Author: Christian Sturt
# Date: 20/9/2025

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
                gpsDict=entry["gps"]
                try:
                   gpsDict['gpsSeqNo'] = gpsDict.pop('SeqNo') #Seq No is present in the top, so have an gpsSeqNo
                except:
                    pass

                #remove any bad data, there was one in the file
                try:
                    if (gpsDict["Lng"] > 100) or (gpsDict["Lng"] < -100):
                        gpsDict["Lng"] = 0
                except:
                    pass

                merged = {**base, **gpsDict}
                gps_data.append(merged)

    # Convert to DataFrames
    df_echook = pd.DataFrame(echook_data)
    df_gps = pd.DataFrame(gps_data)


    if output_excel:
        # Save to Excel with two sheets
        #writer = pd.ExcelWriter(output_excel, engine="openpyxl") 
        writer = pd.ExcelWriter(output_excel, engine="xlsxwriter") 
        
        df_echook.to_excel(writer, sheet_name="echook", index=False)
        df_gps.to_excel(writer, sheet_name="gps", index=False)

        workbook = writer.book
        gpsWorksheet = writer.sheets["gps"]
        echookWorksheet = writer.sheets["echook"]

        # Get the dimensions of the dataframe.
        (maxRowGps, maxColGps) = df_gps.shape 
        (maxRowEchook, maxColEchook) = df_echook.shape 

        # Make the columns wider for clarity.
        gpsWorksheet.set_column(0, maxColGps - 1, 12)
        echookWorksheet.set_column(0, maxColEchook - 1, 12)

        # Set the autofilter.
        gpsWorksheet.autofilter(0, 0,maxRowGps, maxColGps - 1)
        echookWorksheet.autofilter(0, 0,maxRowEchook, maxColEchook - 1)

        writer.close()
  

        print(f"Excel file saved as: {output_excel}")

 
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


        plt.title('Latitude and Longitude Plot')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.show()


if __name__ == "__main__":
    if(len(sys.argv)<3):
        print("Too Few arguments, use %s input.json output.xlsx"%sys.argv[0])
        exit(0)

    #parse_json_to_excel(sys.argv[1], sys.argv[2])
    parse_json_to_excel(sys.argv[1],sys.argv[2],plot=False)
    #parse_json_to_excel(sys.argv[1],None,True)
