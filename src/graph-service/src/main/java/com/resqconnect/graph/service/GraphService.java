package com.resqconnect.graph.service;

import com.resqconnect.graph.model.RequestNode;
import com.resqconnect.graph.model.VolunteerNode;
import com.resqconnect.graph.repository.RequestRepository;
import com.resqconnect.graph.repository.VolunteerRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

@Service
public class GraphService {

    @Autowired
    private RequestRepository requestRepository;

    @Autowired
    private VolunteerRepository volunteerRepository;

    public RequestNode createRequest(RequestNode request) {
        request.setCreatedAt(LocalDateTime.now());
        if (request.getStatus() == null) {
            request.setStatus("OPEN");
        }
        return requestRepository.save(request);
    }

    public VolunteerNode createVolunteer(VolunteerNode volunteer) {
        volunteer.setLastActive(LocalDateTime.now());
        if (volunteer.getAvailable() == null) {
            volunteer.setAvailable(true);
        }
        if (volunteer.getMaxDistance() == null) {
            volunteer.setMaxDistance(10.0); // Default 10km radius
        }
        return volunteerRepository.save(volunteer);
    }

    public List<VolunteerNode> findNearbyVolunteers(Double latitude, Double longitude, 
                                                   Double radiusKm, String skills) {
        if (skills != null && !skills.isEmpty()) {
            return volunteerRepository.findNearbyAvailableVolunteersWithSkills(
                latitude, longitude, radiusKm * 1000, skills); // Convert to meters
        } else {
            return volunteerRepository.findNearbyAvailableVolunteers(
                latitude, longitude, radiusKm * 1000);
        }
    }

    public List<RequestNode> findNearbyRequests(Double latitude, Double longitude, 
                                               Double radiusKm, String status) {
        if (status != null && !status.isEmpty()) {
            return requestRepository.findNearbyRequestsByStatus(
                latitude, longitude, radiusKm * 1000, status);
        } else {
            return requestRepository.findNearbyRequests(
                latitude, longitude, radiusKm * 1000);
        }
    }

    public void assignVolunteerToRequest(String volunteerId, String requestId) {
        Optional<VolunteerNode> volunteer = volunteerRepository.findById(volunteerId);
        Optional<RequestNode> request = requestRepository.findById(requestId);
        
        if (volunteer.isPresent() && request.isPresent()) {
            requestRepository.assignVolunteerToRequest(volunteerId, requestId);
        } else {
            throw new RuntimeException("Volunteer or Request not found");
        }
    }

    public List<RequestNode> getVolunteerAssignments(String volunteerId) {
        return requestRepository.findByAssignedVolunteerId(volunteerId);
    }

    public List<VolunteerNode> getRequestVolunteers(String requestId) {
        return volunteerRepository.findByAssignedRequestId(requestId);
    }

    public void updateRequestStatus(String requestId, String status) {
        requestRepository.updateRequestStatus(requestId, status);
    }

    public void updateVolunteerAvailability(String volunteerId, Boolean available) {
        volunteerRepository.updateVolunteerAvailability(volunteerId, available);
        volunteerRepository.updateLastActive(volunteerId, LocalDateTime.now());
    }

    public Map<String, Object> getGraphStats() {
        Map<String, Object> stats = new HashMap<>();
        
        stats.put("totalRequests", requestRepository.count());
        stats.put("totalVolunteers", volunteerRepository.count());
        stats.put("openRequests", requestRepository.countByStatus("OPEN"));
        stats.put("assignedRequests", requestRepository.countByStatus("ASSIGNED"));
        stats.put("completedRequests", requestRepository.countByStatus("COMPLETED"));
        stats.put("availableVolunteers", volunteerRepository.countByAvailable(true));
        stats.put("activeAssignments", requestRepository.countActiveAssignments());
        
        return stats;
    }
}