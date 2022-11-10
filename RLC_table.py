import skrf as rf
import numpy as np
import matplotlib.pyplot as plt
from skrf.media import MLine

# Model Parameters
freq = rf.Frequency(0.01, 20, unit='MHz', npoints=1000)
w1 = 20*rf.mil  # conductor width [m]
w2 = 90*rf.mil  # conductor width [m]
h = 20*rf.mil  # dielectric thickness [m]
t = 0.7*rf.mil  # conductor thickness [m]
rho = 1.724138e-8  # Copper resistivity [Ohm.m]
ep_r = 10  # dielectric relative permittivity
rough = 1e-6  # conductor RMS roughtness [m]
taper_length = 200*rf.mil  # [m]

# Media definitions
microstrip_w1 = MLine(freq, w=w1, h=h, t=t, rho=rho, ep_r=ep_r, rough=rough)
microstrip_w2 = MLine(freq, w=w2, h=h, t=t, rho=rho, ep_r=ep_r, rough=rough)

# piece of transmission lines connected to the taper
line1 = microstrip_w1.line(d=50, unit='mil', name='feeder')
line2 = microstrip_w2.line(d=50, unit='mil', name='feeder')

# loading resistor
resistor = microstrip_w2.resistor(R=15)


# S11 = []
# S12 = []
# S21 = []
# S22 = []

# freqs = []

taper_exp = rf.taper.Exponential(med=MLine, param='w', start=w1, stop=w2,
                        length=taper_length, n_sections=50,
                        med_kw={'frequency': freq, 'h': h, 't':t, 'ep_r': ep_r,
                                'rough': rough, 'rho': rho}).network

ntwk_exp = line1 ** taper_exp ** line2 ** resistor ** microstrip_w2.short()

# print(taper_exp.s)

fig, ax = plt.subplots()
# ax.plot(taper_exp.frequency.f_scaled, taper_exp.s[:,0, 0], lw=2, label='scikit-rf - Exponential')
# ax.plot(taper_exp.frequency.f_scaled, taper_exp.s[:,0, 1], lw=2, label='scikit-rf - Exponential')
# ax.plot(taper_exp.frequency.f_scaled, taper_exp.s[:,1, 0], lw=2, label='scikit-rf - Exponential')
# ax.plot(taper_exp.frequency.f_scaled, taper_exp.s[:,1, 1], lw=2, label='scikit-rf - Exponential')

# f_ref, s_mag_ref = np.loadtxt('ANSYS_Circuit_taper_exponential_s_mag.csv', delimiter=',', skiprows=1, unpack=True)
# ax.plot(f_ref, s_mag_ref, label='ANSYS Circuit - Exponential Taper', lw=2, ls='--')

# ax.set_xlabel('f [GHz]')
# # ax.set_ylabel('$|s_{11}|$')
# # ax.set_ylim(0, 0.6)
# # ax.set_xlim(1, 20)
# ax.legend()

# plt.show()

Z = rf.s2z(taper_exp.s)
f = taper_exp.frequency.f #.f_scaled

Z11, Z12, Z21, Z22 = Z[:,0,0],Z[:,0,1],Z[:,1,0],Z[:,1,1]

A, B, C = Z11 - Z12, Z22 - Z12, Z12

# ax.plot(taper_exp.frequency.f_scaled, np.imag(A))

def RLC(Z):
    
    R = np.real(Z)
    LC = np.imag(Z)
    
    L = np.where(LC > 0, LC, 0)
    C = np.where(LC < 0, -1/LC, 0)
    
    return R, L, C

def create_ltspice_table(freqs, values):
    
    values = [str(i) + "," + str(j) for i, j in zip(freqs, values)]
    
    return "table(f, " + ', '.join(values) + ")"

# plt.show()

R,L,C = RLC(A)

print("--- R ---")
print(create_ltspice_table(f, R))

print("\n\n--- L ---")
print(create_ltspice_table(f, L))

print("\n\n--- C ---")
print(create_ltspice_table(f, C))

