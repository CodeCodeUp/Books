package com.bookrs.recommendation.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bookrs.recommendation.entity.Book;
import com.bookrs.recommendation.entity.BookTheme;
import com.bookrs.recommendation.mapper.BookMapper;
import com.bookrs.recommendation.mapper.BookThemeMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class BookService {

    private final BookMapper bookMapper;
    private final BookThemeMapper bookThemeMapper;

    // 主题名称缓存，避免重复查询数据库
    private final Map<Integer, String> themeNameCache = new HashMap<>();

    public IPage<Book> getBooks(Integer page, Integer size, String keyword) {
        Page<Book> pageParam = new Page<>(page, size);

        IPage<Book> result;
        if (StringUtils.hasText(keyword)) {
            result = bookMapper.searchBooks(pageParam, keyword);
        } else {
            LambdaQueryWrapper<Book> wrapper = new LambdaQueryWrapper<Book>()
                    .orderByDesc(Book::getAvgRating)
                    .orderByDesc(Book::getRatingCount);
            result = bookMapper.selectPage(pageParam, wrapper);
        }

        // 填充主题名称
        fillThemeNames(result.getRecords());
        return result;
    }

    public Book getBookById(String bookId) {
        Book book = bookMapper.selectById(bookId);
        if (book != null) {
            fillThemeName(book);
        }
        return book;
    }

    public List<Book> getPopularBooks(Integer limit) {
        LambdaQueryWrapper<Book> wrapper = new LambdaQueryWrapper<Book>()
                .gt(Book::getRatingCount, 10)
                .orderByDesc(Book::getAvgRating)
                .orderByDesc(Book::getRatingCount)
                .last("LIMIT " + limit);
        List<Book> books = bookMapper.selectList(wrapper);
        fillThemeNames(books);
        return books;
    }

    public List<Book> getLatestBooks(Integer limit) {
        LambdaQueryWrapper<Book> wrapper = new LambdaQueryWrapper<Book>()
                .isNotNull(Book::getYear)
                .orderByDesc(Book::getYear)
                .last("LIMIT " + limit);
        List<Book> books = bookMapper.selectList(wrapper);
        fillThemeNames(books);
        return books;
    }

    public List<Book> getBooksByAuthor(String bookId, Integer limit) {
        // 先获取目标图书信息
        Book targetBook = bookMapper.selectById(bookId);
        if (targetBook == null || targetBook.getAuthor() == null) {
            return getPopularBooks(limit); // 降级到热门图书
        }

        LambdaQueryWrapper<Book> wrapper = new LambdaQueryWrapper<Book>()
                .eq(Book::getAuthor, targetBook.getAuthor())
                .ne(Book::getBookId, bookId) // 排除当前图书
                .orderByDesc(Book::getAvgRating)
                .orderByDesc(Book::getRatingCount)
                .last("LIMIT " + limit);
        List<Book> books = bookMapper.selectList(wrapper);
        fillThemeNames(books);
        return books;
    }

    /**
     * 填充单个图书的主题名称
     */
    private void fillThemeName(Book book) {
        if (book == null || book.getThemeId() == null) {
            return;
        }

        String themeName = getThemeNameFromCache(book.getThemeId());
        book.setThemeName(themeName);
    }

    /**
     * 批量填充图书的主题名称
     */
    private void fillThemeNames(List<Book> books) {
        if (books == null || books.isEmpty()) {
            return;
        }

        for (Book book : books) {
            fillThemeName(book);
        }
    }

    /**
     * 从缓存获取主题名称，缓存未命中则查询数据库
     */
    private String getThemeNameFromCache(Integer themeId) {
        if (themeId == null) {
            return null;
        }

        // 先从缓存获取
        if (themeNameCache.containsKey(themeId)) {
            return themeNameCache.get(themeId);
        }

        // 缓存未命中，查询数据库
        BookTheme theme = bookThemeMapper.selectById(themeId);
        String themeName = theme != null ? theme.getThemeNameZh() : null;

        // 加入缓存
        if (themeName != null) {
            themeNameCache.put(themeId, themeName);
        }

        return themeName;
    }
}
