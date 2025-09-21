package com.bookrs.recommendation.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bookrs.recommendation.entity.Book;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Update;

@Mapper
public interface BookMapper extends BaseMapper<Book> {
    
    IPage<Book> searchBooks(Page<Book> page, @Param("keyword") String keyword);
    
    @Update("""
        UPDATE books 
        SET avg_rating = (SELECT ROUND(AVG(rating), 2) FROM ratings WHERE book_id = #{bookId}),
            rating_count = (SELECT COUNT(*) FROM ratings WHERE book_id = #{bookId})
        WHERE book_id = #{bookId}
        """)
    void updateBookRatingStats(@Param("bookId") String bookId);
}