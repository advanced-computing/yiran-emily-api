import pandas as pd

infile = "HW4.csv"
outfile = "HW4_1.csv"

df = pd.read_csv(infile)


df["fare_str"] = "$" + df["fare"].astype(int).astype(str)

# ====== 3) 部分数据加空格（例如每 10 行加一次）======
mask = df.index % 10 == 0
df.loc[mask, "fare_str"] = " " + df.loc[mask, "fare_str"] + " "

# ====== 4) 写出 ======
df.to_csv(outfile, index=False)

print("Wrote:", outfile)
print(df[["fare", "fare_str"]].head(15))