% Input
int: n; % number of nodes
int: m; % number of directional edges
int: K; % budget
int: inf;   % Infected edges

set of int: V=0..n-1; % set of nodes
set of int: E=0..m-1; % set of edges
set of int: E_inf = 0..inf-1;   % set of infected edges


array[E] of int: i; % the tail vector of edge
array[E] of int: j; % the head vector of edges
array[E] of int: c; % the cost vector of edges
array[E_inf] of int: idx_inf;  % index of infected edges
array[V] of int: b; % the vector of start node and ending node

set of int: S={s | s in index_set(b) where b[s]=1};

% Decsion Variables
int: M = n;  % upperbound of beta

array[V] of var -2*M..M: pi; 
array[E] of var 0..M: beta; 
array[E_inf] of var 0..M: w;
array[E_inf] of var 0..1: x; % interdiction vector
array[0..0] of var 0..0:z; % Does Nothing 

% Constraints
constraint forall(s in S)(pi[s]=0);

% ensure interdiction stays within budget
constraint sum(x) <= K;  

%T^T*pi - beta <= c    <=>  
%pi_i - pi_j - beta_ij <= c_ij
constraint forall(e in E)(
  (pi[i[e]] - pi[j[e]] - beta[e] <= c[e])
);

%beta_ij - M_ij*x_ij <= w_ij
constraint forall(k in E_inf)(beta[idx_inf[k]] - M*x[k] <= w[k]);

% Objective
var int: obj= sum(v in V)(b[v] * pi[v]) - sum(w);

solve maximize obj;
output [
  "obj=", show(obj),"\n",
  "pi=", show(pi), "\n",
  "w=", show(w), "\n",
  "beta=", show(beta), "\n",
  % "x=", show(x), "\n",
  "M=", show(M), "\n"
  ]