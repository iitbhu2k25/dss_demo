import os
import re
import glob
import tempfile
import subprocess
import rasterio
from sqlalchemy import create_engine, text
import numpy as np

# Database connection details
DB_USER = 'myuser'
DB_PASSWORD = 'mypassword'
DB_HOST = 'localhost'
DB_PORT = '5431'
DB_NAME = 'mydatabase'

# Raster files directory and table name
RASTER_DIR = 'raster_visual/raster_groundwater/'
TABLE_NAME = 'visuall_raster_visual'  # Adjust to your actual table name

def extract_year_and_phase(filename):
    """
    Extract the year and phase (post/pre) from the filename
    Assumes the filename contains a 4-digit year (e.g. post_2011.tif)
    """
    basename = os.path.basename(filename)
    year_match = re.search(r'(19|20)\d{2}', basename)
    
    # Extract pre/post phase indicator
    phase = 'pre' if 'pre' in basename.lower() else 'post'
    
    if year_match:
        return int(year_match.group(0)), phase
    else:
        raise ValueError(f"Could not extract year from filename: {filename}")

def create_raster_table(engine):
    """Create the raster table if it doesn't exist"""
    sql = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id SERIAL PRIMARY KEY,
        name TEXT,
        year INTEGER,
        phase VARCHAR(10),
        resolution FLOAT,
        rast raster,
        UNIQUE(year, phase)
    );
    """
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{TABLE_NAME}_year ON {TABLE_NAME} (year);"))

def load_raster_using_raster2pgsql(raster_file, year, phase, resolution, engine):
    """
    Load a raster file using the raster2pgsql command-line utility,
    which is more reliable than ST_FromGDALRaster for some formats
    """
    # Create a name for the raster
    name = f"Groundwater"
    
    # Create a temporary SQL file
    with tempfile.NamedTemporaryFile(suffix='.sql', delete=False) as temp_file:
        temp_sql_path = temp_file.name
    
    try:
        # Use raster2pgsql to convert the raster to SQL
        raster2pgsql_cmd = [
            'raster2pgsql',
            '-s', '4326',  # SRID
            '-I',          # Create spatial index
            '-C',          # Apply raster constraints
            '-M',          # Vacuum analyze
            '-t', '100x100',  # Tile size
            raster_file,   # Input raster
            'temp_rast'    # Temporary table name
        ]
        
        # Run raster2pgsql and capture output to temp file
        with open(temp_sql_path, 'w') as f:
            subprocess.run(raster2pgsql_cmd, stdout=f, check=True)
        
        # Read the SQL file content
        with open(temp_sql_path, 'r') as f:
            sql_content = f.read()
        
        # First, create a temporary table to hold the raster
        with engine.connect() as conn:
            # Create temporary table
            conn.execute(text("DROP TABLE IF EXISTS temp_rast;"))
            
            # Execute the SQL to load the raster into temp table
            for sql_statement in sql_content.split(';'):
                if sql_statement.strip():
                    conn.execute(text(sql_statement))
            
            # Check if this raster already exists in database
            check_sql = f"SELECT id FROM {TABLE_NAME} WHERE year = {year} AND phase = '{phase}'"
            result = conn.execute(text(check_sql)).fetchone()
            
            if result:
                print(f"Raster for year {year} ({phase}) already exists in database. Skipping.")
                conn.execute(text("DROP TABLE IF EXISTS temp_rast;"))
                return False
            
            # Now insert from temp table to our actual table
            insert_sql = f"""
            INSERT INTO {TABLE_NAME} (name, year, phase, resolution, rast)
            SELECT 
                '{name}', 
                {year},
                '{phase}',
                {resolution},
                rast
            FROM temp_rast;
            """
            conn.execute(text(insert_sql))
            
            # Clean up
            conn.execute(text("DROP TABLE IF EXISTS temp_rast;"))
        
        return True
    
    except Exception as e:
        print(f"Error in raster2pgsql process: {str(e)}")
        return False
    
    finally:
        # Remove the temporary SQL file
        if os.path.exists(temp_sql_path):
            os.unlink(temp_sql_path)
        
def load_raster_to_db():
    try:
        # Create database engine
        engine = create_engine(
            f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
            echo=False
        )
        
        # Create the raster table if it doesn't exist
        create_raster_table(engine)
        
        # Get all TIFF files in the directory
        raster_files = glob.glob(os.path.join(RASTER_DIR, "*.tif"))
        
        if not raster_files:
            print(f"No TIFF files found in {RASTER_DIR}")
            return
            
        # Process each file
        for raster_file in sorted(raster_files):
            try:
                # Extract year and phase type from filename
                year, phase = extract_year_and_phase(raster_file)
                
                # Get raster metadata
                with rasterio.open(raster_file) as src:
                    # Get resolution (pixel size in map units)
                    resolution = src.res[0]  # X resolution
                
                # Use the more reliable method with raster2pgsql
                success = load_raster_using_raster2pgsql(raster_file, year, phase, resolution, engine)
                
                if success:
                    print(f"Successfully imported {raster_file} for year {year} ({phase})")
                
            except ValueError as ve:
                print(f"Error with {raster_file}: {ve}")
            except Exception as e:
                print(f"Unexpected error processing {raster_file}: {str(e)}")
                
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    load_raster_to_db()