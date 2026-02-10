% Input
int: n; % number of nodes
int: m; % number of directional edges
int: K; % budget
set of int: V=1..n; % set of nodes
set of int: A=1..m; % set of edges
array[A] of float: tail; % the tail vector of edge
array[A] of float: head; % the head vector of edges
array[A] of float: c; % the cost vector of edges
array[V] of float: b; % the vector of start node and ending node

% Decsion Variables
float: M = sum(c);  % upperbound of beta

array[V] of float: pi; 
array[A] of 0.0..M: beta; 
array[A] of float: w; 
array[A] of 0..1: x; % interdiction vector

% Constraints
constraint forall(a in A)(0.0 <= w[a]);
constraint sum(x) <= K;  % ensure interdiction stays within budget

%T^T*pi - beta <= c    
%pi_i - pi_j - beta_ij <= c_ij
constraint forall(a in A)(pi[tail[a]] - pi[head[a]] - beta[a] <= c[a]);

%beta_ij - M_ij*x_ij <= w_ij
constraint forall(a in A)(beta[a] - M*x[a] <= w[a]);

% Objective
var float: obj= sum(v in V)(b[v] * pi[v]) - sum(w);

solve maximize obj;

output [
  "pi=", show(pi), "\n",
  "beta=", show(beta), "\n",
  "x=", show(x), "\n"
]