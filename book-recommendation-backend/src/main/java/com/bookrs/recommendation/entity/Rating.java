package com.bookrs.recommendation.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@EqualsAndHashCode(callSuper = false)
@TableName("ratings")
public class Rating {
    
    @TableId(type = IdType.AUTO)
    private Long ratingId;
    
    private Integer userId;
    
    private String bookId;
    
    private BigDecimal rating;
    
    private LocalDateTime ratingDate;
    
    private LocalDateTime createdAt;
}