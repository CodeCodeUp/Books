package com.bookrs.recommendation.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.bookrs.recommendation.entity.User;
import com.bookrs.recommendation.mapper.UserMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

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
    
    public void updateUserInfo(Integer userId, String nickname, String email, String location, Integer age, String country) {
        User user = new User();
        user.setUserId(userId);
        user.setNickname(nickname);
        user.setEmail(email);
        user.setLocation(location);
        user.setAge(age);
        user.setCountry(country);
        user.setUpdatedAt(LocalDateTime.now());
        userMapper.updateById(user);
    }
}