package com.bookrs.recommendation.controller;

import com.bookrs.recommendation.common.Result;
import com.bookrs.recommendation.entity.BookTheme;
import com.bookrs.recommendation.service.BookThemeService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/themes")
@RequiredArgsConstructor
@Tag(name = "图书主题管理", description = "图书主题接口")
public class CategoryController {

    private final BookThemeService bookThemeService;

    @GetMapping
    @Operation(summary = "获取所有图书主题")
    public Result<List<BookTheme>> getAllThemes() {
        List<BookTheme> themes = bookThemeService.getAllThemes();
        return Result.success(themes);
    }

    @GetMapping("/{themeId}")
    @Operation(summary = "根据ID获取主题信息")
    public Result<BookTheme> getThemeById(@PathVariable Integer themeId) {
        BookTheme theme = bookThemeService.getThemeById(themeId);
        if (theme == null) {
            return Result.error("主题不存在");
        }
        return Result.success(theme);
    }
}
