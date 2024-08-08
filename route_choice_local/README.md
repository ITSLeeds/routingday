

The starting point is the following
[example](https://github.com/AequilibraE/aequilibrae/blob/develop/docs/source/examples/assignment_workflows/plot_route_choice.py)
(rendered on their
[website](https://aequilibrae.com/python/latest/_auto_examples/assignment_workflows/plot_route_choice_set.html#sphx-glr-auto-examples-assignment-workflows-plot-route-choice-set-py))
from the Aequillibrae documentation:

<details>

``` python
# Imports
from uuid import uuid4
from tempfile import gettempdir
from os.path import join
from aequilibrae.utils.create_example import create_example
```

``` python
# sphinx_gallery_thumbnail_path = 'images/plot_route_choice_assignment.png'

# %%

# We create the example project inside our temp folder
fldr = join(gettempdir(), uuid4().hex)

project = create_example(fldr, "coquimbo")

# %%
import logging
import sys

# We the project opens, we can tell the logger to direct all messages to the terminal as well
logger = project.logger
stdout_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s;%(levelname)s ; %(message)s")
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)

# %%
# Route Choice
# ------------

# %%
import numpy as np

# %%
# Model parameters
# ~~~~~~~~~~~~~~~~
# We'll set the parameters for our route choice model. These are the parameters that will be used to calculate the
# utility of each path. In our example, the utility is equal to *theta* * distance
# And the path overlap factor (PSL) is equal to *beta*.

# Distance factor
theta = 0.00011

# PSL parameter
beta = 1.1

# %%
# Let's build all graphs
project.network.build_graphs()
```

    /home/robin/.virtualenvs/r-reticulate/lib/python3.10/site-packages/aequilibrae/project/network/network.py:327: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
      df = pd.read_sql(sql, conn).fillna(value=np.nan)

``` python
# We get warnings that several fields in the project are filled with NaNs.
# This is true, but we won't use those fields.

# %%
# We grab the graph for cars
graph = project.network.graphs["c"]

# %%
# We also see what graphs are available
project.network.graphs.keys()
```

    dict_keys(['b', 'c', 't', 'w'])

``` python
od_pairs_of_interest = [(71645, 79385), (77011, 74089)]
nodes_of_interest = (71645, 74089, 77011, 79385)

# %%
# let's say that utility is just a function of distance
# So we build our *utility* field as the distance times theta
graph.network = graph.network.assign(utility=graph.network.distance * theta)

# %%
# Prepare the graph with all nodes of interest as centroids
graph.prepare_graph(np.array(nodes_of_interest))

# %%
# And set the cost of the graph the as the utility field just created
graph.set_graph("utility")

# %%
# We allow flows through "centroid connectors" because our centroids are not really centroids
# If we have actual centroid connectors in the network (and more than one per centroid) , then we
# should remove them from the graph
graph.set_blocked_centroid_flows(False)

# %%
# Mock demand matrix
# ~~~~~~~~~~~~~~~~~~
# We'll create a mock demand matrix with demand `1` for every zone.
from aequilibrae.matrix import AequilibraeMatrix

names_list = ["demand", "5x demand"]

mat = AequilibraeMatrix()
mat.create_empty(zones=graph.num_zones, matrix_names=names_list, memory_only=True)
mat.index = graph.centroids[:]
mat.matrices[:, :, 0] = np.full((graph.num_zones, graph.num_zones), 10.0)
mat.matrices[:, :, 1] = np.full((graph.num_zones, graph.num_zones), 50.0)
mat.computational_view()

# %%
# Route Choice class
# ~~~~~~~~~~~~~~~~~~
# Here we'll construct and use the Route Choice class to generate our route sets
from aequilibrae.paths import RouteChoice

# %%
# This object construct might take a minute depending on the size of the graph due to the construction of the compressed
# link to network link mapping that's required.  This is a one time operation per graph and is cached. We need to
# supply a Graph and optionally a AequilibraeMatrix, if the matrix is not provided link loading cannot be preformed.
rc = RouteChoice(graph)
rc.add_demand(mat)

# %%
# Here we'll set the parameters of our set generation. There are two algorithms available: Link penalisation, or BFSLE
# based on the paper
# "Route choice sets for very high-resolution data" by Nadine Rieser-Schüssler, Michael Balmer & Kay W. Axhausen (2013).
# https://doi.org/10.1080/18128602.2012.671383
#
# Our BFSLE implementation is slightly different and has extended to allow applying link penalisation as well. Every
# link in all routes found at a depth are penalised with the `penalty` factor for the next depth. So at a depth of 0 no
# links are penalised nor removed. At depth 1, all links found at depth 0 are penalised, then the links marked for
# removal are removed. All links in the routes found at depth 1 are then penalised for the next depth. The penalisation
# compounds. Pass set `penalty=1.0` to disable.
#
# To assist in filtering out bad results during the assignment, a `cutoff_prob` parameter can be provided to exclude
# routes from the path-sized logit model. The `cutoff_prob` is used to compute an inverse binary logit and obtain a max
# difference in utilities. If a paths total cost is greater than the minimum cost path in the route set plus the max
# difference, the route is excluded from the PSL calculations. The route is still returned, but with a probability of
# 0.0.
#
# The `cutoff_prob` should be in the range [0, 1]. It is then rescaled internally to [0.5, 1] as probabilities below 0.5
# produce negative differences in utilities. A higher `cutoff_prob` includes more routes. A value of `0.0` will only
# include the minimum cost route. A value of `1.0` includes all routes.
#
# It is highly recommended to set either `max_routes` or `max_depth` to prevent runaway results.

# %%
# rc.set_choice_set_generation("link-penalisation", max_routes=5, penalty=1.02)
rc.set_choice_set_generation("bfsle", max_routes=5)

# %%
# All parameters are optional, the defaults are:
print(rc.default_parameters)
```

    {'generic': {'seed': 0, 'max_routes': 0, 'max_depth': 0, 'max_misses': 100, 'penalty': 1.01, 'cutoff_prob': 0.0, 'beta': 1.0, 'store_results': True}, 'link-penalisation': {}, 'bfsle': {'penalty': 1.0}}

``` python
# %%
# We can now perform a computation for single OD pair if we'd like. Here we do one between the first and last centroid
# as well an an assignment.
results = rc.execute_single(77011, 74089, demand=1.0)
print(results[0])
```

    (24222, 30332, 30333, 10435, 30068, 30069, 14198, 14199, 31161, 30928, 30929, 30930, 30931, 24172, 30878, 30879, 30880, 30881, 30882, 30883, 30884, 30885, 30886, 30887, 30888, 30889, 30890, 30891, 5179, 5180, 5181, 5182, 26463, 26462, 26461, 26460, 26459, 26458, 26457, 26456, 26480, 3341, 3342, 3339, 9509, 9510, 9511, 9512, 18487, 14972, 14973, 32692, 32693, 32694, 2300, 2301, 33715, 19978, 19979, 19977, 19976, 19975, 19974, 19973, 19972, 19971, 19970, 22082, 22080, 5351, 5352, 2280, 2281, 2282, 575, 576, 577, 578, 579, 536, 537, 538, 539, 540, 541, 15406, 15407, 15408, 553, 552, 633, 634, 635, 630, 631, 632, 623, 624, 625, 626, 471, 5363, 34169, 34170, 34171, 34785, 6466, 6465, 29938, 29939, 29940, 29941, 1446, 1447, 1448, 1449, 1450, 939, 940, 941, 9840, 9841, 26314, 26313, 26312, 26311, 26310, 26309, 26308, 26307, 26306, 26305, 26304, 26303, 26302, 26301, 26300, 34079, 34147, 29962, 26422, 26421, 26420, 765, 764, 763, 762, 761, 760, 736, 10973, 10974, 10975, 725, 10972, 727, 728, 26424, 733, 734, 29899, 20970, 20969, 20968, 20967, 20966, 20965, 20964, 20963, 20962, 9584, 9583, 20981, 21398, 20982, 34208, 35, 36, 59, 60, 61, 22363, 22364, 22365, 22366, 22367, 28958, 28959, 28960, 28961, 28962, 28805, 28806, 28807, 28808, 28809, 28810, 28827, 28828, 28829, 28830, 28874)

``` python
# %%
# Because we asked it to also perform an assignment we can access the various results from that
# The default return is a Pyarrow Table but Pandas is nicer for viewing.
res = rc.get_results().to_pandas()
res.head()
```

       origin id  destination id  ... path overlap  probability
    0      77011           74089  ...     0.386507     0.231745
    1      77011           74089  ...     0.287132     0.175078
    2      77011           74089  ...     0.304541     0.184599
    3      77011           74089  ...     0.430542     0.257506
    4      77011           74089  ...     0.246836     0.151071

    [5 rows x 7 columns]

``` python
# %%
# let's define a function to plot assignment results


def plot_results(link_loads):
    import folium
    import geopandas as gpd

    link_loads = link_loads[["link_id", "demand_tot"]]
    link_loads = link_loads[link_loads.demand_tot > 0]
    max_load = link_loads["demand_tot"].max()
    links = gpd.GeoDataFrame(project.network.links.data, crs=4326)
    loaded_links = links.merge(link_loads, on="link_id", how="inner")

    loads_lyr = folium.FeatureGroup("link_loads")

    # Maximum thickness we would like is probably a 10, so let's make sure we don't go over that
    factor = 10 / max_load

    # Let's create the layers
    for _, rec in loaded_links.iterrows():
        points = rec.geometry.wkt.replace("LINESTRING ", "").replace("(", "").replace(")", "").split(", ")
        points = "[[" + "],[".join([p.replace(" ", ", ") for p in points]) + "]]"
        # we need to take from x/y to lat/long
        points = [[x[1], x[0]] for x in eval(points)]
        _ = folium.vector_layers.PolyLine(
            points,
            tooltip=f"link_id: {rec.link_id}, Flow: {rec.demand_tot:.3f}",
            color="red",
            weight=factor * rec.demand_tot,
        ).add_to(loads_lyr)
    long, lat = project.conn.execute("select avg(xmin), avg(ymin) from idx_links_geometry").fetchone()

    map_osm = folium.Map(location=[lat, long], tiles="Cartodb Positron", zoom_start=12)
    loads_lyr.add_to(map_osm)
    folium.LayerControl().add_to(map_osm)
    return map_osm


# %%
plot_results(rc.get_load_results())
```

    <folium.folium.Map object at 0x7cee336479a0>

``` python
# %%
# To perform a batch operation we need to prepare the object first. We can either provide a list of tuple of the OD
# pairs we'd like to use, or we can provided a 1D list and the generation will be run on all permutations.
# rc.prepare(graph.centroids[:5])
rc.prepare()

# %%
# Now we can perform a batch computation with an assignment
rc.execute(perform_assignment=True)
res = rc.get_results().to_pandas()
res.head()
```

       origin id  destination id  ... path overlap  probability
    0      71645           74089  ...     0.384514     0.204478
    1      71645           74089  ...     0.273951     0.145623
    2      71645           74089  ...     0.544362     0.285155
    3      71645           74089  ...     0.443492     0.234682
    4      71645           74089  ...     0.243935     0.130063

    [5 rows x 7 columns]

``` python
# %%
# Since we provided a matrix initially we can also perform link loading based on our assignment results.
rc.get_load_results()
```

           link_id  5x demand_ab  5x demand_ba  ...  demand_ab  demand_ba  demand_tot
    0            1           0.0           0.0  ...        0.0        0.0         0.0
    1            2           0.0           0.0  ...        0.0        0.0         0.0
    2            3           0.0           0.0  ...        0.0        0.0         0.0
    3           12           0.0           0.0  ...        0.0        0.0         0.0
    4           13           0.0           0.0  ...        0.0        0.0         0.0
    ...        ...           ...           ...  ...        ...        ...         ...
    19978    34938           0.0           0.0  ...        0.0        0.0         0.0
    19979    34939           0.0           0.0  ...        0.0        0.0         0.0
    19980    34940           0.0           0.0  ...        0.0        0.0         0.0
    19981    34941           0.0           0.0  ...        0.0        0.0         0.0
    19982    34942           0.0           0.0  ...        0.0        0.0         0.0

    [19983 rows x 7 columns]

``` python
# %% we can plot these as well
plot_results(rc.get_load_results())
```

    <folium.folium.Map object at 0x7cee358621a0>

``` python
# %%
# Select link analysis
# ~~~~~~~~~~~~~~~~~~~~
# We can also enable select link analysis by providing the links and the directions that we are interested in.  Here we
# set the select link to trigger when (7369, 1) and (20983, 1) is utilised in "sl1" and "sl2" when (7369, 1) is
# utilised.
rc.set_select_links({"sl1": [[(7369, 1), (20983, 1)]], "sl2": [(7369, 1)]})
rc.execute(perform_assignment=True)

# %%
# We can get then the results in a Pandas data frame for both the network.
sl = rc.get_select_link_loading_results()
sl
```

           link_id  sl1_5x demand_ab  ...  sl2_demand_ba  sl2_demand_tot
    0            1               0.0  ...            0.0             0.0
    1            2               0.0  ...            0.0             0.0
    2            3               0.0  ...            0.0             0.0
    3           12               0.0  ...            0.0             0.0
    4           13               0.0  ...            0.0             0.0
    ...        ...               ...  ...            ...             ...
    19978    34938               0.0  ...            0.0             0.0
    19979    34939               0.0  ...            0.0             0.0
    19980    34940               0.0  ...            0.0             0.0
    19981    34941               0.0  ...            0.0             0.0
    19982    34942               0.0  ...            0.0             0.0

    [19983 rows x 13 columns]

``` python
# %%
# We can also access the OD matrices for this link loading. These matrices are sparse and can be converted to
# scipy.sparse matrices for ease of use. They're stored in a dictionary where the key is the matrix name concatenated
# wit the select link set name via an underscore. These matrices are constructed during `get_select_link_loading_results`.
rc.get_select_link_od_matrix_results()
```

    {'sl1': {'demand': <aequilibrae.matrix.sparse_matrix.COO object at 0x7cee1b51c880>, '5x demand': <aequilibrae.matrix.sparse_matrix.COO object at 0x7cee1b51e0e0>}, 'sl2': {'demand': <aequilibrae.matrix.sparse_matrix.COO object at 0x7cee1b51cdc0>, '5x demand': <aequilibrae.matrix.sparse_matrix.COO object at 0x7cee1b51e7a0>}}

``` python
# %%
od_matrix = rc.get_select_link_od_matrix_results()["sl1"]["demand"]
od_matrix.to_scipy().toarray()
```

    array([[0.        , 0.        , 0.        , 3.04610785],
           [0.        , 0.        , 0.        , 0.        ],
           [0.        , 0.        , 0.        , 0.        ],
           [0.        , 0.        , 0.        , 0.        ]])

``` python

# %%
project.close()
```

</details>
