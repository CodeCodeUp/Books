package com.bookrs.recommendation.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bookrs.recommendation.entity.Book;
import com.bookrs.recommendation.mapper.BookMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.util.List;

@Service
@RequiredArgsConstructor
public class BookService {
    
    private final BookMapper bookMapper;
    
    public IPage<Book> getBooks(Integer page, Integer size, String keyword) {
        Page<Book> pageParam = new Page<>(page, size);
        
        if (StringUtils.hasText(keyword)) {
            return bookMapper.searchBooks(pageParam, keyword);
        } else {
            LambdaQueryWrapper<Book> wrapper = new LambdaQueryWrapper<Book>()
                    .orderByDesc(Book::getAvgRating)
                    .orderByDesc(Book::getRatingCount);
            return bookMapper.selectPage(pageParam, wrapper);
        }
    }
    
    public Book getBookById(String bookId) {
        return bookMapper.selectById(bookId);
    }
    
    public List<Book> getPopularBooks(Integer limit) {
        LambdaQueryWrapper<Book> wrapper = new LambdaQueryWrapper<Book>()
                .gt(Book::getRatingCount, 10)
                .orderByDesc(Book::getAvgRating)
                .orderByDesc(Book::getRatingCount)
                .last("LIMIT " + limit);
        return bookMapper.selectList(wrapper);
    }
    
    public List<Book> getLatestBooks(Integer limit) {
        LambdaQueryWrapper<Book> wrapper = new LambdaQueryWrapper<Book>()
                .isNotNull(Book::getYear)
                .orderByDesc(Book::getYear)
                .last("LIMIT " + limit);
        return bookMapper.selectList(wrapper);
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
        return bookMapper.selectList(wrapper);
    }
}