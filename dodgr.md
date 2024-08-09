dodgr
================
Malcolm Morgan
2024-08-09

## Load Inputs

# Build graph

# Get Routes

Extracting Origins and Destinations

``` r
origins <- lwgeom::st_startpoint(od_geo) |> st_as_sf()
origins <- st_coordinates(origins)


destinations <- lwgeom::st_endpoint(od_geo) |> st_as_sf()
destinations <- st_coordinates(destinations)
```

Routing

``` r
paths = dodgr_paths(graph, origins, destinations, pairwise = TRUE)
```

user system elapsed 27.16 0.35 26.91

Helper function from UK2GTFS

``` r
path_to_sf <- function(dp, verts, simplify = FALSE) {
    # Check for emplyr paths
    if (length(dp[[1]]) > 0) {
      path <- verts[match(dp[[1]], verts$id), ]
      path <- matrix(c(path$x, path$y), ncol = 2)
      path <- sf::st_linestring(path)

      if (simplify) {
        path <- sf::st_as_sfc(list(path), crs = 4326)
        path <- sf::st_transform(path, 27700)
        path <- sf::st_simplify(path, 5, preserveTopology = TRUE)
        path <- sf::st_transform(path, 4326)
        path <- path[[1]]
      }
      return(path)
    } else {
      return(NA)
    }
}

paths_to_sf <- function(paths, verts){
  dp.list <- purrr::map(paths, path_to_sf, verts = verts, .progress = TRUE)
  dp.list <- unname(dp.list)
  dp.list
}
```

``` r
verts = dodgr_vertices(graph)
paths2 = paths_to_sf(paths, verts)
paths2 = sf::st_as_sfc(paths2, crs = 4326)
```

Plot

``` r
plot(paths2)
```

![](dodgr_files/figure-gfm/unnamed-chunk-5-1.png)<!-- -->
