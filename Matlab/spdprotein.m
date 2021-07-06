function [non_scaled, conformation, info] = spdprotein(Data)
%Sdpprotein2 Solves the Relaxad SPD programm for a given distance list
%   Detailed explanation goes here

% Initiate basic variables:
% m := number of restrictions (|E|)
% n := number of atoms
m = length(Data(:, 1));
n = max([max(Data(:, 1)) max(Data(:, 2))]);
fprintf('# Number of used atoms: %d  Number of know distances: %d ', n, m);

% index list: Atom (u(i), v(i))
u = Data(:, 1);
v = Data(:, 2);

% Restriction inicialization
lim_inf = Data(:, 3).^2 ;
lim_sup = Data(:, 4).^2 ;
disp('# All restricitons loaded')

% Initiate enviromental variables:
% Objective value variables;
I = speye(n,n);
c = sparse(1, 2*m)';

% (SDPT3 Configuration) initiate block properties
blk{1,1} = 's'; blk{1,2} = n;
blk{2,1} = 'l'; blk{2,2} = 2*m;

disp('Generating A(G) and B matrix...')
% Generating A(G) matrix, b vector and B matrix (same loop):
A1 = [];
z =  [1, -1, -1, 1];

% generation of vector b;
b = sparse(1, 2*m + n)';

% creating matrix B;
B = sparse(2*m + n, 2*m);

for i = 1:m
    % first the upper constraints;
    key = [u(i), v(i), u(i), v(i)];
    target = [u(i), u(i), v(i), v(i)];
    E = sparse(key, target, z, n, n);
    A1 = [A1; svec(blk(1,:),E)'];
    
    % second the vector b;
    b(i) = lim_sup(i);
    b(m + i) = lim_inf(i);
    
    % last the B matrix;
    B(i, i) = 1;
    B(m + i, m + i) = -1;
end
fprintf('Completed generation for B matrix and b vector!\n')

% A2 will be the second (the lower constraints);
A = [A1; A1];

% Now the centering conditions;
for i = 1:n
    E = sparse(n,n); E(:,i) = ones(n,1);
    E = (E + E');
    A = [A; svec(blk(1,:),E)'];
end

fprintf('Complete creation of matrix A(G)!\n')
clearvars Z key target E

% start solving
At{1} = A';
At{2} = B';
C{1} = - I;
C{2} = c';
disp('SDPT3 - Start Solving.')
[~,sol, ~, ~, info] = sdpt3(blk,At,C,b);
fprintf('>> Solver conclusion: %s\n', info.msg3);

G = sol{1};

disp('# Get spectral decomposition of solution')
Y = double(G);
[V, La] = eig(Y);

[~,idx] = sort(diag(La),'descend');
D = La(idx,idx);
V = V(:,idx);

% not projected solution
non_scaled = sqrt(D)*V';
non_scaled = non_scaled';

% K-scaled solution: K = 3, "projection" onto 3-dimensional Euclidian Space
Q = V(:,1:3);
conformation = sqrt(D(1:3,1:3)) * Q';
conformation = conformation';
end