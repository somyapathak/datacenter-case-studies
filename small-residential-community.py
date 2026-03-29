import opendssdirect as dss
import pandas as pd

# 1. Setup
dss.Text.Command("Clear")
dss.Text.Command("new circuit.community basekv=12.47 phases=3 bus1=SourceBus")

# 2. Primary Line
dss.Text.Command("new line.primary phases=3 bus1=SourceBus bus2=MainBus length=2 units=km r1=0.18 x1=0.41")

# 3. Transformer (Using the new 'Commands' to avoid the warning)
dss.Text.Commands("""
    new transformer.sub_trans phases=3 windings=2 
    buses=[MainBus, HouseBus] kvs=[12.47, 0.24] kvas=[100, 100] xhl=8
""")

# 4. Secondary Line (Street Wire)
dss.Text.Command("new line.secondary phases=3 bus1=HouseBus bus2=StreetPole length=500 units=ft r1=0.48 x1=0.08")

# 5. Service Drops and Houses
for i in range(1, 6):
    phase = (i % 3) + 1 
    dss.Text.Command(f"new line.service{i} phases=1 bus1=StreetPole.{phase} bus2=HouseNode{i} length=100 units=ft r1=1.2 x1=0.08")
    dss.Text.Command(f"new load.house{i} bus1=HouseNode{i} phases=1 kv=0.139 kw=5 pf=0.95")

dss.Text.Command("Set Voltagebases=[12.47, 0.24]")
dss.Text.Command("CalcVoltageBases")

# --- Scenario 1: Base Case ---
dss.Solution.Solve()
# This "filter" skips the 0.0 ground wires and only looks at the 120V/240V wires
base_voltages = [v for v in dss.Circuit.AllBusMagPu() if v > 0.1]
base_min = min(base_voltages)

# --- Scenario 2: Add Datacenter ---
dss.Text.Command("new load.datacenter bus1=MainBus phases=3 kv=12.47 kw=1000 pf=0.90")
dss.Solution.Solve()
impact_voltages = [v for v in dss.Circuit.AllBusMagPu() if v > 0.1]
impact_min = min(impact_voltages)

# --- Final Summary ---
results = pd.DataFrame({
    "Scenario": ["Residential Only", "With Datacenter"],
    "House Voltage (pu)": [base_min, impact_min]
})

print("\n--- Final Neighborhood Impact Report ---")
print(results.to_string(index=False))

