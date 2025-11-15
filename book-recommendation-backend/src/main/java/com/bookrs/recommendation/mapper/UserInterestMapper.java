package com.bookrs.recommendation.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.bookrs.recommendation.entity.UserInterest;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface UserInterestMapper extends BaseMapper<UserInterest> {
}
