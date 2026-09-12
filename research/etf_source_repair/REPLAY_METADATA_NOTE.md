# Commit-scoped metadata is not a new measurement result

Main run `34677769594` failed after the corrected-action directory was added. The old measurement runner writes `data_path_inventory.json` from `git ls-tree HEAD data`. Its whole-repository path count necessarily changes as files are added, even when all measurement inputs and output values are unchanged. That failure and its artifact `10292704038` remain retained; no reference inventory is overwritten.

`verify_legacy_inventory.py` independently reconstructs BOTH path inventories from the immutable code commits in their respective receipts. It reports each added and removed path and fails if either inventory disagrees with its own Git tree. It does not simply exempt the changed file from checking. All discrete scientific statistics and flags remain exact; only the same sixteen previously permitted quantile columns retain the existing absolute `1e-10` bound. No tolerance was expanded and no scientific runner was changed.

The source-impact audit's 125-file baseline registry includes the operational measurement workflow. Its numerical input code/data remain current-byte exact. Because this one workflow must evolve for the metadata fix, retained verification checks that exact historical workflow through its pinned baseline Git object and reports the current workflow's distinct digest. This exception applies to that ONE named operational file, not to price, signal, action, measurement code, freezes or decisive results.

The immutable original raw impact audit still reconstructs all original masks and source checks. Its complete rerun must use a separate detached checkout of decisive commit `7b66fa290ddeea363323bcb89fdc15f12a896384`, with baseline `ef18bf905e9e427153650d5538a996249bb6a901` available, and a fresh output directory. Do not run the old all-current-file guard in a later working tree and claim changed operational files are identical. Current main's routine `verify_retained.py` is the supported read-only regression command.

These changes fix historical-vs-current repository metadata handling, not the research outcome or the outstanding source-qualification gaps.
