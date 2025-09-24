package com.resqconnect.graph.model;

import org.springframework.data.neo4j.core.schema.Id;
import org.springframework.data.neo4j.core.schema.Node;
import org.springframework.data.neo4j.core.schema.Property;

@Node("Location")
public class LocationNode {
    
    @Id
    private String locationId;
    
    @Property("name")
    private String name;
    
    @Property("latitude")
    private Double latitude;
    
    @Property("longitude")
    private Double longitude;
    
    @Property("type")
    private String type; // hospital, shelter, supply_center, etc.

    // Constructors
    public LocationNode() {}
    
    public LocationNode(String locationId, String name, Double latitude, Double longitude, String type) {
        this.locationId = locationId;
        this.name = name;
        this.latitude = latitude;
        this.longitude = longitude;
        this.type = type;
    }

    // Getters and Setters
    public String getLocationId() { return locationId; }
    public void setLocationId(String locationId) { this.locationId = locationId; }
    
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public Double getLatitude() { return latitude; }
    public void setLatitude(Double latitude) { this.latitude = latitude; }
    
    public Double getLongitude() { return longitude; }
    public void setLongitude(Double longitude) { this.longitude = longitude; }
    
    public String getType() { return type; }
    public void setType(String type) { this.type = type; }
}