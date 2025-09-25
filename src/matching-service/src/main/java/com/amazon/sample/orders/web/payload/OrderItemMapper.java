package com.resqconnect.matching.web.payload;

import com.resqconnect.matching.entities.OrderItemEntity;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface OrderItemMapper {
  OrderItem toOrderItem(OrderItemEntity entity);

  OrderItemEntity toOrderItemEntity(OrderItem item);
}
