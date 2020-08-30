# COSC364Assignment
COSC364 Routing Information Protocol (RIP) assignment. For this assignment we were required to create an implementation of a RIP router in Python. The router reads configuration information detailing its neighbours and their link costs. It then begins send RIP response packets to each of its neighbours from which they build up the a routing table of optimal paths to all reachable routers in the overall topology. Routers respond to failures of neighbours allowing the topology to adapt to changes. 

<H3>Classes</h3>
<ul>
  <li>Router</li>
  <li>Routing Table</li>
  <li>Response</li>
  <li>Config</li>
  <li>Timer (Not in use)</li>
</ul

<h3>Running</h3>
command line: python3 router.py {router config txt}

<h3>Tests</h3>
<ul>
    <li>Basic Topology Convergence</li>
    <li>Failure of Transit node</li>
    <li>Large Topology</li>
    <li>Reinitialisation of dead neighbour before garbage collection</li>
    <li>Reinitialisation of neighbour after garbage collection</li>
    <li>Multiple Neighbour Failure</li>
    <li>Out of range link metric test</li>
    <li>Count to infinity scenario</li>
</ul>
