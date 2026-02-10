include "globals.mzn";

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Clustered, weighted, undirected graph generator
% Outputs a bidirectional edge list: (from,to,cost) and (to,from,cost)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

int: n  = 10;        % number of nodes
int: cl = 3;        % number of clusters
% int: m  = 10;       % number of undirected edges (0..n*(n-1)/2)


var n-1..n*3: m;       
int: w_min = 1;
int: w_max = 30;

set of int: V = 1..n;
set of int: C = 1..cl;

% Cluster assignment
array[V] of var C: cluster;

% Undirected adjacency matrix
array[V,V] of var bool: E;

% Symmetric weights (meaningful only when E[i,j] is true)
array[V,V] of var w_min..w_max: w;
constraint
  forall(i in V)(
    all_different(w[..,i])
  );
  
% --- Graph structure ---
constraint forall(i in V)( E[i,i] = false );

constraint forall(i,j in V where i < j)(
  E[i,j] = E[j,i] /\
  w[i,j] = w[j,i]
);

% exactly m undirected edges
constraint sum(i,j in V where i < j)(bool2int(E[i,j])) <= m;

% --- Connected constraint ---
% existing
constraint sum(i,j in V where i < j)(bool2int(E[i,j])) <= m;

% then connectivity constraints
array[V,V] of var 0..n-1: f;

constraint forall(i,j in V)(
  f[i,j] <= (n-1) * bool2int(E[i,j])
);

int: root = 1;

constraint
  sum(j in V)(f[root,j]) - sum(j in V)(f[j,root]) = n - 1;

constraint forall(v in V where v != root)(
  sum(j in V)(f[j,v]) - sum(j in V)(f[v,j]) = 1
);


% --- Cluster constraints ---
% every cluster non-empty
constraint forall(c in C)(
  exists(v in V)(cluster[v] = c)
);

% --- Optional: bias edges to be within clusters ---
var int: intra_edges =
  sum(i,j in V where i < j)(
    bool2int(E[i,j] /\ (cluster[i] = cluster[j]))
  );

% Pick one:
% solve maximize intra_edges;
solve satisfy;

% --- Output ---
output [
  "n = ", show(n), "\n",
  "cl = ", show(cl), "\n\n",

  "cluster = [",
  concat([ show(cluster[v]) ++ (if v < n then ", " else "" endif) | v in V ]),
  "]  % node 1..n\n\n",

  "edges = [",
  concat([
    "  (" ++ show(i) ++ ", " ++ show(j) ++ ", " ++ show(w[i,j]) ++ ")," ++
    "  (" ++ show(j) ++ ", " ++ show(i) ++ ", " ++ show(w[i,j]) ++ "),"
    | i,j in V where i < j /\ fix(E[i,j])
  ]),
  "]\n\n",

  "intra_edges = ", show(intra_edges), "\n"
];
