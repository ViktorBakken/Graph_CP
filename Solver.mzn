% Input
int: n; % number of nodes
int: m; % number of directional edges
int: K; % budget
set of int: V=0..n-1; % set of nodes
set of int: E=0..m-1; % set of edges
set of int: E_can = { e | e in E where i[e] in S /\ not (j[e] in S) };

array[E] of int: i; % the tail vector of edge
array[E] of int: j; % the head vector of edges
array[E] of int: c; % the cost vector of edges
array[V] of int: b; % the vector of start node and ending node

set of int: S={s | s in index_set(b) where b[s]=1};
set of int: T={t | t in index_set(b) where b[t]=-1};
% Decsion Variables
int: M = m;  % upperbound of beta

array[V] of var -2*M..M: pi; 
array[E] of var 0..M: beta; 
array[E] of var 0..M: w;
array[E] of var 0..1: x; % interdiction vector
array[0..0] of var 0..0:z; % Does Nothing 

% Constraints
constraint forall(s in S)(pi[s]=0);


constraint sum(x) <= K;  % ensure interdiction stays within budget

%T^T*pi - beta <= c    
%pi_i - pi_j - beta_ij <= c_ij
constraint forall(e in E)(
  (pi[i[e]] - pi[j[e]] - beta[e] <= c[e])
);

%beta_ij - M_ij*x_ij <= w_ij
constraint forall(e in E)(beta[e] - M*x[e] <= w[e]);

% Interdicted edges are connected to infected nodes
% constraint forall(e in E)(x[e]=1->(i[e] in S/\(j[e] in S)=false));
constraint forall(e in E diff E_can)(x[e] = 0);

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