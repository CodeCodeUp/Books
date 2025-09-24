package com.bookrs.recommendation.controller;

import com.bookrs.recommendation.common.Result;
import com.bookrs.recommendation.service.RecommendationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/recommendations")
@RequiredArgsConstructor
@Tag(name = "推荐系统", description = "个性化图书推荐")
public class RecommendationController {
    
    private final RecommendationService recommendationService;
    
    @PostMapping("/user-based")
    @Operation(summary = "基于用户的协同过滤推荐")
    public Result<Object> getUserBasedRecommendations(
            @RequestParam Integer userId,
            @RequestParam(defaultValue = "10") Integer topN,
            @RequestParam(defaultValue = "3.0") Double minRating) {
        
        Map<String, Object> result = recommendationService.getUserBasedRecommendations(userId, topN, minRating);
        
        if (Boolean.TRUE.equals(result.get("success"))) {
            return Result.success("推荐生成成功", result.get("data"));
        } else {
            return Result.error(result.get("message").toString());
        }
    }
    
    @PostMapping("/item-based")
    @Operation(summary = "基于物品的协同过滤推荐")
    public Result<Object> getItemBasedRecommendations(
            @RequestParam Integer userId,
            @RequestParam(defaultValue = "10") Integer topN,
            @RequestParam(defaultValue = "3.0") Double minRating) {
        
        Map<String, Object> result = recommendationService.getItemBasedRecommendations(userId, topN, minRating);
        
        if (Boolean.TRUE.equals(result.get("success"))) {
            return Result.success("推荐生成成功", result.get("data"));
        } else {
            return Result.error(result.get("message").toString());
        }
    }
    
    @PostMapping("/similar-users")
    @Operation(summary = "获取相似用户")
    public Result<Object> getSimilarUsers(
            @RequestParam Integer userId,
            @RequestParam(defaultValue = "10") Integer topK) {
        
        Map<String, Object> result = recommendationService.getSimilarUsers(userId, topK);
        
        if (Boolean.TRUE.equals(result.get("success"))) {
            return Result.success("获取成功", result.get("data"));
        } else {
            return Result.error(result.get("message").toString());
        }
    }
    
    @GetMapping("/algorithm/info")
    @Operation(summary = "获取算法信息")
    public Result<Object> getAlgorithmInfo() {
        Map<String, Object> result = recommendationService.getAlgorithmInfo();
        
        if (Boolean.TRUE.equals(result.get("success"))) {
            return Result.success("获取成功", result.get("data"));
        } else {
            return Result.error(result.get("message").toString());
        }
    }
    
    @GetMapping("/health")
    @Operation(summary = "检查推荐服务健康状态")
    public Result<Boolean> checkHealth() {
        boolean isHealthy = recommendationService.isAlgorithmServiceHealthy();
        
        if (isHealthy) {
            return Result.success("推荐服务运行正常", true);
        } else {
            return Result.error("推荐服务不可用");
        }
    }
}