# C07-D7C reproducibility package

Run from the package root:

```powershell
python .\work\c07d7\c07d7c_partition_census.py
python .\work\c07d7\c07d7c_partition_verify.py
```

The commands reproduce the 150-state absorption-partition census and its
independent logical/identity audit. They require the included frozen D7B
satellite results as input.

No external Python package is required. The package retains the D6/D7
scripts and results that supply the witness and frozen atomic semantics.
