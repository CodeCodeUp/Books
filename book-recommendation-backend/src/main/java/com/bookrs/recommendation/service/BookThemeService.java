package com.bookrs.recommendation.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.bookrs.recommendation.entity.BookTheme;
import com.bookrs.recommendation.mapper.BookThemeMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class BookThemeService {

    @Autowired
    private BookThemeMapper bookThemeMapper;

    /**
     * 获取所有主题
     */
    public List<BookTheme> getAllThemes() {
        QueryWrapper<BookTheme> queryWrapper = new QueryWrapper<>();
        queryWrapper.orderByAsc("theme_id");
        return bookThemeMapper.selectList(queryWrapper);
    }

    /**
     * 根据ID获取主题
     */
    public BookTheme getThemeById(Integer themeId) {
        return bookThemeMapper.selectById(themeId);
    }

    /**
     * 根据英文名称获取主题
     */
    public BookTheme getThemeByNameEn(String themeNameEn) {
        QueryWrapper<BookTheme> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("theme_name_en", themeNameEn);
        return bookThemeMapper.selectOne(queryWrapper);
    }

    /**
     * 根据中文名称获取主题
     */
    public BookTheme getThemeByNameZh(String themeNameZh) {
        QueryWrapper<BookTheme> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("theme_name_zh", themeNameZh);
        return bookThemeMapper.selectOne(queryWrapper);
    }
}
