import numpy as np

import pyperclip

### taper setup

import skrf as rf
from skrf.media import MLine

freq = rf.Frequency(20, 100000, unit='MHz', npoints=10000)
w1 = 20*rf.mil  # conductor width [m]
w2 = 90*rf.mil  # conductor width [m]
h = 20*rf.mil  # dielectric thickness [m]
t = 0.7*rf.mil  # conductor thickness [m]
rho = 1.724138e-8  # Copper resistivity [Ohm.m]
ep_r = 10  # dielectric relative permittivity
rough = 1e-6  # conductor RMS roughtness [m]
taper_length = 200*rf.mil  # [m]

taper_exp = rf.taper.Exponential(med=MLine, param='w', start=w1, stop=w2,
                        length=taper_length, n_sections=50,
                        med_kw={'frequency': freq, 'h': h, 't':t, 'ep_r': ep_r,
                                'rough': rough, 'rho': rho}).network

S = taper_exp.s

S11, S12, S21, S22 = S[:,0,0], S[:,0,1], S[:,1,0], S[:,1,1]

Zin, Zout = 50, 50

freq = taper_exp.frequency.f

###

# ### Manual Test

# Zin, Zout = 50, 50

# freq = [1e6, 2e6]

# S11 = [1+2j, 1-2j]
# S12 = [1-2j, 1+2j]
# S21 = [-1-0.5j, 1]
# S22 = [2, 0]

# ###

def S_param_source(freq, Sxy):
    
    output = ""
    
    for idx in range(len(freq)):
        
        mag, phase = abs(Sxy[idx]), np.angle(Sxy[idx])
        
        output += f"+ ({str(freq[idx])}, {20*np.log10(mag)}, {phase})\n"
        
    return output

OUTPUT = f""".SUBCKT 2_PORT_TEST 1 2
R1N 1 10 {-Zin}
R1P 10 11 {2*Zout}
R2N 2 20 {-Zout}
R2P 20 21 {2*Zout}

*S11 FREQ DB PHASE
E11 11 12 FREQ {{V(10, 0)}}= DB
{S_param_source(freq, S11)}

*S12 FREQ DB PHASE
E12 12 G FREQ {{V(20, 0)}}= DB
{S_param_source(freq, S12)}

*S21 FREQ DB PHASE
E21 21 22 FREQ {{V(10, 0)}}= DB
{S_param_source(freq, S21)}

*S22 FREQ DB PHASE
E22 22 G FREQ {{V(20, 0)}}= DB
{S_param_source(freq, S22)}

.ENDS
"""

print(OUTPUT)

pyperclip.copy(OUTPUT)

### Debug Plotting

import matplotlib.pyplot as plt

plt.loglog(freq, abs(S11))

plt.show()

###