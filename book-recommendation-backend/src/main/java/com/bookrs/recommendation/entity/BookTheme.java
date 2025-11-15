package com.bookrs.recommendation.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;

@Data
@EqualsAndHashCode(callSuper = false)
@TableName("book_theme")
public class BookTheme {

    @TableId(type = IdType.AUTO)
    private Integer themeId;

    private String themeNameEn;

    private String themeNameZh;

    private String description;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;
}
