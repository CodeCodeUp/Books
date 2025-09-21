package com.bookrs.recommendation.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.bookrs.recommendation.entity.Rating;
import com.bookrs.recommendation.mapper.BookMapper;
import com.bookrs.recommendation.mapper.RatingMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class RatingService {
    
    private final RatingMapper ratingMapper;
    private final BookMapper bookMapper;
    
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