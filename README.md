# sunshadeCisseeker-docs

Sphinx documentation sources for
**sunshadeCisseeker** — promoter cis-regulatory element comparison of sun /
facultative / shade plants across nuclear, chloroplast and mitochondrial
genomes.

The documentation is built and hosted on
[Read the Docs](https://readthedocs.org/) from this repository
(`.readthedocs.yaml` at the root, Sphinx sources under `docs/`).

## Build locally

```bash
pip install -r docs/requirements.txt
sphinx-build -b html docs docs/_build/html
# open docs/_build/html/index.html
```

## Layout

```
.readthedocs.yaml      Read the Docs build configuration
docs/conf.py           Sphinx configuration
docs/index.rst         landing page + toctrees
docs/*.rst             user guide / analysis / reference pages
docs/requirements.txt  sphinx + sphinx-rtd-theme
```

## License

MIT — see `LICENSE`.
