package com.bookrs.recommendation.controller;

import com.bookrs.recommendation.common.Result;
import com.bookrs.recommendation.entity.User;
import com.bookrs.recommendation.service.UserService;
import com.bookrs.recommendation.util.JwtTokenUtil;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.constraints.NotBlank;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/users")
@RequiredArgsConstructor
@Tag(name = "用户管理", description = "用户注册、登录和信息管理")
public class UserController {
    
    private final UserService userService;
    private final JwtTokenUtil jwtTokenUtil;
    
    @PostMapping("/register")
    @Operation(summary = "用户注册")
    public Result<User> register(
            @RequestParam @NotBlank String username,
            @RequestParam @NotBlank String password,
            @RequestParam(required = false) String email) {
        
        if (userService.getUserByUsername(username) != null) {
            return Result.error("用户名已存在");
        }
        
        User user = userService.register(username, password, email);
        return Result.success("注册成功", user);
    }
    
    @PostMapping("/login")
    @Operation(summary = "用户登录")
    public Result<Map<String, Object>> login(
            @RequestParam @NotBlank String username,
            @RequestParam @NotBlank String password) {
        
        User user = userService.login(username, password);
        if (user == null) {
            return Result.error("用户名或密码错误");
        }
        
        // 生成JWT Token
        String token = jwtTokenUtil.generateToken(user.getUserId(), user.getUsername());
        
        Map<String, Object> loginResult = new HashMap<>();
        loginResult.put("user", user);
        loginResult.put("token", token);
        
        return Result.success("登录成功", loginResult);
    }
    
    @GetMapping("/{userId}")
    @Operation(summary = "获取用户信息")
    public Result<User> getUserInfo(@PathVariable Integer userId) {
        User user = userService.getUserById(userId);
        if (user == null) {
            return Result.error("用户不存在");
        }
        return Result.success(user);
    }
    
    @PutMapping("/{userId}")
    @Operation(summary = "更新用户信息")
    public Result<String> updateUserInfo(
            @PathVariable Integer userId,
            @RequestParam(required = false) String nickname,
            @RequestParam(required = false) String email) {
        
        userService.updateUserInfo(userId, nickname, email);
        return Result.success("更新成功");
    }
}