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

def upload_anchor(anchor_combi_path: str, anchor_synergy_path: str, project_name: str):
    anchor_combi = pd.read_csv(anchor_combi_path)

    anchor_synergy =  pd.read_csv(anchor_synergy_path)

    print(project_name)
    # project = get_project(project_name)
    # print(project)

   # add_new_models(anchor_result)
   #  models = pd.read_sql(session.query(Model).statement, session.bind)
   #  print(models)
   # add_new_drugs(anchor_result)

    # project = get_project(project_name)
    # anchor_data = pd.read_csv(file)




if __name__ == '__main__':
    print("!!! Run this program using gdscmatrixexplorer/cli.py !!!")