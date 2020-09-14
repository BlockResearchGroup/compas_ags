conda env remove -n ags
conda create -n ags python=3.7 conda-pack cython -y
conda activate ags
REM pip install compas==0.15.6
pip install git+https://github.com/compas-dev/compas.git#egg=compas
pip install .
python scripts/pack.py
