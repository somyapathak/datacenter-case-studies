import opendssdirect as dss
import pandas as pd

# 1. Setup
dss.Text.Command("Clear")
dss.Text.Command("new circuit.community basekv=12.47 phases=3 bus1=SourceBus")

# 2. Primary Line (2km Street Line)
dss.Text.Command("new line.primary phases=3 bus1=SourceBus bus2=MainBus length=2 units=km r1=0.18 x1=0.41")

# 3. Transformer (Steps down to 0.24kV)
dss.run_command("""
    new transformer.sub_trans phases=3 windings=2 
    buses=[MainBus, HouseBus] kvs=[12.47, 0.24] kvas= xhl=8
""")

# 4. Secondary Line (500ft of wire from Transformer to the Houses' area)
# We use 'units=ft' and a higher resistance (r1) because these wires are smaller
dss.Text.Command("new line.secondary phases=3 bus1=HouseBus bus2=StreetPole length=500 units=ft r1=0.48 x1=0.08")

# 5. Add Service Drops and Houses
for i in range(1, 6):
    phase = (i % 3) + 1 
    
    # Each house gets its own 'Service Drop' wire (100ft from the pole to the house)
    # This is usually very thin wire, so we use a high resistance (r1=1.2)
    dss.Text.Command(f"new line.service{i} phases=1 bus1=StreetPole.{phase} bus2=HouseNode{i} length=100 units=ft r1=1.2 x1=0.08")
    
    # Plug the house into its specific Node
    dss.Text.Command(f"new load.house{i} bus1=HouseNode{i} phases=1 kv=0.139 kw=5 pf=0.95")

# 6. Define Voltage Bases
dss.Text.Command("Set Voltagebases=[12.47, 0.24]")
dss.Text.Command("CalcVoltageBases")

# --- Scenario 1: Base Case ---
dss.Solution.Solve()
base_voltages = dss.Circuit.AllBusMagPu()

# --- Scenario 2: Add Datacenter (Stays on High Voltage line) ---
dss.Text.Command("new load.datacenter bus1=MainBus phases=3 kv=12.47 kw=1000 pf=0.90")
dss.Solution.Solve()
impact_voltages = dss.Circuit.AllBusMagPu()

# Summary
results = pd.DataFrame({
    "Scenario": ["Residential Only", "With Datacenter"],
    "Voltage (pu)": [max(base_voltages), max(impact_voltages)]
})
print(results)
