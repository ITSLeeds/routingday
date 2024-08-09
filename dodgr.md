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
time_dodgr1 <- system.time({
  paths <- dodgr_paths(graph, origins, destinations, pairwise = TRUE)
})
time_dodgr1
```

    ##    user  system elapsed 
    ##  68.991   1.161  68.719

``` r
time_dodgr1[3]
```

    ## elapsed 
    ##  68.719

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

paths_to_sf <- function(paths, verts) {
  dp.list <- purrr::map(paths, path_to_sf, verts = verts, .progress = TRUE)
  dp.list <- unname(dp.list)
  dp.list
}
```

``` r
verts <- dodgr_vertices(graph)
paths2 <- paths_to_sf(paths, verts)
paths2 <- sf::st_as_sfc(paths2, crs = 4326)
```

Plot

``` r
plot(paths2)
```

![](dodgr_files/figure-gfm/unnamed-chunk-5-1.png)<!-- -->

# Save times

``` r
timing_dodgr = data.frame(
  approach = "dodgr-no-contraction",
  version = as.character(packageVersion("dodgr")),
  date = Sys.Date(),
  time = round(time_dodgr1[3], 1)
)
# Save csv and append:
timings = readr::read_csv("timings.csv")
```

    ## Rows: 1 Columns: 4
    ## ── Column specification ────────────────────────────────────────────────────────
    ## Delimiter: ","
    ## chr  (2): approach, dodgr_version
    ## dbl  (1): time
    ## date (1): date
    ## 
    ## ℹ Use `spec()` to retrieve the full column specification for this data.
    ## ℹ Specify the column types or set `show_col_types = FALSE` to quiet this message.

``` r
# Combine and deduplicate:
timings = bind_rows(timings, timing_dodgr) |>
  distinct(approach, version, date)
readr::write_csv(timings, "timings.csv")
```
