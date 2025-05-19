import geopandas as gpd
import json
import os
from datetime import datetime
from shapely import Point


def create_stac_collection(collection_id, description, extent, output_dir):
    collection = {
        "stac_version": "1.0.0",
        "id": collection_id,
        "description": description,
        "extent": extent,
        "links": [],
    }

    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, f"{collection_id}.json"), "w") as f:
        json.dump(collection, f, indent=2)


def create_stac_item(geometry, properties, item_id, collection_id, output_dir):
    item = {
        "stac_version": "1.0.0",
        "type": "Feature",
        "id": item_id,
        "geometry": geometry,
        "properties": properties,
        "assets": {
            "data": {
                "href": f"https://example.com/{item_id}.geojson",
                "type": "application/geo+json",
                "title": "GeoJSON data",
            }
        },
        "links": [
            {"rel": "self", "href": f"{item_id}.json", "type": "application/json"},
            {"rel": "parent", "href": "collection.json", "type": "application/json"},
        ],
    }

    with open(os.path.join(output_dir, f"{item_id}.json"), "w") as f:
        json.dump(item, f, indent=2)


def create_stac_catalog_from_geodataframe(gdf, collection_id, description, output_dir):
    # Calculate spatial and temporal extents
    bbox = gdf.total_bounds.tolist()
    start_time = gdf["datetime"].min().isoformat()
    end_time = gdf["datetime"].max().isoformat()
    extent = {
        "spatial": {"bbox": [bbox]},
        "temporal": {"interval": [[start_time, end_time]]},
    }

    # Create the STAC Collection
    create_stac_collection(collection_id, description, extent, output_dir)

    # Create STAC Items for each row in the GeoDataFrame
    for idx, row in gdf.iterrows():
        geometry = row["geometry"].__geo_interface__
        properties = {
            "datetime": row["datetime"].isoformat(),
            "name": row["name"],
            "description": row["description"],
        }
        item_id = f"{collection_id}-item-{idx}"
        create_stac_item(geometry, properties, item_id, collection_id, output_dir)


# Example usage
if __name__ == "__main__":
    # Create a sample GeoDataFrame
    data = {
        "name": ["Point1", "Point2"],
        "description": ["Description1", "Description2"],
        "datetime": [datetime(2020, 1, 1), datetime(2020, 1, 2)],
        "geometry": [Point(125.6, 10.1), Point(125.7, 10.2)],
    }
    gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")

    # Generate STAC Catalog
    create_stac_catalog_from_geodataframe(
        gdf, "example-collection", "Example description", "output_dir"
    )
