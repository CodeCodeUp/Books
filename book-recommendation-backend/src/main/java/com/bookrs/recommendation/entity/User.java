package com.bookrs.recommendation.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;

@Data
@EqualsAndHashCode(callSuper = false)
@TableName("users")
public class User {
    
    @TableId(type = IdType.AUTO)  // 恢复自增主键
    private Integer userId;
    
    private String username;
    
    private String password;
    
    private String email;
    
    private String nickname;
    
    private String location;
    
    private Integer age;
    
    private String ageGroup;
    
    private String country;
    
    private String avatarUrl;
    
    private Integer status;
    
    private LocalDateTime createdAt;
    
    private LocalDateTime updatedAt;
    
    private LocalDateTime lastLoginAt;
}