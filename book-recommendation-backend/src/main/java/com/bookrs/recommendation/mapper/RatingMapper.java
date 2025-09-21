package com.bookrs.recommendation.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.bookrs.recommendation.entity.Rating;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface RatingMapper extends BaseMapper<Rating> {
}