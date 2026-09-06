# Stabilization compatibility wrapper

The exact historical A4-L3 source tree is preserved unchanged in
`../stabilization_A4L3_historical/`.

The original historical closure function has a wall-clock escape that can
return a partial BFS closure, and the original module's `__main__` block also
has a two-vs-three return-value unpack mismatch. For publication use, run:

```bash
python REPRODUCE/reproduce_stabilization.py --k 6 --output build/stabilization
```

`run_exact_partition_refinement.py` is retained as a backward-compatible
positional-argument shim, but it now delegates to the fail-closed publication
launcher. A time-budget overrun is an error; no partial closure is refined.

Example:

```bash
python REPRODUCE/stabilization_wrapper/run_exact_partition_refinement.py 6
```
