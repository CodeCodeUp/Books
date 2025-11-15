package com.bookrs.recommendation.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.bookrs.recommendation.entity.BookTheme;
import com.bookrs.recommendation.entity.UserInterest;
import com.bookrs.recommendation.mapper.UserInterestMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class UserInterestService {

    private final UserInterestMapper userInterestMapper;
    private final BookThemeService bookThemeService;

    /**
     * 获取用户的兴趣列表
     */
    public List<BookTheme> getUserInterests(Integer userId) {
        LambdaQueryWrapper<UserInterest> wrapper = new LambdaQueryWrapper<UserInterest>()
                .eq(UserInterest::getUserId, userId);

        List<UserInterest> userInterests = userInterestMapper.selectList(wrapper);

        return userInterests.stream()
                .map(ui -> bookThemeService.getThemeById(ui.getThemeId()))
                .filter(theme -> theme != null)
                .collect(Collectors.toList());
    }

    /**
     * 获取用户兴趣的ID列表
     */
    public List<Integer> getUserInterestIds(Integer userId) {
        LambdaQueryWrapper<UserInterest> wrapper = new LambdaQueryWrapper<UserInterest>()
                .eq(UserInterest::getUserId, userId)
                .select(UserInterest::getThemeId);

        return userInterestMapper.selectList(wrapper).stream()
                .map(UserInterest::getThemeId)
                .collect(Collectors.toList());
    }

    /**
     * 保存用户兴趣（覆盖式更新）
     */
    @Transactional
    public void saveUserInterests(Integer userId, List<Integer> themeIds) {
        // 删除用户现有的所有兴趣
        LambdaQueryWrapper<UserInterest> deleteWrapper = new LambdaQueryWrapper<UserInterest>()
                .eq(UserInterest::getUserId, userId);
        userInterestMapper.delete(deleteWrapper);

        // 插入新的兴趣
        if (themeIds != null && !themeIds.isEmpty()) {
            for (Integer themeId : themeIds) {
                UserInterest userInterest = new UserInterest();
                userInterest.setUserId(userId);
                userInterest.setThemeId(themeId);
                userInterest.setCreatedAt(LocalDateTime.now());
                userInterestMapper.insert(userInterest);
            }
        }
    }

    /**
     * 添加单个兴趣
     */
    public void addUserInterest(Integer userId, Integer themeId) {
        // 检查是否已存在
        LambdaQueryWrapper<UserInterest> wrapper = new LambdaQueryWrapper<UserInterest>()
                .eq(UserInterest::getUserId, userId)
                .eq(UserInterest::getThemeId, themeId);

        if (userInterestMapper.selectCount(wrapper) == 0) {
            UserInterest userInterest = new UserInterest();
            userInterest.setUserId(userId);
            userInterest.setThemeId(themeId);
            userInterest.setCreatedAt(LocalDateTime.now());
            userInterestMapper.insert(userInterest);
        }
    }

    /**
     * 删除单个兴趣
     */
    public void removeUserInterest(Integer userId, Integer themeId) {
        LambdaQueryWrapper<UserInterest> wrapper = new LambdaQueryWrapper<UserInterest>()
                .eq(UserInterest::getUserId, userId)
                .eq(UserInterest::getThemeId, themeId);
        userInterestMapper.delete(wrapper);
    }

    /**
     * 检查用户是否设置了兴趣
     */
    public boolean hasUserInterests(Integer userId) {
        LambdaQueryWrapper<UserInterest> wrapper = new LambdaQueryWrapper<UserInterest>()
                .eq(UserInterest::getUserId, userId);
        return userInterestMapper.selectCount(wrapper) > 0;
    }
}
