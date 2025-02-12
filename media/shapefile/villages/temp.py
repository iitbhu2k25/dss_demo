import geopandas as gpd
import os
import pandas as pd

def shapefile_to_geojson_and_csv(input_shapefile, output_geojson, output_csv):
    
    try:
        # Read the shapefile
        gdf = gpd.read_file(input_shapefile)
        
        # Check if the shapefile has a CRS (Coordinate Reference System)
        if gdf.crs is not None:
            # Convert to WGS84 (standard for GeoJSON)
            gdf = gdf.to_crs('EPSG:4326')
        
        # Convert to GeoJSON
        gdf.to_file(output_geojson, driver='GeoJSON')
        print(f"Successfully converted {input_shapefile} to {output_geojson}")
        
        # Extract attributes to CSV
        # Get all columns except the geometry column
        attributes_df = gdf.drop(columns=['geometry'])
        attributes_df.to_csv(output_csv, index=False)
        print(f"Successfully exported attributes to {output_csv}")
        
        # Print summary of the conversion
        print("\nConversion Summary:")
        print(f"Number of features: {len(gdf)}")
        print(f"Attributes exported: {', '.join(attributes_df.columns)}")
        
    except Exception as e:
        print(f"Error converting file: {str(e)}")

def main():
   
    input_shapefile = "Basin_Villages.shp"
    output_geojson = "Basin_Villages.geojson"
    output_csv = "Basin_Villages.csv"
    
    # Validate input file exists
    if not os.path.exists(input_shapefile):
        print("Error: Input shapefile does not exist!")
        return
    
    # Validate input file is a shapefile
    if not input_shapefile.lower().endswith('.shp'):
        print("Error: Input file must be a .shp file!")
        return
    
    # Convert the file
    shapefile_to_geojson_and_csv(input_shapefile, output_geojson, output_csv)

if __name__ == "__main__":
    main()