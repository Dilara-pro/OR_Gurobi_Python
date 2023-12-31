# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 10:40:37 2023

@author: Huawei
"""

import gurobipy as gp
from gurobipy import GRB
import pandas as pd
import numpy as np
import os
import re

# dosya isimlerini tanimlayalim

directory = 'C:\\Users\\Huawei\\.spyder-py3\\model_girdileri'  

filename = 'orman_veri.csv'
file_path = os.path.join(directory, filename)
orman_df = pd.read_csv(file_path)

# Sabit verilerin tanımlanması
analiz_alan_seti = list(set(orman_df["Analiz Alani"].tolist())) # ['Pencils', 'Pens'] # ürün seti listesi
receteler_seti =list(set(orman_df["Recete"].tolist())) # arz eden şehirler


orman_multidict = {}
analiz_alan_dict ={}
for i in range(len(orman_df)):
    row = orman_df.loc[i, :]
    orman_multidict[int(row["Analiz Alani"]), int(row["Recete"])] = [row["Net Deger"], row["Kereste"], row["Otlatma"], row["Yaban Endeksi"]]
    analiz_alan_dict[int(row["Analiz Alani"])] = row["Donum"]
    
tahsis_ikilisi_dict, net_deger_dict, kereste_dict, otlatma_dict, yaban_endeksi_dict  = gp.multidict(orman_multidict)

#net_deger_dict[(5,2)] = 200
# Modeli yaratalım
model = gp.Model('orman_tahsis')

# Değişkenleri modele ekleyelim
x_ij = model.addVars(
    tahsis_ikilisi_dict,
    vtype=GRB.CONTINUOUS,
    name="x_ij",
    )

# amac fonksiyonunu ekleyelim
# Amaç fonksiyonu, analiz alanlarının reçetelere tahsis edilmesiyle elde edilecek net değeri maksimize eder.
model.setObjective(x_ij.prod(net_deger_dict))

# kisitlari ekleyelim
# kisit  2 - arazi alanı tahsisi
# bir analiz alanının reçetelere tahsis edilen toplam analının analiz alanın büyüklüğüne eşit olacağını belirtir.
for i in analiz_alan_seti: 
    print(i)
    model.addConstr((x_ij.sum(i, "*") == analiz_alan_dict[i]), "alan_tahsis_kisiti")
                 
                 
# kisit  3 - kereste gereksinimi
model.addConstr((x_ij.prod(kereste_dict) >= 40000), "kereste_kisiti")
          

# kisit  4 - otlatma gereksinimi
model.addConstr((x_ij.prod(otlatma_dict) >= 5), "otlatma_kisiti")
          

# kisit  5 - ortalama yaban endeksi
model.addConstr(((1/788) * x_ij.prod(yaban_endeksi_dict) >= 70), "yaban_endeksi_kisiti")
          
# modeli acik olarak bir lp dosyasi olarak yazdirip, kisitlari kontrol edebilirsiniz
model.update()
model.write("model_kontrol.lp")


# Compute optimal solution
model.ModelSense = -1  # default gurobi minimizasyon yapar, bu parametreyi -1 tanimlayarak amac fonksiyonunu maksimizasyona cevirebiliriz.

model.optimize()
model.write("model_primal_hand.mps")
model.write("model_primal_hand.lp")
model.write("model_dual_hand.dlp")

# store the decision variables values in the optimal solution into a dataframe
x_ij_results_df = pd.DataFrame(columns=['var_name', 'analiz_alani_id', 'recete_id', 'value', 'basis_status','obj_coef', 'reduced_cost', 'smallest_coef', 'largest_coef' ])
counter = 0
for v in x_ij.values():
    current_var = re.split("\[|,|]", v.varName)[:-1]
    # current_var.append(round(v.X, 4))
    
    current_var.extend([round(v.X, 4),  v.VBasis, round(v.obj, 4), round(v.RC, 4), round(v.SAObjLow, 4), round(v.SAObjUp, 4)])
    x_ij_results_df.loc[counter] = current_var
    counter = counter + 1

print(x_ij_results_df)

constraints_results_df = pd.DataFrame(columns=['constraint_name', 'basis_status','slack', 'pi', 'RHS', 'SARHSLow', 'SARHSUp' ])

counter = 0
for c in model.getConstrs():
    constraints_results_df.loc[counter] = [c.ConstrName, c.CBasis, c.Slack, c.Pi, c.RHS, c.SARHSLow, c.SARHSUp ]
    counter = counter + 1
    
print(constraints_results_df)