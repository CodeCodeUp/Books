package com.bookrs.recommendation.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.bookrs.recommendation.entity.User;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface UserMapper extends BaseMapper<User> {
}