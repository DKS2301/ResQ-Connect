package com.resqconnect.graph.repository;

import com.resqconnect.graph.model.VolunteerNode;
import org.springframework.data.neo4j.repository.Neo4jRepository;
import org.springframework.data.neo4j.repository.query.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface VolunteerRepository extends Neo4jRepository<VolunteerNode, String> {

    @Query("MATCH (v:Volunteer) " +
           "WHERE v.available = true AND " +
           "point.distance(point({latitude: v.latitude, longitude: v.longitude}), " +
           "point({latitude: $latitude, longitude: $longitude})) <= $radiusMeters " +
           "RETURN v ORDER BY " +
           "point.distance(point({latitude: v.latitude, longitude: v.longitude}), " +
           "point({latitude: $latitude, longitude: $longitude})) ASC")
    List<VolunteerNode> findNearbyAvailableVolunteers(@Param("latitude") Double latitude, 
                                                     @Param("longitude") Double longitude, 
                                                     @Param("radiusMeters") Double radiusMeters);

    @Query("MATCH (v:Volunteer) " +
           "WHERE v.available = true AND " +
           "ANY(skill IN v.skills WHERE skill CONTAINS $skills) AND " +
           "point.distance(point({latitude: v.latitude, longitude: v.longitude}), " +
           "point({latitude: $latitude, longitude: $longitude})) <= $radiusMeters " +
           "RETURN v ORDER BY " +
           "point.distance(point({latitude: v.latitude, longitude: v.longitude}), " +
           "point({latitude: $latitude, longitude: $longitude})) ASC")
    List<VolunteerNode> findNearbyAvailableVolunteersWithSkills(@Param("latitude") Double latitude, 
                                                               @Param("longitude") Double longitude, 
                                                               @Param("radiusMeters") Double radiusMeters,
                                                               @Param("skills") String skills);

    @Query("MATCH (v:Volunteer)<-[:ASSIGNED_TO]-(r:Request {requestId: $requestId}) " +
           "RETURN v")
    List<VolunteerNode> findByAssignedRequestId(@Param("requestId") String requestId);

    @Query("MATCH (v:Volunteer {volunteerId: $volunteerId}) " +
           "SET v.available = $available")
    void updateVolunteerAvailability(@Param("volunteerId") String volunteerId, 
                                    @Param("available") Boolean available);

    @Query("MATCH (v:Volunteer {volunteerId: $volunteerId}) " +
           "SET v.lastActive = $lastActive")
    void updateLastActive(@Param("volunteerId") String volunteerId, 
                         @Param("lastActive") LocalDateTime lastActive);

    @Query("MATCH (v:Volunteer) WHERE v.available = $available RETURN count(v)")
    Long countByAvailable(@Param("available") Boolean available);
}