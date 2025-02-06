import os
import subprocess

# Set the directory containing Python scripts (change '.' to a specific path if needed)
directory = "."

# Get a list of all Python files in the directory
python_files = [f for f in os.listdir(directory) if f.endswith(".py") and f != __file__]

# Execute each Python script
for script in python_files:
    script_path = os.path.join(directory, script)
    print(f"\nRunning: {script_path}")
    result = subprocess.run(["python", script_path], capture_output=True, text=True)
    
    # Print script output
    print(result.stdout)
    print(result.stderr)
