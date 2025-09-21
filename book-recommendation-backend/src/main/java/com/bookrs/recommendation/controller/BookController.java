package com.bookrs.recommendation.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.bookrs.recommendation.common.PageResult;
import com.bookrs.recommendation.common.Result;
import com.bookrs.recommendation.entity.Book;
import com.bookrs.recommendation.service.BookService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/books")
@RequiredArgsConstructor
@Tag(name = "图书管理", description = "图书信息查询和管理")
public class BookController {
    
    private final BookService bookService;
    
    @GetMapping
    @Operation(summary = "分页查询图书")
    public Result<PageResult<Book>> getBooks(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "20") Integer size,
            @RequestParam(required = false) String keyword) {
        
        IPage<Book> pageResult = bookService.getBooks(page, size, keyword);
        PageResult<Book> result = PageResult.of(
            pageResult.getRecords(),
            pageResult.getTotal(),
            pageResult.getCurrent(),
            pageResult.getSize()
        );
        return Result.success(result);
    }
    
    @GetMapping("/{bookId}")
    @Operation(summary = "获取图书详情")
    public Result<Book> getBookDetail(@PathVariable String bookId) {
        Book book = bookService.getBookById(bookId);
        if (book == null) {
            return Result.error("图书不存在");
        }
        return Result.success(book);
    }
    
    @GetMapping("/popular")
    @Operation(summary = "获取热门图书")
    public Result<List<Book>> getPopularBooks(@RequestParam(defaultValue = "10") Integer limit) {
        List<Book> books = bookService.getPopularBooks(limit);
        return Result.success(books);
    }
    
    @GetMapping("/latest")
    @Operation(summary = "获取最新图书")
    public Result<List<Book>> getLatestBooks(@RequestParam(defaultValue = "10") Integer limit) {
        List<Book> books = bookService.getLatestBooks(limit);
        return Result.success(books);
    }
}