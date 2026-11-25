"""
Requires: pandas, statsmodels, sqlalchemy, psycopg2-binary, matplotlib
Run:      python finalProject.py
"""

from sqlalchemy import create_engine, text
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")   # save the chart to a file instead of opening a window
