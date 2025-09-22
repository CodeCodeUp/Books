package com.bookrs.recommendation.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class RecommendationService {
    
    @Value("${recommendation.service.url:http://localhost:5000}")
    private String algorithmServiceUrl;
    
    private final RestTemplate restTemplate = new RestTemplate();
    
    /**
     * 基于用户的协同过滤推荐
     */
    public Map<String, Object> getUserBasedRecommendations(Integer userId, Integer topN, Double minRating) {
        log.info("调用用户协同过滤推荐: userId={}, topN={}, minRating={}", userId, topN, minRating);
        
        try {
            String url = algorithmServiceUrl + "/api/recommend/user-based";
            
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("user_id", userId);
            requestBody.put("top_n", topN != null ? topN : 10);
            requestBody.put("min_rating", minRating != null ? minRating : 3.0);
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, Object>> requestEntity = new HttpEntity<>(requestBody, headers);
            
            ResponseEntity<Map> response = restTemplate.exchange(
                url, 
                HttpMethod.POST, 
                requestEntity, 
                Map.class
            );
            
            if (response.getStatusCode() == HttpStatus.OK) {
                Map<String, Object> responseBody = response.getBody();
                if (responseBody != null && Boolean.TRUE.equals(responseBody.get("success"))) {
                    log.info("推荐生成成功");
                    return responseBody;
                }
            }
            
            log.error("推荐服务返回失败状态");
            return createErrorResponse("推荐服务返回失败状态");
            
        } catch (Exception e) {
            log.error("调用推荐服务失败", e);
            return createErrorResponse("推荐服务暂时不可用，请稍后重试");
        }
    }
    
    /**
     * 获取相似用户
     */
    public Map<String, Object> getSimilarUsers(Integer userId, Integer topK) {
        log.info("获取相似用户: userId={}, topK={}", userId, topK);
        
        try {
            String url = algorithmServiceUrl + "/api/recommend/similar-users";
            
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("user_id", userId);
            requestBody.put("top_k", topK != null ? topK : 10);
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, Object>> requestEntity = new HttpEntity<>(requestBody, headers);
            
            ResponseEntity<Map> response = restTemplate.exchange(
                url, 
                HttpMethod.POST, 
                requestEntity, 
                Map.class
            );
            
            if (response.getStatusCode() == HttpStatus.OK) {
                return response.getBody();
            }
            
            return createErrorResponse("获取相似用户失败");
            
        } catch (Exception e) {
            log.error("获取相似用户失败", e);
            return createErrorResponse("推荐服务暂时不可用");
        }
    }
    
    /**
     * 检查推荐服务健康状态
     */
    public boolean isAlgorithmServiceHealthy() {
        try {
            String healthUrl = algorithmServiceUrl + "/health";
            ResponseEntity<Map> response = restTemplate.getForEntity(healthUrl, Map.class);
            
            return response.getStatusCode() == HttpStatus.OK;
            
        } catch (Exception e) {
            log.warn("推荐服务健康检查失败: {}", e.getMessage());
            return false;
        }
    }
    
    /**
     * 获取算法信息
     */
    public Map<String, Object> getAlgorithmInfo() {
        try {
            String url = algorithmServiceUrl + "/api/algorithm/info";
            ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);
            
            if (response.getStatusCode() == HttpStatus.OK) {
                return response.getBody();
            }
            
            return createErrorResponse("获取算法信息失败");
            
        } catch (Exception e) {
            log.error("获取算法信息失败", e);
            return createErrorResponse("推荐服务暂时不可用");
        }
    }
    
    /**
     * 创建错误响应
     */
    private Map<String, Object> createErrorResponse(String message) {
        Map<String, Object> errorResponse = new HashMap<>();
        errorResponse.put("success", false);
        errorResponse.put("message", message);
        errorResponse.put("data", null);
        return errorResponse;
    }
}