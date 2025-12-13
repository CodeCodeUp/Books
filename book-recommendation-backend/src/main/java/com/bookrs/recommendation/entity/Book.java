package com.bookrs.recommendation.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@EqualsAndHashCode(callSuper = false)
@TableName("books")
public class Book {

    @TableId
    private String bookId;

    private String title;

    private String author;

    private String publisher;

    private Integer year;

    private String imageUrlS;

    private String imageUrlM;

    private String imageUrlL;

    private BigDecimal avgRating;

    private Integer ratingCount;

    private Integer themeId;

    /**
     * 主题名称（中文）- 非数据库字段，用于前端显示
     */
    @TableField(exist = false)
    private String themeName;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;
}
