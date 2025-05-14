import os
import glob
import subprocess

test_files = glob.glob('tests/test_*.py')

for file in test_files:
    print(f"## Running {file}")
    subprocess.run(['python', '-m', 'unittest', file])
