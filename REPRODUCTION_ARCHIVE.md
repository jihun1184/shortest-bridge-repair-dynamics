# Full historical archive distribution

The exact predecessor ZIPs are intentionally not all committed to the Git tree.  In particular, the canonical 02C9 archive is about 144 MB and is better distributed as a GitHub Release asset.

Recommended release asset:

`CGTA_REPRODUCTION_FULL_LINEAGE_ARCHIVES_20260906.zip`

The asset contains the exact original archives listed in `REPRODUCE/provenance/SOURCE_ARCHIVE_SHA256SUMS.txt`.


## Windows-safe public packaging

The recovered generation-code aggregate is preserved in the public repository as
`REPRODUCE/provenance/RECOVERED_GENERATION_CODE_20260906.zip` with SHA-256
`344effe7933eb8a44d3838bbc16e81ec04696be161f60e26268d9b21b6373f21`.
It is not expanded in the public release because the original lineage contains
paths that exceed the limits handled reliably by Windows Explorer.
