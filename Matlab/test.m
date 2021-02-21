% Test Script for sdpprotein.
Node = 'test';
Data = [1 2 1 2; 1 3 1 2; 2 3 1 2]; 

[X, Xo, info] = spdprotein(Data);

disp(Xo)

disp(info)
