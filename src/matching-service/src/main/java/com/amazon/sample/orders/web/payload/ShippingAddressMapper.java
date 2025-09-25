package com.resqconnect.matching.web.payload;

import com.resqconnect.matching.entities.ShippingAddressEntity;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface ShippingAddressMapper {
  ShippingAddress toShippingAddress(ShippingAddressEntity entity);

  ShippingAddressEntity toShippingAddressEntity(ShippingAddress item);
}
