% This function reads the avaliable proteins for test,
% and the executes the SDP relax algorithm for them.

% Open the file containing the protein names and paths;
fid = fopen('proteins.txt', 'r+');
proteins = textscan(fid, '%s %s %s', 'delimiter', ',');
fclose(fid);
disp('# proteins.txt read complete!')

% style: (Nodes) (Nodes-path) (Tests-path)
Nodes = proteins{1, 1}; 
Nodes_path = proteins{1, 2};
Tests_path = proteins{1, 3};


n = length(Nodes);
fprintf('# Total number of nodes read: %d \n', n)
for i = 1 : n
    fprintf('# Protein: %s \n', Nodes{i})
    path = Nodes_path{i};
    test_path = Tests_path{i};
    
    % Get distance data file from the respective node;
    dist = readtable(sprintf('%s\\dist.txt', path));
    disp('# Distance file read: Complete')

    % Using the data, creating an acess matrix as [i,j, l_ij, u_ij]
    Data = [dist(:,1), dist(:,2), dist(:,9), dist(:,10)];

    clearvars dist_data

    % table ~~> array
    Data = table2array(Data);
    
    tic;
    [non_scaled, conformation, info] = spdprotein(Data);
    t = toc;
    
    % Generating output files from obtained solutions
    disp('# Generating output files from obtained solutions')

    % first --nonscaled solution
    file_dir = sprintf('%s\\relax_np.txt', test_path); 
    dlmwrite(file_dir, non_scaled, 'delimiter', ' ');

    % second -- K-scaled solution
    file_dir = sprintf('%s\\relax_k.txt', test_path);
    dlmwrite(file_dir, conformation, 'delimiter', ' ');

    % disable output diary(Log) feature;
    disp('# Process completed successfully!')
    disp('------------------------------------------------------')

    % Save solver output to file; 
    file_dir = sprintf('%s\\solver_varargout.txt', test_path);
    solveriter = sprintf('"solveriter": "%d"', info.iter);
    solvertime = sprintf('"solvertime": "%d"', info.cputime);
    time = sprintf('"elapsed time": "%d"' ,t);
    info = sprintf('"info": "%s"' ,string(info.msg3));

    msg = sprintf('{%s, %s, %s, %s}', solveriter, solvertime, time, info);

    diagnostics_out = msg;
    fid = fopen(file_dir, 'w+');
    fprintf(fid, diagnostics_out);
    fclose(fid);
end
disp('# The [SDP] process was successfully completed !')