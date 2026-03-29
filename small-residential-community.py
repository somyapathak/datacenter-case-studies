import opendssdirect as dss
import pandas as pd

# 1. Setup
dss.Text.Command("Clear")
dss.Text.Command("new circuit.community basekv=12.47 phases=3 bus1=SourceBus")

# 2. The Primary Line (The "Street" Line)
dss.Text.Command("new line.line1 phases=3 bus1=SourceBus bus2=MainBus length=2 units=km r1=0.18 x1=0.41")

# 3. THE HIERARCHY: Add a Transformer
# This steps 12.47kV down to 0.24kV (240V) for the houses
dss.Text.Command("""
    new transformer.reg_transformer 
    phases=3 
    windings=2 
    buses=[MainBus, HouseBus] 
    conns=[delta, wye] 
    kvs=[12.47, 0.24] 
    kvas=[100, 100] 
    xhl=8
""")

# 4. Add 5 Houses to the LOW VOLTAGE bus (HouseBus)
for i in range(1, 6):
    phase = (i % 3) + 1 
    # Note: kv is now 0.139 (which is 0.24 / sqrt(3) for a single phase)
    dss.Text.Command(f"new load.house{i} bus1=HouseBus.{phase} phases=1 kv=0.139 kw=5 pf=0.95")

# 5. Define Voltage Bases for BOTH levels
dss.Text.Command("Set Voltagebases=[12.47, 0.24]")
dss.Text.Command("CalcVoltageBases")

# --- SCENARIO 1: Base Case ---
dss.Solution.Solve()
base_voltages = dss.Circuit.AllBusMagPu()
print(f"Base Case Max Voltage: {max(base_voltages):.4f} pu")

# --- SCENARIO 2: Add Datacenter (Stays on the high-voltage MainBus) ---
dss.Text.Command("new load.datacenter bus1=MainBus phases=3 kv=12.47 kw=1000 pf=0.90")
dss.Solution.Solve()
impact_voltages = dss.Circuit.AllBusMagPu()
print(f"Impact Case Max Voltage: {max(impact_voltages):.4f} pu")

# 6. Summary
results = pd.DataFrame({
    "Scenario": ["Residential Only", "With Datacenter"],
    "Voltage (pu)": [max(base_voltages), max(impact_voltages)]
})
print("\n--- Summary ---")
print(results)
