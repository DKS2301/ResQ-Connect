package com.resqconnect.graph.model;

import org.springframework.data.neo4j.core.schema.Id;
import org.springframework.data.neo4j.core.schema.Node;
import org.springframework.data.neo4j.core.schema.Property;
import org.springframework.data.neo4j.core.schema.Relationship;

import java.time.LocalDateTime;
import java.util.Set;

@Node("Request")
public class RequestNode {
    
    @Id
    private String requestId;
    
    @Property("type")
    private String requestType;
    
    @Property("urgency")
    private Integer urgency;
    
    @Property("latitude")
    private Double latitude;
    
    @Property("longitude")
    private Double longitude;
    
    @Property("status")
    private String status;
    
    @Property("createdAt")
    private LocalDateTime createdAt;
    
    @Property("description")
    private String description;
    
    @Relationship(type = "ASSIGNED_TO", direction = Relationship.Direction.OUTGOING)
    private Set<VolunteerNode> assignedVolunteers;
    
    @Relationship(type = "NEAR", direction = Relationship.Direction.OUTGOING)
    private Set<LocationNode> nearbyLocations;

    // Constructors
    public RequestNode() {}
    
    public RequestNode(String requestId, String requestType, Integer urgency, 
                      Double latitude, Double longitude, String status, String description) {
        this.requestId = requestId;
        this.requestType = requestType;
        this.urgency = urgency;
        this.latitude = latitude;
        this.longitude = longitude;
        this.status = status;
        this.description = description;
        this.createdAt = LocalDateTime.now();
    }

    // Getters and Setters
    public String getRequestId() { return requestId; }
    public void setRequestId(String requestId) { this.requestId = requestId; }
    
    public String getRequestType() { return requestType; }
    public void setRequestType(String requestType) { this.requestType = requestType; }
    
    public Integer getUrgency() { return urgency; }
    public void setUrgency(Integer urgency) { this.urgency = urgency; }
    
    public Double getLatitude() { return latitude; }
    public void setLatitude(Double latitude) { this.latitude = latitude; }
    
    public Double getLongitude() { return longitude; }
    public void setLongitude(Double longitude) { this.longitude = longitude; }
    
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
    
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    
    public Set<VolunteerNode> getAssignedVolunteers() { return assignedVolunteers; }
    public void setAssignedVolunteers(Set<VolunteerNode> assignedVolunteers) { this.assignedVolunteers = assignedVolunteers; }
    
    public Set<LocationNode> getNearbyLocations() { return nearbyLocations; }
    public void setNearbyLocations(Set<LocationNode> nearbyLocations) { this.nearbyLocations = nearbyLocations; }
}