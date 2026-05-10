def test(edges,rng):
    chosen_edges=[]
    new_edges=[]
    for edge in edges:
        (i,j)=edge
        if (j,i) not in chosen_edges:
            cost = generate_cost(rng)
            chosen_edges.append((i,j))
            new_edges.append((i,j,cost))
        else:
            cost = next(c for (a,b,c) in new_edges if (a,b) == (j,i))
            chosen_edges.append((i,j))
            new_edges.append((i,j,cost))

    return new_edges

def generate_cost(rng):
    return 1
    # return(int(rng.integers(1,101)))