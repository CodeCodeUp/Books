package com.bookrs.recommendation;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.bookrs.recommendation.mapper")
public class BookRecommendationApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(BookRecommendationApplication.class, args);
    }
}