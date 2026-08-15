# cko-fcp

`cko-fcp` is the independently versioned, standard-library-only distribution of
the CKO Federated Catalog Protocol foundation authorized by P-018-01 and
ADR-007.

- Distribution: `cko-fcp`
- Import namespace: `cko_fcp`
- Distribution version: `0.1.0`
- Protocol compatibility version: negotiated independently through
  `cko_fcp.FCPVersion`
- Runtime dependencies: none

Install the distribution and import its canonical namespace:

```console
python -m pip install cko-fcp
```

```python
import cko_fcp
```

This package does not depend on or extend `cko`, `cko.core`, or the protected
CKO SDK public API. It contains no P-018-02 authority, publication, query, I/O,
network, database, or credential functionality.
