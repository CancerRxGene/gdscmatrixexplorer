#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
!!! Run this program using gdscmatrixexplorer/cli.py !!!
'''

import json
import re
import time

import pandas as pd
import requests
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm
from scripts.db_loader import get_project
from db import engine, Base
from models import Model, Drug, Combination, MatrixResult, WellResult, \
    DoseResponseCurve, SingleAgentWellResult, Project

Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)

def upload_anchor(project_name:str, file:str):
    project = get_project(project_name)
    anchor_data = pd.read_csv(file)




if __name__ == '__main__':
    print("!!! Run this program using gdscmatrixexplorer/cli.py !!!")