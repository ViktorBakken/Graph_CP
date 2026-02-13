% Input
int: n; % number of nodes
int: m; % number of undirectional edges
int: K; % budget
set of int: V=1..n; % set of nodes
set of int: E=1..m; % set of edges

array[E] of int: i; % the tail vector of edge
array[E] of int: j; % the head vector of edges
array[E] of int: c; % the cost vector of edges
array[V] of int: b; % the vector of start node and ending node

set of int: S={s | s in index_set(b) where b[s]=1};
set of int: T={t | t in index_set(b) where b[t]=-1};

% Decsion Variables
int: M = sum(c);  % upperbound of beta

array[V] of var int: pi; 
array[E] of var 0..M: beta; 
array[E] of var 0..: w; 
array[E] of var 0..1: x; % edges related to interdicted nodes
array[V] of var 0..1: z; % interdiction vector

% Constraints
constraint forall(s in S)(pi[s]=0);
constraint forall(t in T)(z[t]=0);


% constraint forall(e in E)(0 <= w[e]);
constraint sum(z) <= K;  % ensure interdiction stays within budget


% interdicted node's edges are removed
constraint forall(e in E)(
  x[e]<=z[i[e]]+z[j[e]]/\
  x[e]>=z[i[e]]/\
  x[e]>=z[j[e]] 
);




%T^T*pi - beta <= c    
%pi_i - pi_j - beta_ij <= c_ij
constraint forall(e in E)(
  (pi[i[e]] - pi[j[e]] - beta[e] <= c[e]) /\
  (pi[j[e]] - pi[i[e]] - beta[e] <= c[e])
);

%beta_ij - M_ij*x_ij <= w_ij
constraint forall(e in E)(beta[e] - M*x[e] <= w[e]);

constraint sum(s in S)(z[s])= sum(z);

% Objective
var int: obj= sum(v in V)(b[v] * pi[v]) - sum(w);

solve maximize obj;

output [
  "obj=", show(obj),"\n",
  "pi=", show(pi), "\n",
  "beta=", show(beta), "\n",
  "z=", show(z), "\n",
  "s=", show(S), ", t=", show(T),"\n"
]