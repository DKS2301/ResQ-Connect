package com.resqconnect.graph.controller;

import com.resqconnect.graph.model.RequestNode;
import com.resqconnect.graph.model.VolunteerNode;
import com.resqconnect.graph.service.GraphService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/graph")
@CrossOrigin(origins = "*")
public class GraphController {

    @Autowired
    private GraphService graphService;

    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of(
            "status", "healthy",
            "service", "graph-service"
        ));
    }

    @PostMapping("/requests")
    public ResponseEntity<RequestNode> createRequest(@RequestBody RequestNode request) {
        RequestNode created = graphService.createRequest(request);
        return ResponseEntity.ok(created);
    }

    @PostMapping("/volunteers")
    public ResponseEntity<VolunteerNode> createVolunteer(@RequestBody VolunteerNode volunteer) {
        VolunteerNode created = graphService.createVolunteer(volunteer);
        return ResponseEntity.ok(created);
    }

    @GetMapping("/volunteers/nearby")
    public ResponseEntity<List<VolunteerNode>> findNearbyVolunteers(
            @RequestParam Double latitude,
            @RequestParam Double longitude,
            @RequestParam(defaultValue = "10.0") Double radiusKm,
            @RequestParam(required = false) String skills) {
        
        List<VolunteerNode> volunteers = graphService.findNearbyVolunteers(
            latitude, longitude, radiusKm, skills);
        return ResponseEntity.ok(volunteers);
    }

    @GetMapping("/requests/nearby")
    public ResponseEntity<List<RequestNode>> findNearbyRequests(
            @RequestParam Double latitude,
            @RequestParam Double longitude,
            @RequestParam(defaultValue = "10.0") Double radiusKm,
            @RequestParam(required = false) String status) {
        
        List<RequestNode> requests = graphService.findNearbyRequests(
            latitude, longitude, radiusKm, status);
        return ResponseEntity.ok(requests);
    }

    @PostMapping("/assignments")
    public ResponseEntity<String> assignVolunteerToRequest(
            @RequestParam String volunteerId,
            @RequestParam String requestId) {
        
        graphService.assignVolunteerToRequest(volunteerId, requestId);
        return ResponseEntity.ok("Assignment created successfully");
    }

    @GetMapping("/volunteers/{volunteerId}/assignments")
    public ResponseEntity<List<RequestNode>> getVolunteerAssignments(@PathVariable String volunteerId) {
        List<RequestNode> assignments = graphService.getVolunteerAssignments(volunteerId);
        return ResponseEntity.ok(assignments);
    }

    @GetMapping("/requests/{requestId}/volunteers")
    public ResponseEntity<List<VolunteerNode>> getRequestVolunteers(@PathVariable String requestId) {
        List<VolunteerNode> volunteers = graphService.getRequestVolunteers(requestId);
        return ResponseEntity.ok(volunteers);
    }

    @PutMapping("/requests/{requestId}/status")
    public ResponseEntity<String> updateRequestStatus(
            @PathVariable String requestId,
            @RequestParam String status) {
        
        graphService.updateRequestStatus(requestId, status);
        return ResponseEntity.ok("Request status updated");
    }

    @PutMapping("/volunteers/{volunteerId}/availability")
    public ResponseEntity<String> updateVolunteerAvailability(
            @PathVariable String volunteerId,
            @RequestParam Boolean available) {
        
        graphService.updateVolunteerAvailability(volunteerId, available);
        return ResponseEntity.ok("Volunteer availability updated");
    }

    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getGraphStats() {
        Map<String, Object> stats = graphService.getGraphStats();
        return ResponseEntity.ok(stats);
    }
}