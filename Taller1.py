# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 20:47:08 2021

@author: MARIO ALBERTO
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import flopy


#parametros iniciales
name = "tutorial01_mf6"
h1 = 100
h2 = 90
Nlay = 10
N = 101
L = 400.0
H = 50.0
k = 1.0



#Busca mf6 en la carpeta especificada y guarda los archivos
sim = flopy.mf6.MFSimulation(
    sim_name=name, exe_name="mf6",
    version="mf6", sim_ws="Workspace"
) 

#Crea objetos de flopy TDIS
tdis = flopy.mf6.ModflowTdis(
    sim, pname="tdis", time_units="DAYS", nper=1, perioddata=[(1.0, 1, 1.0)]
)


#Crea el paquete de objetos de flopy IMS
ims = flopy.mf6.ModflowIms(sim, pname="ims", complexity="SIMPLE")

#Crea el modelo de flujo de agua 
model_nam_file = "{}.nam".format(name)
gwf = flopy.mf6.ModflowGwf(sim, modelname=name, model_nam_file=model_nam_file)

bot = np.linspace(-H / Nlay, -H, Nlay)#La altura va desde -H/#de celdas hasta el fondo total, en el número de capa que tenemos (Nlay)
delrow = delcol = L / (N - 1) #Espesor de filas
dis = flopy.mf6.ModflowGwfdis( #Paquete de discretización
    gwf,
    nlay=Nlay,
    nrow=N,
    ncol=N,
    delr=delrow,
    delc=delcol,
    top=0.0,
    botm=bot,
)

#Crea las condiciones iniciales
start = h1 * np.ones((Nlay, N, N))
ic = flopy.mf6.ModflowGwfic(gwf, pname="ic", strt=start)


#Controla el flujo entre celdas
#k=np.ones([10,N,N])                      #PONE LA PERMEABILIDAD COMO UNA MATRIZ
#k[1,:,:]=5e-3                            #LE ASIGNA UN VALOR DE K A UNA CAPA
npf = flopy.mf6.ModflowGwfnpf(gwf, icelltype=1, k=k, save_flows=True)


#
chd_rec = []
chd_rec.append(((0, int(N / 4), int(N / 4)), h2))
#chd_rec.append(((1, int(3*N / 4), int(3*N / 4)), h2-5)) #AGREGA POZOS
for layer in range(0, Nlay):
    for row_col in range(0, N):
        chd_rec.append(((layer, row_col, 0), h1))
        chd_rec.append(((layer, row_col, N - 1), h1))
        if row_col != 0 and row_col != N - 1:
            chd_rec.append(((layer, 0, row_col), h1))
            chd_rec.append(((layer, N - 1, row_col), h1))
chd = flopy.mf6.ModflowGwfchd(
    gwf,
    maxbound=len(chd_rec),
    stress_period_data=chd_rec,
    save_flows=True,
)

iper = 0
ra = chd.stress_period_data.get_data(key=iper)
ra

#Create the output control ('OC') Package
headfile = "{}.hds".format(name)
head_filerecord = [headfile]
budgetfile = "{}.cbb".format(name)
budget_filerecord = [budgetfile]
saverecord = [("HEAD", "ALL"), ("BUDGET", "ALL")]
printrecord = [("HEAD", "LAST")]
oc = flopy.mf6.ModflowGwfoc(
    gwf,
    saverecord=saverecord,
    head_filerecord=head_filerecord,
    budget_filerecord=budget_filerecord,
    printrecord=printrecord,
)


#Construye los .txt
sim.write_simulation()


#COndición de éxito
success, buff = sim.run_simulation()
if not success:
    raise Exception("MODFLOW 6 did not terminate normally.")
    
    
    #Plot a Map of Layer 1
headfile= 'WorkSpace' +'/'+headfile #Esto se lo agrego
hds = flopy.utils.binaryfile.HeadFile(headfile)
h = hds.get_data(kstpkper=(0, 0))
x = y = np.linspace(0, L, N)
y = y[::-1]
fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(1, 1, 1, aspect="equal")
c = ax.contour(x, y, h[0], np.arange(90, 100.1, 0.2), colors="blue")
plt.clabel(c, fmt="%2.1f")

#Plot a Map of Layer 10
x = y = np.linspace(0, L, N)
y = y[::-1]
fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(1, 1, 1, aspect="equal")
c = ax.contour(x, y, h[-1], np.arange(90, 100.1, 0.2), colors="red")
plt.clabel(c, fmt="%1.1f")

#Plot a Cross-section along row 51
z = np.linspace(-H / Nlay / 2, -H + H / Nlay / 2, Nlay)
fig = plt.figure(figsize=(5, 2.5))
ax = fig.add_subplot(1, 1, 1, aspect="auto")
c = ax.contour(x, z, h[:, 50, :], np.arange(90, 100.1, 0.2), colors="cyan")
plt.clabel(c, fmt="%1.1f")