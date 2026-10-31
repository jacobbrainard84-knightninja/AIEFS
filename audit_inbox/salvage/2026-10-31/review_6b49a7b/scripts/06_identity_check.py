#!/usr/bin/env python3
"""Shows that the 'exact decomposition' e = T1 + T2 used in the new zips/PDFs is an
algebraic identity (true for ANY complex numbers), so checking it to 1e-12 confirms wiring,
not a physical mechanism. Random complex inputs, no AIEF data needed."""
import numpy as np, json, os
rng=np.random.default_rng(0); worst=0.0
for _ in range(200000):
    Ca,Cb,Za,Zb=(rng.normal(size=4)+1j*rng.normal(size=4))*rng.uniform(0.01,10)
    Cbar=(Ca+Cb)/2; Zbar=(Za+Zb)/2; dC=Ca-Cb; dZ=Za-Zb
    T1=2*np.real(np.conj(Cbar)*(dZ-dC)); T2=2*np.real(np.conj(dC)*Zbar)
    e=2*(np.real(np.conj(Ca)*Za)-np.real(np.conj(Cb)*Zb))-(abs(Ca)**2-abs(Cb)**2)
    worst=max(worst,abs(e-(T1+T2))/(1+abs(e)))
out={"random_trials":200000,"worst_relative_error":worst,
     "conclusion":"e == T1+T2 holds for arbitrary complex inputs (algebra), so it is not evidence of AIEF dynamics."}
os.makedirs("results",exist_ok=True); json.dump(out,open("results/identity_check.json","w"),indent=1); print(out)
