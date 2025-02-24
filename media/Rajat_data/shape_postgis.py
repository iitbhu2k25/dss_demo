import geopandas as gpd
from sqlalchemy import create_engine, Integer
from geoalchemy2 import Geometry, WKTElement

# Database connection details
DB_USER = 'myuser'
DB_PASSWORD = 'mypassword'
DB_HOST = 'localhost'
DB_PORT = '5431'
DB_NAME = 'mydatabase'

SHAPEFILE_PATH = 'shape_stp/subdistrict_updated.shp'
TABLE_NAME = 'stp_stp_subdis'

REQUIRED_COLUMNS = ['state_code', 'state_name', 'dist_code', 'dist_name', 'subdis_nam', 'subdis_cod', 'geometry']

def convert_geometry(geom):
    """
    Convert geometry to WKTElement while preserving original type.
    Only fixes invalid geometries if needed.
    """
    if geom is None:
        return None
    
    try:
        # Fix any self-intersections or invalid geometries
        if not geom.is_valid:
            geom = geom.buffer(0)
            
        return WKTElement(geom.wkt, srid=4326)
    except Exception as e:
        print(f"Error converting geometry: {str(e)}")
        return None

def load_shapefile_to_db():
    try:
        # Read shapefile using GeoPandas
        gdf = gpd.read_file(SHAPEFILE_PATH)
        
        # Check if all required columns exist
        missing_columns = set(REQUIRED_COLUMNS) - set(gdf.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Select only required columns
        gdf = gdf[REQUIRED_COLUMNS]

        # Convert geometries with improved error handling
        gdf["geometry"] = gdf["geometry"].apply(convert_geometry)
        
        # Remove rows with failed geometry conversions
        gdf = gdf.dropna(subset=['geometry'])

        # Create database engine
        engine = create_engine(
            f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
            echo=False
        )

        # Store data in the database with generic GEOMETRY type
        gdf.to_sql(
            TABLE_NAME, 
            engine, 
            if_exists='append', 
            index=False,
            dtype={
                "geometry": Geometry("GEOMETRY", srid=4326),  # Using GEOMETRY to accept any type
                "state_code": Integer,
                "dist_code": Integer,
                "subdis_cod": Integer
            }
        )

        print(f"Successfully imported {len(gdf)} records from {SHAPEFILE_PATH} to {TABLE_NAME}.")

    except FileNotFoundError:
        print(f"Error: Shapefile not found at {SHAPEFILE_PATH}")
    except ValueError as ve:
        print(f"Validation error: {ve}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    load_shapefile_to_db()