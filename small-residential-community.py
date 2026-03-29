import opendssdirect as dss
import pandas as pd

def print_status(label):
    print(f"\n{'='*40}")
    print(f">>> {label}")
    print(f"{'='*40}")
    
    # 1. Total System Power (Substation)
    dss.Circuit.SetActiveElement("Line.primary")
    p_all = dss.CktElement.Powers()
    p_total = p_all[0] + p_all[2] + p_all[4]
    print(f" [Substation] Total Power Out: {abs(p_total):.2f} kW")
    
    # 2. Individual House Usage
    print(" [Neighborhood] Individual House Usage:")
    for i in range(1, 6):
        dss.Circuit.SetActiveElement(f"Load.house{i}")
        p_house = dss.CktElement.Powers()
        # Single phase loads return [kW, kVAR]
        print(f"   - House {i}: {abs(p_house[0]):.2f} kW")

    # 3. Heat Losses
    loss_total = dss.Circuit.Losses()[0] / 1000
    print(f" [Losses] Wasted as heat in wires: {loss_total:.2f} kW")

# --- Setup ---
dss.Text.Command("Clear")
dss.Text.Command("new circuit.community basekv=12.47 phases=3 bus1=SourceBus")

# Primary Line (High Voltage)
dss.Text.Command("new line.primary phases=3 bus1=SourceBus bus2=MainBus length=2 units=km r1=0.18 x1=0.41")

# Transformer (Step down 12.47kV to 0.24kV L-L / 0.139kV L-N)
dss.Text.Commands("""
    new transformer.sub_trans phases=3 windings=2 
    buses=[MainBus, HouseBus] kvs=[12.47, 0.24] kvas=[100, 100] xhl=8
""")

# --- FIX 1: Realistic Secondary Line Impedance ---
# Reduced r1 and x1 to per-foot values typical for aluminum conductor
dss.Text.Command("new line.secondary phases=3 bus1=HouseBus bus2=StreetPole length=500 units=ft r1=0.00048 x1=0.00008")

# House Loop
for i in range(1, 6):
    phase = (i % 3) + 1 
    # --- FIX 2: Realistic Service Line Impedance ---
    dss.Text.Command(f"new line.service{i} phases=1 bus1=StreetPole.{phase} bus2=HouseNode{i}.1 length=100 units=ft r1=0.0004 x1=0.00008")
    
    # --- FIX 3: Correct Voltage Rating (L-N) ---
    # Since we connect to a single phase (.1), we use 0.139 kV (240 / sqrt(3))
    dss.Text.Command(f"new load.house{i} bus1=HouseNode{i}.1 phases=1 kv=0.139 kw=5 pf=0.95")

# --- Voltage Bases ---
dss.Text.Command("Set Voltagebases=[12.47, 0.24]")
dss.Text.Command("CalcVoltageBases")

# --- Run Scenarios ---
dss.Solution.Solve()
print_status("BASE CASE (Houses Only)")

# Add Datacenter
dss.Text.Command("new load.datacenter bus1=MainBus phases=3 kv=12.47 kw=1000 pf=0.90")
dss.Solution.Solve()
print_status("IMPACT CASE (Houses + Datacenter)")