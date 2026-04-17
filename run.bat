import os
import subprocess

os.chdir(os.path.join(os.path.dirname(__file__), "rt_dashboard"))
subprocess.run(["python", "-m", "uvicorn", "server:app", "--reload"])
