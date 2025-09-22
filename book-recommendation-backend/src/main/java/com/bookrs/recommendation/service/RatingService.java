package com.bookrs.recommendation.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.bookrs.recommendation.entity.Rating;
import com.bookrs.recommendation.mapper.BookMapper;
import com.bookrs.recommendation.mapper.RatingMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class RatingService {
    
    private final RatingMapper ratingMapper;
    private final BookMapper bookMapper;
    private final RestTemplate restTemplate;
    
    @Value("${recommendation.service.url:http://localhost:5000}")
    private String algorithmServiceUrl;
    
    /**
     * 用户对图书评分
     */
    @Transactional
    public void rateBook(Integer userId, String bookId, BigDecimal rating) {
        // 检查用户是否已经评分过
        LambdaQueryWrapper<Rating> wrapper = new LambdaQueryWrapper<Rating>()
                .eq(Rating::getUserId, userId)
                .eq(Rating::getBookId, bookId);
        
        Rating existingRating = ratingMapper.selectOne(wrapper);
        
        if (existingRating != null) {
            // 更新现有评分
            existingRating.setRating(rating);
            existingRating.setRatingDate(LocalDateTime.now());
            ratingMapper.updateById(existingRating);
        } else {
            // 创建新评分
            Rating newRating = new Rating();
            newRating.setUserId(userId);
            newRating.setBookId(bookId);
            newRating.setRating(rating);
            newRating.setRatingDate(LocalDateTime.now());
            newRating.setCreatedAt(LocalDateTime.now());
            ratingMapper.insert(newRating);
        }
        
        // 更新图书统计信息
        bookMapper.updateBookRatingStats(bookId);
        
        // 异步触发推荐预计算
        triggerRecommendationPrecompute(userId);
    }
    
    /**
     * 触发推荐预计算
     */
    private void triggerRecommendationPrecompute(Integer userId) {
        try {
            // 先清除缓存
            String clearUrl = algorithmServiceUrl + "/api/cache/clear";
            Map<String, Object> clearRequest = new HashMap<>();
            clearRequest.put("user_id", userId);
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> clearEntity = new HttpEntity<>(clearRequest, headers);
            
            restTemplate.postForObject(clearUrl, clearEntity, Map.class);
            
            // 启动预计算
            String precomputeUrl = algorithmServiceUrl + "/api/cache/precompute";
            HttpEntity<Map<String, Object>> precomputeEntity = new HttpEntity<>(clearRequest, headers);
            
            restTemplate.postForObject(precomputeUrl, precomputeEntity, Map.class);
            
            log.info("已触发用户{}的推荐预计算", userId);
            
        } catch (Exception e) {
            log.warn("触发推荐预计算失败（算法服务可能未启动）: {}", e.getMessage());
        }
    }
    
    /**
     * 获取用户对特定图书的评分
     */
    public Rating getUserBookRating(Integer userId, String bookId) {
        LambdaQueryWrapper<Rating> wrapper = new LambdaQueryWrapper<Rating>()
                .eq(Rating::getUserId, userId)
                .eq(Rating::getBookId, bookId);
        return ratingMapper.selectOne(wrapper);
    }
    
    /**
     * 获取用户的所有评分
     */
    public List<Rating> getUserRatings(Integer userId) {
        LambdaQueryWrapper<Rating> wrapper = new LambdaQueryWrapper<Rating>()
                .eq(Rating::getUserId, userId)
                .orderByDesc(Rating::getRatingDate);
        return ratingMapper.selectList(wrapper);
    }
    
    /**
     * 获取图书的所有评分
     */
    public List<Rating> getBookRatings(String bookId) {
        LambdaQueryWrapper<Rating> wrapper = new LambdaQueryWrapper<Rating>()
                .eq(Rating::getBookId, bookId)
                .orderByDesc(Rating::getRatingDate);
        return ratingMapper.selectList(wrapper);
    }
}