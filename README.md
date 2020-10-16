# Protein refinement method.
## Installing

## Executing
  Inside the correct directory, just type on terminal
```bash 
python protein_refine.py 'SET' 'OPT' 
```
This code aims to execute the protein generation and refinment for a SET of proteins (whose locations are stored inside the Nodes folder) and the OPT means alternative commands for the program such as `debug` and turn the statistics off.

Note that, SET can also contain only one protein, which in return will set the process to single mode.

A detaliade example for the SET and OPT strucutre come as follows:

```python
### First Example
python protein_refine.py '2Y2A' 

### Second Example
python protein_refine.py 
```
For the fisrt example, it will exectue the `protein_refine` method in single mode, for the protein 2Y2A. By the other hand, on the second example though, as any argumetn were given for `SET`, the standard response will set it as the node directory informed on the `config.json` file (Wich by standard it's the Node directory). And as a consequence it will proced the tests for all the avaliable proteins currently located on `Nodes`. 

Resumably, it can be loaded as:
```python
# As the protein name wich we want to test;
python protein_refine.py `NAME`

# or, another directory within the protein names (and data*)
python protein_refine.py 'C://...' 

# Also, as the satandard configuration
python protein_refine.py 
```

## Check Tests

## The config.json file and it's properties

## The general process (aka the method)

## Some information reggarding the execution and assimilation betwewn the `C` and `Python` languages.
