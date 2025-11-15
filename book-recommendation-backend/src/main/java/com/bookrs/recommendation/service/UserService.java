package com.bookrs.recommendation.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.bookrs.recommendation.entity.User;
import com.bookrs.recommendation.mapper.UserMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class UserService {
    
    private final UserMapper userMapper;
    private final PasswordEncoder passwordEncoder;
    
    public User getUserById(Integer userId) {
        return userMapper.selectById(userId);
    }
    
    public User getUserByUsername(String username) {
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<User>()
                .eq(User::getUsername, username);
        return userMapper.selectOne(wrapper);
    }
    
    public User register(String username, String password, String email) {
        User user = new User();
        user.setUsername(username);
        user.setPassword(passwordEncoder.encode(password));
        user.setEmail(email);
        user.setStatus(1);
        user.setCreatedAt(LocalDateTime.now());
        
        userMapper.insert(user);
        return user;
    }
    
    public User login(String username, String password) {
        User user = getUserByUsername(username);
        if (user != null && passwordEncoder.matches(password, user.getPassword())) {
            user.setLastLoginAt(LocalDateTime.now());
            userMapper.updateById(user);
            return user;
        }
        return null;
    }
    
    public void updateUserInfo(Integer userId, String nickname, Integer age) {
        User user = new User();
        user.setUserId(userId);
        user.setNickname(nickname);
        user.setAge(age);

        // 根据年龄自动设置年龄组
        if (age != null) {
            String ageGroup = getAgeGroup(age);
            user.setAgeGroup(ageGroup);
        }

        user.setUpdatedAt(LocalDateTime.now());
        userMapper.updateById(user);
    }

    private String getAgeGroup(Integer age) {
        if (age == null || age <= 0) return "Unknown";

        if (age < 18) return "Under 18";
        else if (age < 25) return "18-24";
        else if (age < 35) return "25-34";
        else if (age < 45) return "35-44";
        else if (age < 55) return "45-54";
        else return "55+";
    }
}