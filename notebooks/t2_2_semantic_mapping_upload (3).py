# %% [markdown]
# # T2.2 — Semantic Mapping Upload to DBRepo
# 
# Uploads all semantic mappings from `docs/semantic_mapping.csv` to DBRepo via REST API.
# 
# **Owner:** Person B | **Task:** T2.2 — Semantic Mapping | **Dataset:** Hohe Warte Vienna Weather
# 
# > **Requires:** TU Wien VPN active, and the group database already created in DBRepo (T2.1 complete).

# %% [markdown]
# ## Step 0 — Install the official DBRepo Python library

# %%
import subprocess, sys
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'dbrepo', '--quiet'])
print('dbrepo library ready')

# Verify the exact method signature we will use
from dbrepo.RestClient import RestClient
import inspect
print()
print('update_table_column signature:')
print(inspect.signature(RestClient.update_table_column))
print(inspect.getdoc(RestClient.update_table_column))


# %% [markdown]
# ## Step 1 — Configuration

# %%
import os

ENDPOINT    = "https://test.dbrepo.tuwien.ac.at"
DATABASE_ID = "899bfcba-7fec-40c9-9076-3a3a9372c844"
USERNAME    = "azra1558"
PASSWORD    = "Katalizator1558!"

candidates = [
    "../docs/semantic_mapping.csv",
    "docs/semantic_mapping.csv",
    "semantic_mapping.csv"
]

MAPPING_FILE = next((c for c in candidates if os.path.exists(c)), None)
if MAPPING_FILE is None:
    searched = "\n".join(f"  {os.path.abspath(c)}" for c in candidates)
    raise FileNotFoundError(
        f"semantic_mapping.csv not found. Searched:\n{searched}\n"
        f"Current working directory: {os.getcwd()}"
    )

print(f"Mapping file found: {os.path.abspath(MAPPING_FILE)}")

# %% [markdown]
# ## Step 2 — Connect to DBRepo and fetch database structure
# 
# The API requires **table UUID** and **column UUID** — not names. We fetch them here.

# %%
from dbrepo.RestClient import RestClient

client = RestClient(endpoint=ENDPOINT, username=USERNAME, password=PASSWORD)

db = client.get_database(database_id=DATABASE_ID)
print(f"Connected to database: {db.name}")

tables = db.tables or []
print(f"Tables found: {[t.name for t in tables]}")
if not tables:
    raise RuntimeError("No tables found — check DATABASE_ID or ensure T2.1 is complete")


# %% [markdown]
# ## Step 3 — Build name-to-ID lookup maps

# %%
table_id_map  = {} 
column_id_map = {}

for table in tables:
    table_id_map[table.name] = table.id
    if not table.columns:
        table = client.get_table(database_id=DATABASE_ID, table_id=table.id)
    print(f"  Table '{table.name}' -> {table.id} ({len(table.columns)} columns)")
    for col in table.columns:
        column_id_map[(table.name, col.name)] = col.id

print(f"\nMapped {len(table_id_map)} tables, {len(column_id_map)} columns")
if len(column_id_map) == 0:
    raise RuntimeError("No columns found — cannot upload. Check DBRepo schema.")

print("\nDiscovered columns in DBRepo:")
for k in sorted(column_id_map.keys()):
    print(f"  {k[0]}.{k[1]}")


# %% [markdown]
# ## Step 4 — Load the semantic mapping CSV

# %%
import csv

mappings = []
with open(MAPPING_FILE, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        mappings.append(row)

print(f"Loaded {len(mappings)} mappings from CSV")
for m in mappings[:3]:
    print(m)


# %% [markdown]
# ## Step 5 — Upload each semantic concept using the official dbrepo client
# 
# Uses `client.update_table_column(database_id, table_id, column_id, concept_uri=uri)`.
# 
# > **Note on `ontology_label`:** Only `concept_uri` is sent to DBRepo. The label field in the CSV 
# is for human readability. DBRepo resolves the concept name internally from its own concept 
# store using the URI — no separate label call is needed.

# %%
success, skipped, errors = 0, 0, []

for row in mappings:
    tname = row["table_name"]
    cname = row["column_name"]
    uri   = row["ontology_uri"]

    tid = table_id_map.get(tname)
    cid = column_id_map.get((tname, cname))

    if tid is None or cid is None:
        skipped += 1
        print(f"  SKIP  {tname}.{cname} — not found in DBRepo schema")
        continue

    try:
        client.update_table_column(
            database_id=DATABASE_ID,
            table_id=tid,
            column_id=cid,
            concept_uri=uri
        )
        success += 1
        print(f"  OK    {tname}.{cname} -> {uri}")
    except Exception as e:
        errors.append((tname, cname, str(e)))
        print(f"  FAIL  {tname}.{cname} -> {e}")

print()
print(f"Result: {success} uploaded, {skipped} skipped, {len(errors)} failed")
if errors:
    print("\nFailed rows:")
    for e in errors:
        print(f"  {e[0]}.{e[1]}: {e[2]}")


# %% [markdown]
# ## Step 6 — Verify: read back spot-checks from DBRepo

# %%
spot_checks = [
    ("weather_measurement", "t_mean_c"),
    ("weather_measurement", "precp_sum_mm"),
    ("station",             "nuts_code"),
    ("station",             "latitude_deg"),
    ("time_dimension",      "ref_year"),
]

print("Spot-check verification:")
all_ok = True
for tname, cname in spot_checks:
    tid = table_id_map.get(tname)
    cid = column_id_map.get((tname, cname))
    if tid is None or cid is None:
        print(f"  SKIP  {tname}.{cname} — ID not found")
        continue
    try:
        tbl = client.get_table(database_id=DATABASE_ID, table_id=tid)  # returns Table object
        matched = next((c for c in tbl.columns if c.name == cname), None)
        if matched:
            print(f"  OK    {tname}.{cname}")
            print(f"        concept_uri = {matched.concept_uri}")
            if not matched.concept_uri:
                print(f"        WARNING: concept_uri is empty — upload may have failed")
                all_ok = False
        else:
            print(f"  MISS  {tname}.{cname} — column not in response")
            all_ok = False
    except Exception as e:
        print(f"  FAIL  {tname}.{cname} -> {e}")
        all_ok = False

print()
print("All spot-checks passed" if all_ok else "Some checks failed — review above")


# %%
!pip show dbrepo

# %%



