# Lab 08: Loading CPI Data into DuckDB

## Overview

This project implements and compares three methods for loading continuously updated Consumer Price Index (CPI) data into a DuckDB database: `append`, `trunc`, and `incremental`.

The project includes both a simplified version and a full version.

- The simplified version uses two CPI snapshot files, `PCPI24M1.csv` and `PCPI25M2.csv`, to simulate a database update.
- The full version uses `pcpi_vintages.csv`, which contains multiple CPI vintages and allows the code to select the latest available data for a given `pull_date`.

The main goal is to show how different loading methods behave when source data changes over time, including both new observations and revisions to past values.



## Data

### Simplified version

The simplified version uses two prepared CPI snapshot files:

- `PCPI24M1.csv`
- `PCPI25M2.csv`

`PCPI24M1.csv` contains CPI data as available in January 2024.  
`PCPI25M2.csv` contains CPI data as available in February 2025.

These two files are used to simulate a real update process. The second file includes:

- new observations for later dates
- possible revisions to previously released CPI values

### Full version

The full version uses `pcpi_vintages.csv`.

This file contains:

- one date column
- multiple vintage columns such as `PCPI04M1`, `PCPI04M2`, and `PCPI25M2`

Each vintage column represents the CPI values available at a particular release date. For any given `pull_date`, the code identifies the latest vintage available up to that date and returns a standardized dataset with only two columns:

- `date`
- `cpi`



## Methods Implemented

This project compares three methods for loading CPI data into DuckDB:

### 1. Append

The append method inserts rows into the target table without replacing the full existing table.

### 2. Trunc

The trunc method removes all rows from the target table and then reloads the complete latest dataset.

### 3. Incremental

The incremental method inserts only new rows and updates only rows whose values have changed.

---

## Database Tables

The project creates three separate DuckDB tables so that the results of each loading method can be compared directly:

- `cpi_append`
- `cpi_trunc`
- `cpi_inc`

In this project:

- the simplified version uses `lab8.duckdb`
- the full version uses `lab8_full.duckdb`



## How to Run

Run the project from the `lab_08` directory after confirming that the required data files are in the `data/` folder.

### Requirements

Install the required packages:

`pip install duckdb pandas`

### Simplified version

The simplified version uses:

- `lab8_utils.py`
- `simulation.ipynb`
- `lab8.duckdb`

Open and run:

- `simulation.ipynb`

This notebook initializes the database using `PCPI24M1.csv`, updates it with `PCPI25M2.csv`, and compares the three loading methods.

### Full version

The full version uses:

- `lab8_full_utils.py`
- `simulation_full.ipynb`
- `lab8_full.duckdb`

Open and run:

- `simulation_full.ipynb`

This notebook reads `pcpi_vintages.csv`, selects the latest available data for each `pull_date`, and loads it into DuckDB using append, trunc, and incremental methods.



## Manual Testing Instructions

### Simplified version

#### 1. Initialize the database

Run the notebook cells that create the initial tables from `PCPI24M1.csv`.

Expected result:

- `cpi_append`, `cpi_trunc`, and `cpi_inc` are created
- all three tables initially contain the same CPI values

#### 2. Load the updated file

Run the notebook cells that load `PCPI25M2.csv` into the database using each method.

Expected result:

- `cpi_append` adds new rows based on append logic
- `cpi_trunc` is cleared and replaced with the newest full snapshot
- `cpi_inc` updates changed rows and inserts new rows

#### 3. Inspect the tables

Check the output tables after each method runs.

Expected result:

- the three tables show different update behavior
- revised values appear correctly in `cpi_trunc` and `cpi_inc`
- `cpi_append` preserves previously loaded records

### Full version

#### 1. Test `get_latest_data(pull_date)`

Call the function with a selected pull date.

Example:

`get_latest_data("2004-01-15")`

Expected result:

- the function selects the latest vintage available up to that date
- the output contains only two columns:
  - `date`
  - `cpi`

#### 2. Test each loading function

Run each loading method separately:

`load_append("2004-01-15")`  
`load_trunc("2004-01-15")`  
`load_incremental("2004-01-15")`

Expected result:

- `cpi_append` receives rows based on append logic
- `cpi_trunc` is cleared and reloaded with the newest full dataset
- `cpi_inc` inserts new rows and updates changed values

#### 3. Inspect the tables

Use the helper function:

`show_table("cpi_append")`  
`show_table("cpi_trunc")`  
`show_table("cpi_inc")`

Expected result:

- the three tables exist
- the table contents reflect the intended loading behavior

#### 4. Simulate repeated runs

Loop over a sequence of pull dates and rerun the loading process.

Expected result:

- append preserves loaded history according to append behavior
- trunc always shows the newest full snapshot
- incremental maintains one up-to-date record per CPI date



## What the User Should Expect to See

After running the notebooks, the user should expect different results in the three tables because each loading strategy behaves differently.

### `cpi_append`

The user should expect to see:

- rows inserted according to append logic
- previously loaded records preserved
- possible multiple stored versions of the same CPI date across different runs

### `cpi_trunc`

The user should expect to see:

- only one current full snapshot of the CPI dataset
- no outdated rows remaining after reload
- a table that reflects the latest available full data

### `cpi_inc`

The user should expect to see:

- one final row per CPI date
- newly added dates inserted into the table
- revised CPI values updated in place



## Discussion of Method Differences

The three methods differ in both behavior and practical use.

**Append** is the simplest approach. It preserves loading history, but it does not automatically represent the latest clean current-state table.

**Trunc** is the most direct way to maintain a fully current table. It removes all existing rows and reloads the latest full dataset. This makes it easy to understand and reliable, but it can be less efficient because it rewrites the entire table each time.

**Incremental** updates only changed rows and inserts only new rows. This is often more efficient than a full reload, but it requires more careful logic when revisions occur.

In short:

- append preserves history
- trunc keeps a clean full snapshot
- incremental balances efficiency and accuracy



## Summary

This lab demonstrates how to maintain CPI data in a DuckDB database when the source data changes over time.

The simplified version uses two prepared CPI snapshots to simulate an update. The full version uses a vintage-based CPI file and retrieves the latest available data for a given `pull_date`.

By comparing append, trunc, and incremental methods, this project shows the tradeoff between simplicity, consistency, and efficiency in data loading workflows.