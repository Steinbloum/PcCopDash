
import pandas as pd
import numpy as np
import random
import string
from dataclasses import dataclass
import numpy as np
import plotly.express as px
import sqlite3


@dataclass
class FakeDataGenerator:

    components : str = lambda : random.choice(["COMPONENT_" + str(n) for n in range(200)] + ['DIRECT ROUTE']*30)
    names : str = lambda : ''.join(random.choice(string.ascii_letters).upper() for _ in range(4))
    signal_types : str = lambda : random.choice(['GND', 'AGND', 'VSS', 'DVSS', 'IO', 'DATA', 'FOO', 'BAR'])
    pogozones : str = lambda : random.choice(["A", "B", "C", "D", "E", "F", "G"])
    pogocols : str = lambda : "C" + str(random.choice(range(40)))
    pogorows : str = lambda : "R" + str(random.choice(range(25)))
    instruments : str = lambda : "J10" + str(random.choice(range(100,800)))
    slots : str = lambda : "SLOT_" +str(random.choice(range(1,17)))
    slotpins : str = lambda : f"PIN_{random.choice(range(100, 500))}.{random.choice(range(10,100))}"
    channels : str = lambda : "CH" + str(random.choice(range(990)))
    skip_x : int = lambda : random.choice(range(3))
    skip_y : int = lambda : random.choice(range(3))
    dutCount : int = lambda : random.choice([x for x in range(1,38) if x%4==0])
    unique_pc_ids : list = lambda x : random.sample(range(1,999), k = x )
    manufacturers : str = lambda : random.choice(["ShapeMaker", "FolkPalper", "EngineerMess"])
    family : str = lambda : ''.join(random.choice(string.ascii_letters).upper() for _ in range(4)) + str(random.randint(10,20))
    serial : str = lambda : f"{''.join(random.choice(string.ascii_letters).upper() for _ in range(6))}/A.0{random.randint(1,9)}"
    tech : str = lambda : f"T{random.randint(1,30)}.{random.choice(string.ascii_letters).upper()}{random.randint(1,4)}"
    rack : str = lambda : f"{random.randint(1,9)}{random.choice(string.ascii_uppercase)}{random.randint(10,85)}"

    
    def generateBaseDut(self) -> pd.DataFrame:
        # Step 1: Define the Space Size
        x_size = np.random.randint(5000, 9000)
        y_size = np.random.randint(5000, 9000)
        min_distance = 150
        edge_length = min(x_size, y_size)  
        points_per_edge = int((edge_length * 0.8) / min_distance)
        points_per_edge = min(points_per_edge, edge_length // min_distance)


        def generate_edge_points(size, points_count, on_x=True):
            """Generate points located on one edge of the graph.
            
            Args:
                size (int): The size of the edge where points will be generated.
                points_count (int): The number of points to generate.
                on_x (bool): Whether points are generated on the x-axis (True) or y-axis (False).
                
            Returns:
                list of tuples: Generated points (x, y).
            """
            spacing = size / points_count
            points = []
            for i in range(points_count):
                # Calculate point position
                pos = i * spacing + (spacing / 2)  # Centering the point in its allocated space
                if on_x:
                    points.append((pos, 0))  # Points on the bottom edge
                    points.append((pos, y_size))  # Points on the top edge
                else:
                    points.append((0, pos))  # Points on the left edge
                    points.append((x_size, pos))  # Points on the right edge
            return points

        # Generate points for each edge
        bottom_top_points = generate_edge_points(x_size, points_per_edge, on_x=True)
        left_right_points = generate_edge_points(y_size, points_per_edge, on_x=False)
        all_points = bottom_top_points + left_right_points
        df = pd.DataFrame(all_points, columns=['X', 'Y'])

        #populate base dut
        df["name"] = [self.names() for x in range(len(df))]
        df["signal_type"] = [self.signal_types() for x in range(len(df))]
        df["dut"] = 0
        df["pin_number"] = list(range(len(df)))
        return df

    def populatePc(self, baseDut) -> pd.DataFrame:
        dutCount = self.dutCount()
        skip_x = self.skip_x()
        skip_y = self.skip_y()
        step_x = baseDut.X.max()+1000
        step_y = baseDut.Y.max()+1000
        
        def findSquariestLayout(n):
            sqrt_n = int(np.sqrt(n))
            for i in range(sqrt_n, 0, -1):
                if n % i == 0:
                    factor1 = i
                    factor2 = n // i
                    return (factor1, factor2)
        
        duts = [baseDut.copy() for n in range(dutCount)]
        duts_x, duts_y = findSquariestLayout(dutCount)
        row = 0 
        col = 0
        for dut, df in enumerate(duts):#generate duts
            # print(row, col)
            df["dut"] = dut
            delta_x = col*((skip_x+1)*step_x)
            delta_y = row*((skip_y+1)*step_y)
            df["X"] += delta_x
            df["Y"] += delta_y
            if (col%(duts_x-1)==0)&(col>0):
                row +=1
                col = 0
            else:
                col +=1

        df = pd.concat(duts)#concat data

        #populate data
        df["components"] = list(self.components() for _ in range(len(df)))
        df["pogozone"] = list(self.pogozones() for _ in range(len(df)))
        df["pogolocation"] = list(f"{x}_{y}_{z}" 
                                  for x, y, z in zip(df.pogozone, 
                                            [self.pogocols() for _ in range (len(df))], 
                                            [self.pogorows() for _ in range (len(df))]
                                            ))
        instru = [self.instruments() for n in range(20)]
        df["instrument"] = list(random.choice(instru) for _ in range(len(df)))
        df['slot'] = list(self.slots() for _ in range(len(df)))
        df['slotpin'] = list(self.slotpins()for _ in range(len(df)))
        df["channel"] = list(self.channels() for _ in range(len(df)))

        return df
    
    def generateHardware(self, count):
        print(f'Generating {count} Fake Hardware devices')
        #generate fake ids:
        ids = self.unique_pc_ids(count)
        #generate dataframes, link to an id in a dict
        data = {
            id:self.populatePc(self.generateBaseDut()) for id in ids
        }
        print(f"Generated {format(np.sum([len(df) for df in data.values()]), ',')} data points")
        #generate the index
        families = [self.family() for n in range(3)]
        idx = []
        for id in ids:
            idx.append(
                {
                "id" : id,
                "rack" : self.rack(),
                "tip_count" : len(data[id]),
                "dut_count" : data[id].dut.max()+1,
                "family":random.choice(families),
                "manufacturer":self.manufacturers(),
                "serial":self.serial(),
                "tech":self.tech(),
                }
                    )

        idx = pd.DataFrame.from_records(idx)
        print(idx.head())
        return idx, data




fdg = FakeDataGenerator()

idx, data = fdg.generateHardware(200)

#save to db

conn = sqlite3.connect('hw.db')


# Save the index 
idx.to_sql('tbl_idx', conn, if_exists='replace', index=False)

# save the maps
for id, df in data.items():
    df.to_sql(f"tbl_map_{id}", conn, if_exists="replace", index=False)

# Close the connection
conn.close()



