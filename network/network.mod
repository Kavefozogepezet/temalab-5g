/*********************************************
 * OPL 22.1.1.0 Model
 * Author: kavefozogepezet
 * Creation Date: 1 Oct 2023 at 09:43:35
 *********************************************/

tuple Edge {
  int node1;
  int node2;
  float cost;
}
 
int node_count = ...;
range node_range = 1..node_count;

{Edge} edges = ...;

int source = ...;
int destination = ...;

dvar boolean selected[edges];
dvar float cost;
 
 minimize cost;
 
 subject to {
   cost == sum(e in edges) e.cost * selected[e];
   
   forall(i in node_range) {
     (sum(e in edges: e.node1 == i) selected[e])
     - (sum(e in edges: e.node2 == i) selected[e])
       == (i == source ? 1 : (i == destination ? -1 : 0));
   }
}
 
 execute {
   write("Cost: ");
   writeln(cost);
   
   writeln("Edges: ");
   for(e in edges) {
     if(selected[e] == 1) {
       writeln(e);
     }
   }
 }