package com.resqconnect.graph.model;

import org.springframework.data.neo4j.core.schema.Id;
import org.springframework.data.neo4j.core.schema.Node;
import org.springframework.data.neo4j.core.schema.Property;
import org.springframework.data.neo4j.core.schema.Relationship;

import java.time.LocalDateTime;
import java.util.Set;

@Node("Volunteer")
public class VolunteerNode {
    
    @Id
    private String volunteerId;
    
    @Property("name")
    private String name;
    
    @Property("skills")
    private Set<String> skills;
    
    @Property("latitude")
    private Double latitude;
    
    @Property("longitude")
    private Double longitude;
    
    @Property("available")
    private Boolean available;
    
    @Property("maxDistance")
    private Double maxDistance; // km
    
    @Property("lastActive")
    private LocalDateTime lastActive;
    
    @Relationship(type = "ASSIGNED_TO", direction = Relationship.Direction.INCOMING)
    private Set<RequestNode> assignedRequests;

    // Constructors
    public VolunteerNode() {}
    
    public VolunteerNode(String volunteerId, String name, Set<String> skills, 
                        Double latitude, Double longitude, Boolean available, Double maxDistance) {
        this.volunteerId = volunteerId;
        this.name = name;
        this.skills = skills;
        this.latitude = latitude;
        this.longitude = longitude;
        this.available = available;
        this.maxDistance = maxDistance;
        this.lastActive = LocalDateTime.now();
    }

    // Getters and Setters
    public String getVolunteerId() { return volunteerId; }
    public void setVolunteerId(String volunteerId) { this.volunteerId = volunteerId; }
    
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public Set<String> getSkills() { return skills; }
    public void setSkills(Set<String> skills) { this.skills = skills; }
    
    public Double getLatitude() { return latitude; }
    public void setLatitude(Double latitude) { this.latitude = latitude; }
    
    public Double getLongitude() { return longitude; }
    public void setLongitude(Double longitude) { this.longitude = longitude; }
    
    public Boolean getAvailable() { return available; }
    public void setAvailable(Boolean available) { this.available = available; }
    
    public Double getMaxDistance() { return maxDistance; }
    public void setMaxDistance(Double maxDistance) { this.maxDistance = maxDistance; }
    
    public LocalDateTime getLastActive() { return lastActive; }
    public void setLastActive(LocalDateTime lastActive) { this.lastActive = lastActive; }
    
    public Set<RequestNode> getAssignedRequests() { return assignedRequests; }
    public void setAssignedRequests(Set<RequestNode> assignedRequests) { this.assignedRequests = assignedRequests; }
}