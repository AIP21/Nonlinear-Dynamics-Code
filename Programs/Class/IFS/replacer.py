import json
import os
import random

runDir = os.path.dirname(os.path.realpath(__file__))

path = runDir + "/Systems"

# Open every file in this path
for filename in os.listdir(path):
    lines = []
    
    with open(runDir + "/INPUT.txt", "r") as f:
        lines = f.readlines()
    
    for line in lines:
        line.replace