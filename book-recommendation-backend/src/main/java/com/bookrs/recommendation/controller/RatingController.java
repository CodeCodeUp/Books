package com.bookrs.recommendation.controller;

import com.bookrs.recommendation.common.Result;
import com.bookrs.recommendation.entity.Rating;
import com.bookrs.recommendation.service.RatingService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.List;

@RestController
@RequestMapping("/ratings")
@RequiredArgsConstructor
@Tag(name = "评分管理", description = "图书评分功能")
public class RatingController {
    
    private final RatingService ratingService;
    
    @PostMapping("/rate")
    @Operation(summary = "用户评分")
    public Result<String> rateBook(
            @RequestParam Integer userId,
            @RequestParam String bookId,
            @RequestParam BigDecimal rating) {
        
        // 验证评分范围
        if (rating.compareTo(BigDecimal.ZERO) < 0 || rating.compareTo(new BigDecimal("5")) > 0) {
            return Result.error("评分必须在0-5分之间");
        }
        
        // 验证评分精度(只允许0.5的倍数)
        BigDecimal remainder = rating.remainder(new BigDecimal("0.5"));
        if (remainder.compareTo(BigDecimal.ZERO) != 0) {
            return Result.error("评分只支持0.5分间隔");
        }
        
        ratingService.rateBook(userId, bookId, rating);
        return Result.success("评分成功");
    }
    
    @GetMapping("/user/{userId}/book/{bookId}")
    @Operation(summary = "获取用户对图书的评分")
    public Result<Rating> getUserBookRating(
            @PathVariable Integer userId,
            @PathVariable String bookId) {
        
        Rating rating = ratingService.getUserBookRating(userId, bookId);
        return Result.success(rating);
    }
    
    @GetMapping("/user/{userId}")
    @Operation(summary = "获取用户的所有评分")
    public Result<List<Rating>> getUserRatings(@PathVariable Integer userId) {
        List<Rating> ratings = ratingService.getUserRatings(userId);
        return Result.success(ratings);
    }
    
    @GetMapping("/book/{bookId}")
    @Operation(summary = "获取图书的所有评分")
    public Result<List<Rating>> getBookRatings(@PathVariable String bookId) {
        List<Rating> ratings = ratingService.getBookRatings(bookId);
        return Result.success(ratings);
    }
}