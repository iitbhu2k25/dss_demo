import subprocess
import sys
import os

def run_scripts_in_sequence(script_list):
    """
    Run Python scripts in sequence
    Args:
        script_list: List of Python script filenames to run
    """
    for script in script_list:
        if not os.path.exists(script):
            print(f"Error: Script {script} not found")
            continue
            
        print(f"\nExecuting: {script}")
        try:
            # Run the script using Python interpreter
            result = subprocess.run([sys.executable, script], capture_output=True, text=True)
            
            # Print output
            if result.stdout:
                print("Output:")
                print(result.stdout)
                
            # Print errors if any
            if result.stderr:
                print("Errors:")
                print(result.stderr)
                
            if result.returncode != 0:
                print(f"Script {script} failed with return code {result.returncode}")
                
        except Exception as e:
            print(f"Error executing {script}: {str(e)}")

# Example usage
if __name__ == "__main__":
    # List your scripts in the order you want them to run
    scripts_to_run = [
        "state.py",
        "districts.py",
        "subdistricts.py",
        "villages.py",
        'shape_postgis.py',
    ]
    
    run_scripts_in_sequence(scripts_to_run)