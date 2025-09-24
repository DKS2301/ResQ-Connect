package com.resqconnect.graph.repository;

import com.resqconnect.graph.model.RequestNode;
import org.springframework.data.neo4j.repository.Neo4jRepository;
import org.springframework.data.neo4j.repository.query.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface RequestRepository extends Neo4jRepository<RequestNode, String> {

    @Query("MATCH (r:Request) " +
           "WHERE point.distance(point({latitude: r.latitude, longitude: r.longitude}), " +
           "point({latitude: $latitude, longitude: $longitude})) <= $radiusMeters " +
           "RETURN r ORDER BY r.urgency DESC, r.createdAt ASC")
    List<RequestNode> findNearbyRequests(@Param("latitude") Double latitude, 
                                        @Param("longitude") Double longitude, 
                                        @Param("radiusMeters") Double radiusMeters);

    @Query("MATCH (r:Request) " +
           "WHERE r.status = $status AND " +
           "point.distance(point({latitude: r.latitude, longitude: r.longitude}), " +
           "point({latitude: $latitude, longitude: $longitude})) <= $radiusMeters " +
           "RETURN r ORDER BY r.urgency DESC, r.createdAt ASC")
    List<RequestNode> findNearbyRequestsByStatus(@Param("latitude") Double latitude, 
                                                @Param("longitude") Double longitude, 
                                                @Param("radiusMeters") Double radiusMeters,
                                                @Param("status") String status);

    @Query("MATCH (r:Request)-[:ASSIGNED_TO]->(v:Volunteer {volunteerId: $volunteerId}) " +
           "RETURN r ORDER BY r.urgency DESC")
    List<RequestNode> findByAssignedVolunteerId(@Param("volunteerId") String volunteerId);

    @Query("MATCH (v:Volunteer {volunteerId: $volunteerId}), (r:Request {requestId: $requestId}) " +
           "CREATE (r)-[:ASSIGNED_TO]->(v)")
    void assignVolunteerToRequest(@Param("volunteerId") String volunteerId, 
                                 @Param("requestId") String requestId);

    @Query("MATCH (r:Request {requestId: $requestId}) " +
           "SET r.status = $status")
    void updateRequestStatus(@Param("requestId") String requestId, 
                            @Param("status") String status);

    @Query("MATCH (r:Request) WHERE r.status = $status RETURN count(r)")
    Long countByStatus(@Param("status") String status);

    @Query("MATCH (r:Request)-[:ASSIGNED_TO]->(v:Volunteer) " +
           "WHERE r.status IN ['OPEN', 'ASSIGNED', 'IN_PROGRESS'] " +
           "RETURN count(DISTINCT r)")
    Long countActiveAssignments();
}