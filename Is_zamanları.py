# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 22:44:16 2023

@author: Huawei
"""

import gurobipy as gp
from gurobipy import GRB   
import pandas as pd
import os

# Model is_zamanları

#directory = 'model_girdileri'    HOCAM YİNE OLMADI BU MAALESEF
directory = 'C:\\Users\\Huawei\\.spyder-py3\\model_girdileri'  

filename = 'Is_zaman_allocation.csv'
file_path = os.path.join(directory, filename)
is_zaman_df = pd.read_csv(file_path)    #python liste indeksini 0 ile başlattığı için en üst row 0 eklenerek oluşturulmuştur. 

# Sabitler
min_time = is_zaman_df["min zaman"].tolist()
max_time = is_zaman_df["maks zaman"].tolist()
min_cost = is_zaman_df["min maliyet"].tolist()
max_cost = is_zaman_df["maks maliyet"].tolist()
# Modeli oluştur
model = gp.Model("min_maliyet")

# Karar değişkenleri
x = model.addVars(range(1, 8), vtype=GRB.CONTINUOUS, name="x")
y = model.addVars(range(1, 8), vtype=GRB.CONTINUOUS, name="y")

# Kısıtlar
model.addConstr(x[1] + y[1] <= x[4], "4. iş öncülü")
model.addConstr(x[4] + y[4] <= x[7], "7. iş öncülü")
model.addConstr(x[2] + y[2] <= x[3], "3. iş öncülü")
model.addConstr(x[2] + y[2] <= x[4], "4. iş öncülü 2")
model.addConstr(x[3] + y[3] <= x[5], "5. iş öncülü")
model.addConstr(x[3] + y[3] <= x[6], "6. iş öncülü")


model.addConstr(x[1] + y[1] <= 40, "1. iş en fazla 40 gün")
model.addConstr(x[2] + y[2] <= 40, "2. iş en fazla 40 gün")
model.addConstr(x[3] + y[3] <= 40, "3. iş en fazla 40 gün")
model.addConstr(x[4] + y[4] <= 40, "4. iş en fazla 40 gün")
model.addConstr(x[5] + y[5] <= 40, "5. iş en fazla 40 gün")
model.addConstr(x[6] + y[6] <= 40, "6. iş en fazla 40 gün")
model.addConstr(x[7] + y[7] <= 40, "7. iş en fazla 40 gün")


model.addConstr(y[1] >= 6, "1. iş zaman aralığı alt sınır")
model.addConstr(y[1] <= 12, "1. iş zaman aralığı üst sınır")
model.addConstr(y[2] >= 8, "2. iş zaman aralığı alt sınır")
model.addConstr(y[2] <= 16, "2. iş zaman aralığı üst sınır")
model.addConstr(y[3] >= 16, "3. iş zaman aralığı alt sınır")
model.addConstr(y[3] <= 24, "3. iş zaman aralığı üst sınır")
model.addConstr(y[4] >= 14, "4. iş zaman aralığı alt sınır")
model.addConstr(y[4] <= 20, "4. iş zaman aralığı üst sınır")
model.addConstr(y[5] >= 4, "5. iş zaman aralığı alt sınır")
model.addConstr(y[5] <= 16, "5. iş zaman aralığı üst sınır")
model.addConstr(y[6] >= 12, "6. iş zaman aralığı alt sınır")
model.addConstr(y[6] <= 16, "6. iş zaman aralığı üst sınır")
model.addConstr(y[7] >= 2, "7. iş zaman aralığı alt sınır")
model.addConstr(y[7] <= 12, "7. iş zaman aralığı üst sınır")
model.update()

# Amac fonksiyonu
model.setObjective(
    gp.quicksum(min_cost[i] + (y[i] - min_time[i]) * ((max_cost[i] - min_cost[i]) / (max_time[i] - min_time[i])) for i in range(1, 8)),
    GRB.MINIMIZE
)
# Modeli çöz
model.optimize()

# Çözümü yazdır
if model.Status == GRB.OPTIMAL:
    solution_x = model.getAttr('X', x)
    solution_y = model.getAttr('X', y)
    for i in range(1, 8):
        print('x[%s]: %g' % (i, solution_x[i]))
        print('y[%s]: %g' % (i, solution_y[i]))

print("Toplam Maliyet =", model.objVal)



